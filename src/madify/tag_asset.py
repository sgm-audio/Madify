"""Apply title, description, and tags to a catalogued asset.

Resolves the target by id xor path, merges the request onto existing
metadata, persists via :class:`~madify.ports.CatalogStore`, and optionally
writes an XMP sidecar through :class:`~madify.ports.MetadataWriter`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from madify.errors import AssetNotFoundError, MetadataWriteError
from madify.tagging import build_metadata

if TYPE_CHECKING:
    from madify.models import MediaAsset, TagRequest
    from madify.ports import CatalogStore, Clock, MetadataWriter


def tag_asset(  # noqa: PLR0913
    *,
    catalog: CatalogStore,
    clock: Clock,
    request: TagRequest,
    asset_id: int | None = None,
    path: str | None = None,
    metadata_writer: MetadataWriter | None = None,
) -> MediaAsset:
    """Update metadata for one asset identified by id or path.

    Args:
        catalog: Catalog store port.
        clock: Clock port for ``updated_at``.
        request: Partial metadata fields to apply.
        asset_id: Catalog id (mutually exclusive with ``path``).
        path: Absolute asset path (mutually exclusive with ``asset_id``).
        metadata_writer: Optional writer for on-disk / sidecar metadata.
            Failures raise :class:`~madify.errors.MetadataWriteError` after
            the catalog update succeeds (catalog remains source of truth).

    Returns:
        The updated :class:`~madify.models.MediaAsset`.

    Raises:
        AssetNotFoundError: Missing target, both id and path, or neither.
        MetadataValidationError: Request fails validation (from tagging).
        MetadataWriteError: Sidecar/file write failed after catalog update.
    """
    asset = _resolve_asset(catalog, asset_id=asset_id, path=path)
    metadata = build_metadata(
        title=request.title,
        description=request.description,
        tags=request.tags,
        base=asset.metadata,
        replace_tags=request.replace_tags,
    )
    updated = catalog.update_metadata(asset.id, metadata, now=clock.now())
    if metadata_writer is not None:
        try:
            metadata_writer.write(updated.path, updated.metadata)
        except OSError as exc:
            message = f"failed to write metadata for {updated.path}: {exc}"
            raise MetadataWriteError(message) from exc
    return updated


def _resolve_asset(
    catalog: CatalogStore,
    *,
    asset_id: int | None,
    path: str | None,
) -> MediaAsset:
    """Load an asset by exactly one of ``asset_id`` or ``path``."""
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
