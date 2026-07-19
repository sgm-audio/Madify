"""CLI for scan, tag, and rename against a SQLite catalog."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from madify.errors import MadifyError
from madify.local_fs import LocalFileSystem
from madify.models import TagRequest
from madify.rename_assets import rename_assets
from madify.scan import scan_directory
from madify.sqlite_catalog import SqliteCatalog
from madify.system_clock import SystemClock
from madify.tag_asset import tag_asset


def run_cli(argv: list[str]) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    db_path = str(Path(args.db).resolve())
    fs = LocalFileSystem()
    clock = SystemClock()
    catalog: SqliteCatalog | None = None
    try:
        catalog = SqliteCatalog(db_path)
        code = _dispatch(args, fs=fs, catalog=catalog, clock=clock)
    except MadifyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    else:
        return code
    finally:
        if catalog is not None:
            catalog.close()


def _dispatch(
    args: argparse.Namespace,
    *,
    fs: LocalFileSystem,
    catalog: SqliteCatalog,
    clock: SystemClock,
) -> int:
    if args.command == "scan":
        return _cmd_scan(args, fs=fs, catalog=catalog, clock=clock)
    if args.command == "tag":
        return _cmd_tag(args, catalog=catalog, clock=clock)
    if args.command == "rename":
        return _cmd_rename(args, fs=fs, catalog=catalog, clock=clock)
    message = f"unknown command: {args.command}"
    raise MadifyError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="madify",
        description="Photo cataloguer and metadata assistant.",
    )
    parser.add_argument(
        "--db",
        default="madify.sqlite",
        help="SQLite catalog path (default: madify.sqlite)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan_p = sub.add_parser("scan", help="Scan a directory into the catalog")
    scan_p.add_argument("root", help="Directory to scan recursively")

    tag_p = sub.add_parser("tag", help="Set title, description, and/or tags")
    target = tag_p.add_mutually_exclusive_group(required=True)
    target.add_argument("--id", type=int, dest="asset_id", help="Catalog asset id")
    target.add_argument("--path", help="Absolute or relative asset path")
    tag_p.add_argument("--title", default=None, help="Asset title")
    tag_p.add_argument("--description", default=None, help="Asset description")
    tag_p.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=None,
        help="Tag (repeatable)",
    )

    rename_p = sub.add_parser(
        "rename",
        help="Rename files from their catalog titles",
    )
    rename_p.add_argument(
        "--id",
        type=int,
        dest="asset_id",
        default=None,
        help="Rename one asset id (default: all with titles)",
    )
    return parser


def _cmd_scan(
    args: argparse.Namespace,
    *,
    fs: LocalFileSystem,
    catalog: SqliteCatalog,
    clock: SystemClock,
) -> int:
    root = str(Path(args.root).resolve())
    result = scan_directory(root, fs=fs, catalog=catalog, clock=clock)
    print(
        f"scan complete: added={len(result.added)} "
        f"updated={len(result.updated)} skipped={len(result.skipped)}"
    )
    for asset in result.added:
        print(f"  + id={asset.id} [{asset.kind.value}] {asset.path}")
    for asset in result.updated:
        print(f"  ~ id={asset.id} [{asset.kind.value}] {asset.path}")
    return 0


def _cmd_tag(
    args: argparse.Namespace,
    *,
    catalog: SqliteCatalog,
    clock: SystemClock,
) -> int:
    path = None if args.path is None else str(Path(args.path).resolve())
    asset = tag_asset(
        catalog=catalog,
        clock=clock,
        asset_id=args.asset_id,
        path=path,
        request=TagRequest(
            title=args.title,
            description=args.description,
            tags=args.tags,
        ),
    )
    tags = ",".join(asset.metadata.tags) if asset.metadata.tags else ""
    print(
        f"tagged id={asset.id} title={asset.metadata.title!r} "
        f"description={asset.metadata.description!r} tags=[{tags}]"
    )
    return 0


def _cmd_rename(
    args: argparse.Namespace,
    *,
    fs: LocalFileSystem,
    catalog: SqliteCatalog,
    clock: SystemClock,
) -> int:
    result = rename_assets(
        catalog=catalog,
        fs=fs,
        clock=clock,
        asset_id=args.asset_id,
    )
    print(
        f"rename complete: renamed={len(result.renamed)} "
        f"unchanged={len(result.unchanged)}"
    )
    for asset in result.renamed:
        print(f"  -> id={asset.id} {asset.path}")
    return 0
