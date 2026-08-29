"""Apply title, description, and tags to a catalogued asset.

Resolves the target by id xor path, merges the request onto existing
metadata, persists via :class:`~madify.ports.CatalogStore`, and optionally
writes an XMP sidecar through :class:`~madify.ports.MetadataWriter`.
"""

from __future__ import annotations

import re
from pathlib import PurePath
from typing import TYPE_CHECKING

from madify.errors import MetadataValidationError
from madify.models import TagRequest
from madify.ports import write_metadata
from madify.query import resolve_asset
from madify.tagging import build_metadata

if TYPE_CHECKING:
    from madify.models import MediaAsset, MediaKind
    from madify.ports import CatalogStore, Clock, MetadataWriter

_FILENAME_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
_MIN_AUTO_TOKEN_LEN = 3


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
    asset = resolve_asset(catalog, asset_id=asset_id, path=path)
    metadata = build_metadata(
        title=request.title,
        description=request.description,
        tags=request.tags,
        base=asset.metadata,
        replace_tags=request.replace_tags,
    )
    updated = catalog.update_metadata(asset.id, metadata, now=clock.now())
    write_metadata(metadata_writer, updated.path, updated.metadata)
    return updated


def tag_many(  # noqa: PLR0913
    catalog: CatalogStore,
    clock: Clock,
    request: TagRequest,
    *,
    kind: MediaKind | None = None,
    auto: bool = False,
    metadata_writer: MetadataWriter | None = None,
) -> list[MediaAsset]:
    """Apply ``request`` to every asset, optionally filtered by kind.

    When ``auto`` is True and the request leaves the title unset, derive the
    title from the filename stem. When the request leaves tags unset and
    ``auto`` is True, add a tag for the file extension and any hyphen/underscore
    tokens in the filename stem (deduped against the existing tag set).

    Args:
        catalog: Catalog store port.
        clock: Clock port for ``updated_at``.
        request: Partial metadata fields to apply.
        kind: Optional :class:`~madify.models.MediaKind` filter.
        auto: When True, fill in untitled title/tags from the filename.
        metadata_writer: Optional writer for on-disk / sidecar metadata.

    Returns:
        Updated assets, in ascending id order.

    Raises:
        MetadataWriteError: Sidecar/file write failed after a catalog update.
    """
    if (
        request.title is None
        and request.description is None
        and request.tags is None
        and not auto
    ):
        message = "provide at least one of title, description, tags, or --auto"
        raise MetadataValidationError(message)
    updated_assets: list[MediaAsset] = []
    for asset in catalog.list_assets():
        if kind is not None and asset.kind != kind:
            continue
        effective = _effective_request(asset, request, auto=auto)
        metadata = build_metadata(
            title=effective.title,
            description=effective.description,
            tags=effective.tags,
            base=asset.metadata,
            replace_tags=effective.replace_tags,
        )
        next_asset = catalog.update_metadata(asset.id, metadata, now=clock.now())
        write_metadata(metadata_writer, next_asset.path, next_asset.metadata)
        updated_assets.append(next_asset)
    return updated_assets


def _effective_request(
    asset: MediaAsset,
    request: TagRequest,
    *,
    auto: bool,
) -> TagRequest:
    """Fill in untitled title/tags from ``asset.path`` when ``auto`` is True."""
    if not auto:
        return request
    title = request.title
    extra_tags: list[str] | None = request.tags
    if title is None and not asset.metadata.title:
        title = PurePath(asset.path).stem
    derived = _auto_tags_for(asset)
    extra_tags = derived if extra_tags is None else [*extra_tags, *derived]
    return TagRequest(
        title=title,
        description=request.description,
        tags=extra_tags,
        replace_tags=request.replace_tags,
    )


def _auto_tags_for(asset: MediaAsset) -> list[str]:
    """Derive a small tag set from a media path's extension and stem."""
    path = PurePath(asset.path)
    ext = path.suffix.lstrip(".").lower()
    tags: list[str] = []
    if ext:
        tags.append(ext)
    stem_tokens = _FILENAME_TOKEN_RE.findall(path.stem)
    for token in stem_tokens:
        if token.isdigit():
            continue
        if len(token) < _MIN_AUTO_TOKEN_LEN:
            continue
        if token.lower() in {ext.lower(), "img", "image", "photo", "video"}:
            continue
        tags.append(token.lower())
    return tags
