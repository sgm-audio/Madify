"""Rename catalogued files from their titles via injected filesystem."""

from __future__ import annotations

from pathlib import PurePath
from typing import TYPE_CHECKING

from madify.errors import AssetNotFoundError, RenameError
from madify.models import MediaAsset, RenameResult
from madify.naming import allocate_unique_path, proposed_path

if TYPE_CHECKING:
    from madify.ports import CatalogStore, Clock, FileSystem


def rename_assets(
    *,
    catalog: CatalogStore,
    fs: FileSystem,
    clock: Clock,
    asset_id: int | None = None,
) -> RenameResult:
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
    taken = {a.path.casefold() for a in catalog.list_assets()}
    for path in _existing_neighbor_paths(assets, fs):
        taken.add(path.casefold())
    return taken


def _rename_one(
    asset: MediaAsset,
    *,
    catalog: CatalogStore,
    fs: FileSystem,
    clock: Clock,
    taken: set[str],
) -> MediaAsset | None:
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
    return updated


def _existing_neighbor_paths(assets: list[MediaAsset], fs: FileSystem) -> list[str]:
    parents: set[str] = set()
    for asset in assets:
        parent = str(PurePath(asset.path).parent)
        parents.add(parent)
    found: list[str] = []
    for parent in sorted(parents):
        if fs.is_directory(parent):
            found.extend(fs.iter_files(parent))
    return found
