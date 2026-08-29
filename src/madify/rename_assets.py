"""Rename catalogued files from their titles via injected filesystem.

Bulk rename skips untitled assets. Renaming a single ``asset_id`` without a
title raises :class:`~madify.errors.RenameError`. Destination collisions with
neighbors or other catalogued paths get ``_2``, ``_3``, … suffixes.

Sibling ``.xmp`` sidecars move with the media when present; an existing target
sidecar is left alone (never clobbered).
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import PurePath
from typing import TYPE_CHECKING

from madify.errors import AssetNotFoundError, RenameError
from madify.models import MediaAsset, RenameResult
from madify.naming import allocate_unique_path, proposed_path
from madify.xmp_sidecar import sidecar_path_for

if TYPE_CHECKING:
    from madify.ports import CatalogStore, Clock, FileSystem


def rename_assets(
    *,
    catalog: CatalogStore,
    fs: FileSystem,
    clock: Clock,
    asset_id: int | None = None,
    dry_run: bool = False,
) -> RenameResult:
    """Rename one asset or every titled asset in the catalog.

    ``dry_run=True`` computes the full rename plan (including collision
    suffixes) without touching the filesystem or catalog. ``renamed`` then
    holds assets carrying their *proposed* destination paths.

    Args:
        catalog: Catalog store port.
        fs: Filesystem port used for existence checks and renames.
        clock: Clock port for ``updated_at`` after a successful move.
        asset_id: When set, only that asset is considered; when ``None``,
            all catalogued assets are considered.
        dry_run: When True, plan renames but perform no filesystem or catalog
            writes.

    Returns:
        Renamed and unchanged asset collections.

    Raises:
        AssetNotFoundError: ``asset_id`` was given but does not exist.
        RenameError: Targeted asset has no title, destination exists, or
            the filesystem rename fails.
    """
    assets = _assets_to_rename(catalog, asset_id=asset_id)
    taken = _build_taken_paths(assets, catalog=catalog, fs=fs)
    renamed: list[MediaAsset] = []
    unchanged: list[MediaAsset] = []

    for asset in assets:
        if asset_id is not None and not asset.metadata.title.strip():
            message = f"asset id={asset.id} has no title; tag it before rename"
            raise RenameError(message)
        outcome = _rename_one(
            asset,
            catalog=catalog,
            fs=fs,
            clock=clock,
            taken=taken,
            dry_run=dry_run,
        )
        if outcome is None:
            unchanged.append(asset)
        else:
            renamed.append(outcome)

    return RenameResult(renamed=tuple(renamed), unchanged=tuple(unchanged))


def _assets_to_rename(
    catalog: CatalogStore,
    *,
    asset_id: int | None,
) -> list[MediaAsset]:
    """Return the asset list for a rename pass."""
    if asset_id is None:
        return catalog.list_assets()
    asset = catalog.get_by_id(asset_id)
    if asset is None:
        message = f"asset not found: id={asset_id}"
        raise AssetNotFoundError(message)
    return [asset]


def _build_taken_paths(
    assets: list[MediaAsset],
    *,
    catalog: CatalogStore,
    fs: FileSystem,
) -> set[str]:
    """Casefolded set of catalog paths plus on-disk neighbor files."""
    taken = {a.path.casefold() for a in catalog.list_assets()}
    for path in _existing_neighbor_paths(assets, fs):
        taken.add(path.casefold())
    return taken


def _rename_one(  # noqa: PLR0913
    asset: MediaAsset,
    *,
    catalog: CatalogStore,
    fs: FileSystem,
    clock: Clock,
    taken: set[str],
    dry_run: bool,
) -> MediaAsset | None:
    """Rename a single titled asset; return ``None`` when unchanged."""
    if not asset.metadata.title.strip():
        return None

    desired = proposed_path(asset)
    if PurePath(desired).name == PurePath(asset.path).name:
        return None

    taken.discard(asset.path.casefold())
    destination = allocate_unique_path(desired, taken)
    if destination.casefold() == asset.path.casefold():
        taken.add(asset.path.casefold())
        return None

    if dry_run:
        taken.add(destination.casefold())
        return replace(asset, path=destination)

    if fs.exists(destination):
        message = f"destination already exists: {destination}"
        raise RenameError(message)

    try:
        fs.rename(asset.path, destination)
    except OSError as exc:
        taken.add(asset.path.casefold())
        message = f"failed to rename {asset.path} -> {destination}: {exc}"
        raise RenameError(message) from exc

    updated = catalog.update_path(asset.id, destination, now=clock.now())
    taken.add(destination.casefold())
    _rename_sidecar_if_present(fs, asset.path, destination, taken=taken)
    return updated


def _rename_sidecar_if_present(
    fs: FileSystem,
    source_media: str,
    destination_media: str,
    *,
    taken: set[str],
) -> None:
    """Rename sibling ``.xmp`` with the media when safe; no-op otherwise."""
    old_sidecar = sidecar_path_for(source_media)
    new_sidecar = sidecar_path_for(destination_media)
    if not fs.exists(old_sidecar):
        return
    if old_sidecar.casefold() == new_sidecar.casefold():
        return
    if fs.exists(new_sidecar):
        # Don't clobber an existing target sidecar.
        return

    try:
        fs.rename(old_sidecar, new_sidecar)
    except OSError as exc:
        message = f"failed to rename sidecar {old_sidecar} -> {new_sidecar}: {exc}"
        raise RenameError(message) from exc

    taken.discard(old_sidecar.casefold())
    taken.add(new_sidecar.casefold())


def _existing_neighbor_paths(assets: list[MediaAsset], fs: FileSystem) -> list[str]:
    """List files in each unique parent directory of ``assets``."""
    parents: set[str] = set()
    for asset in assets:
        parent = str(PurePath(asset.path).parent)
        parents.add(parent)
    found: list[str] = []
    for parent in sorted(parents):
        if fs.is_directory(parent):
            found.extend(fs.iter_files(parent))
    return found
