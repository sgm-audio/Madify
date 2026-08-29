"""Query helpers for listing and searching catalogued assets.

Pure filtering over :class:`~madify.ports.CatalogStore` results — no I/O
beyond what the catalog port already performed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from madify.errors import AssetNotFoundError

if TYPE_CHECKING:
    from madify.models import MediaAsset
    from madify.ports import CatalogStore


def resolve_asset(
    catalog: CatalogStore,
    *,
    asset_id: int | None = None,
    path: str | None = None,
) -> MediaAsset:
    """Load an asset by exactly one of ``asset_id`` or ``path``.

    Args:
        catalog: Catalog store port.
        asset_id: Catalog id (mutually exclusive with ``path``).
        path: Absolute asset path (mutually exclusive with ``asset_id``).

    Returns:
        The requested :class:`~madify.models.MediaAsset`.

    Raises:
        AssetNotFoundError: Both or neither selector was given, or the asset
            does not exist.
    """
    if asset_id is None and path is None:
        message = "provide asset id or path (or use --all)"
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


def list_catalog(catalog: CatalogStore) -> list[MediaAsset]:
    """Return all assets ordered by id.

    Args:
        catalog: Catalog store port.

    Returns:
        Assets from :meth:`~madify.ports.CatalogStore.list_assets`.
    """
    return catalog.list_assets()


def search_catalog(
    catalog: CatalogStore,
    *,
    query: str | None = None,
    tag: str | None = None,
) -> list[MediaAsset]:
    """Filter assets by substring query and/or exact tag (casefold).

    Args:
        catalog: Catalog store port.
        query: Case-insensitive substring matched against title, description,
            path, or any tag. ``None`` or blank skips this filter.
        tag: Require a tag equal to this value (casefold). ``None`` skips.

    Returns:
        Matching assets in catalog order.

    Raises:
        ValueError: Neither ``query`` nor ``tag`` was provided.
    """
    needle = (query or "").strip()
    tag_key = (tag or "").strip()
    if not needle and not tag_key:
        message = "provide --query and/or --tag"
        raise ValueError(message)

    results: list[MediaAsset] = []
    for asset in catalog.list_assets():
        if tag_key and not _has_tag(asset, tag_key):
            continue
        if needle and not _matches_query(asset, needle):
            continue
        results.append(asset)
    return results


def _has_tag(asset: MediaAsset, tag_key: str) -> bool:
    key = tag_key.casefold()
    return any(t.casefold() == key for t in asset.metadata.tags)


def _matches_query(asset: MediaAsset, needle: str) -> bool:
    n = needle.casefold()
    haystacks = [
        asset.path,
        asset.metadata.title,
        asset.metadata.description,
        *asset.metadata.tags,
        asset.kind.value,
    ]
    return any(n in h.casefold() for h in haystacks)
