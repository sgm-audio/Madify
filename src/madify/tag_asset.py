"""Apply title, description, and tags to a catalogued asset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from madify.errors import AssetNotFoundError
from madify.tagging import build_metadata

if TYPE_CHECKING:
    from madify.models import MediaAsset, TagRequest
    from madify.ports import CatalogStore, Clock


def tag_asset(
    *,
    catalog: CatalogStore,
    clock: Clock,
    request: TagRequest,
    asset_id: int | None = None,
    path: str | None = None,
) -> MediaAsset:
    asset = _resolve_asset(catalog, asset_id=asset_id, path=path)
    metadata = build_metadata(
        title=request.title,
        description=request.description,
        tags=request.tags,
        base=asset.metadata,
    )
    return catalog.update_metadata(asset.id, metadata, now=clock.now())


def _resolve_asset(
    catalog: CatalogStore,
    *,
    asset_id: int | None,
    path: str | None,
) -> MediaAsset:
    if asset_id is None and path is None:
        message = "provide asset id or path"
        raise AssetNotFoundError(message)
    if asset_id is not None and path is not None:
        message = "provide asset id or path, not both"
        raise AssetNotFoundError(message)

    asset = (
        catalog.get_by_id(asset_id)
        if asset_id is not None
        else catalog.get_by_path(path or "")
    )
    if asset is None:
        target = f"id={asset_id}" if asset_id is not None else f"path={path}"
        message = f"asset not found: {target}"
        raise AssetNotFoundError(message)
    return asset
