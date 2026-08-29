"""Remove tags (and optionally title/description) from catalogued assets.

Mirrors :mod:`madify.tag_asset`: targets one asset by id xor path, or every
asset optionally filtered by kind, persists via the catalog port, and writes
an XMP sidecar through :class:`~madify.ports.MetadataWriter` when provided.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from madify.models import MediaMetadata, UntagRequest
from madify.ports import write_metadata
from madify.query import resolve_asset

if TYPE_CHECKING:
    from madify.models import MediaAsset, MediaKind
    from madify.ports import CatalogStore, Clock, MetadataWriter


def untag_asset(  # noqa: PLR0913
    catalog: CatalogStore,
    clock: Clock,
    request: UntagRequest,
    *,
    asset_id: int | None = None,
    path: str | None = None,
    metadata_writer: MetadataWriter | None = None,
) -> MediaAsset:
    """Clear requested fields for one asset identified by id or path.

    Args:
        catalog: Catalog store port.
        clock: Clock port for ``updated_at``.
        request: Fields to clear.
        asset_id: Catalog id (mutually exclusive with ``path``).
        path: Absolute asset path (mutually exclusive with ``asset_id``).
        metadata_writer: Optional writer for on-disk / sidecar metadata.

    Returns:
        The updated :class:`~madify.models.MediaAsset`.

    Raises:
        AssetNotFoundError: Missing target, both id and path, or neither.
        MetadataWriteError: Sidecar/file write failed after catalog update.
    """
    asset = resolve_asset(catalog, asset_id=asset_id, path=path)
    return _apply(catalog, clock, asset, request, metadata_writer=metadata_writer)


def untag_many(
    catalog: CatalogStore,
    clock: Clock,
    request: UntagRequest,
    *,
    kind: MediaKind | None = None,
    metadata_writer: MetadataWriter | None = None,
) -> list[MediaAsset]:
    """Clear requested fields on every asset, optionally filtered by kind.

    Args:
        catalog: Catalog store port.
        clock: Clock port for ``updated_at``.
        request: Fields to clear.
        kind: Optional :class:`~madify.models.MediaKind` filter.
        metadata_writer: Optional writer for on-disk / sidecar metadata.

    Returns:
        Updated assets, in ascending id order.

    Raises:
        MetadataWriteError: Sidecar/file write failed after a catalog update.
    """
    updated_assets: list[MediaAsset] = []
    for asset in catalog.list_assets():
        if kind is not None and asset.kind != kind:
            continue
        updated_assets.append(
            _apply(catalog, clock, asset, request, metadata_writer=metadata_writer)
        )
    return updated_assets


def _apply(
    catalog: CatalogStore,
    clock: Clock,
    asset: MediaAsset,
    request: UntagRequest,
    *,
    metadata_writer: MetadataWriter | None,
) -> MediaAsset:
    """Clear requested fields, persist, and write the sidecar for one asset."""
    metadata = _cleared_metadata(asset.metadata, request)
    updated = catalog.update_metadata(asset.id, metadata, now=clock.now())
    write_metadata(metadata_writer, updated.path, updated.metadata)
    return updated


def _cleared_metadata(base: MediaMetadata, request: UntagRequest) -> MediaMetadata:
    """Return ``base`` with the fields named in ``request`` cleared."""
    removed = {t.casefold() for t in request.tags}
    if removed:
        new_tags = tuple(t for t in base.tags if t.casefold() not in removed)
    else:
        new_tags = ()
    return MediaMetadata(
        title="" if request.clear_title else base.title,
        description="" if request.clear_description else base.description,
        tags=new_tags,
    )
