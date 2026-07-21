"""CLI for scan, tag, rename, list, and search against a SQLite catalog.

Wires production adapters into the core use cases and prints human-readable
summaries. Expected domain errors become exit code 1.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from madify.errors import MadifyError
from madify.local_fs import LocalFileSystem
from madify.models import MediaAsset, TagRequest
from madify.query import list_catalog, search_catalog
from madify.rename_assets import rename_assets
from madify.scan import scan_directory
from madify.sqlite_catalog import SqliteCatalog
from madify.system_clock import SystemClock
from madify.tag_asset import tag_asset
from madify.xmp_sidecar import XmpSidecarWriter


def run_cli(argv: list[str]) -> int:
    """Parse ``argv`` and run the selected subcommand.

    Args:
        argv: Argument list without the program name (as for
            ``argparse.ArgumentParser.parse_args``).

    Returns:
        Process exit code (0 on success, 1 on :class:`~madify.errors.MadifyError`).
    """
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
    """Route a parsed namespace to the matching command handler."""
    if args.command == "scan":
        return _cmd_scan(args, fs=fs, catalog=catalog, clock=clock)
    if args.command == "tag":
        return _cmd_tag(args, catalog=catalog, clock=clock)
    if args.command == "rename":
        return _cmd_rename(args, fs=fs, catalog=catalog, clock=clock)
    if args.command == "list":
        return _cmd_list(catalog=catalog)
    if args.command == "search":
        return _cmd_search(args, catalog=catalog)
    message = f"unknown command: {args.command}"
    raise MadifyError(message)


def _build_parser() -> argparse.ArgumentParser:
    """Build the top-level ``madify`` argument parser."""
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
        help="Tag to merge (repeatable); use --replace-tags to replace all",
    )
    tag_p.add_argument(
        "--replace-tags",
        action="store_true",
        help="Replace the full tag set instead of merging",
    )
    tag_p.add_argument(
        "--no-sidecar",
        action="store_true",
        help="Skip writing an XMP sidecar next to the media file",
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

    sub.add_parser("list", help="List all catalogued assets")

    search_p = sub.add_parser("search", help="Search assets by query and/or tag")
    search_p.add_argument(
        "--query",
        "-q",
        default=None,
        help="Case-insensitive substring (title, description, path, tags)",
    )
    search_p.add_argument(
        "--tag",
        default=None,
        help="Require this tag (case-insensitive exact match)",
    )
    return parser


def _cmd_scan(
    args: argparse.Namespace,
    *,
    fs: LocalFileSystem,
    catalog: SqliteCatalog,
    clock: SystemClock,
) -> int:
    """Run ``scan`` and print a summary."""
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
    """Run ``tag``, write XMP sidecar (unless disabled), print metadata."""
    path = None if args.path is None else str(Path(args.path).resolve())
    writer = None if args.no_sidecar else XmpSidecarWriter()
    asset = tag_asset(
        catalog=catalog,
        clock=clock,
        asset_id=args.asset_id,
        path=path,
        metadata_writer=writer,
        request=TagRequest(
            title=args.title,
            description=args.description,
            tags=args.tags,
            replace_tags=args.replace_tags,
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
    """Run ``rename`` and print renamed paths."""
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


def _cmd_list(*, catalog: SqliteCatalog) -> int:
    """Print every catalogued asset."""
    assets = list_catalog(catalog)
    print(f"assets: {len(assets)}")
    for asset in assets:
        _print_asset_line(asset)
    return 0


def _cmd_search(args: argparse.Namespace, *, catalog: SqliteCatalog) -> int:
    """Print assets matching query/tag filters."""
    try:
        assets = search_catalog(catalog, query=args.query, tag=args.tag)
    except ValueError as exc:
        raise MadifyError(str(exc)) from exc
    print(f"matches: {len(assets)}")
    for asset in assets:
        _print_asset_line(asset)
    return 0


def _print_asset_line(asset: MediaAsset) -> None:
    """Format one asset summary line for list/search output."""
    tags = ",".join(asset.metadata.tags) if asset.metadata.tags else ""
    title = asset.metadata.title or "(untitled)"
    print(f"  id={asset.id} [{asset.kind.value}] {title!r} tags=[{tags}] {asset.path}")
