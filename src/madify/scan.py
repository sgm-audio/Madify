"""Scan a directory and upsert supported media into the catalog.

Uses injected :class:`~madify.ports.FileSystem`,
:class:`~madify.ports.CatalogStore`, and :class:`~madify.ports.Clock` only —
no direct OS or database imports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from madify.errors import ScanError
from madify.media_kinds import classify_media, is_supported_media
from madify.models import MediaAsset, ScanResult

if TYPE_CHECKING:
    from madify.ports import CatalogStore, Clock, FileSystem


def scan_directory(
    root: str,
    *,
    fs: FileSystem,
    catalog: CatalogStore,
    clock: Clock,
) -> ScanResult:
    """Walk ``root`` and upsert every supported media file.

    Unsupported files are listed in :attr:`~madify.models.ScanResult.skipped`
    and never raise. Paths are processed in sorted order for determinism.

    Args:
        root: Directory to scan recursively.
        fs: Filesystem port.
        catalog: Catalog store port.
        clock: Clock port for ``created_at`` / ``updated_at``.

    Returns:
        Added, updated, and skipped path collections.

    Raises:
        ScanError: ``root`` is not an existing directory.
    """
    if not fs.is_directory(root):
        message = f"scan root is not a directory: {root}"
        raise ScanError(message)

    added: list[MediaAsset] = []
    updated: list[MediaAsset] = []
    skipped: list[str] = []

    for path in sorted(fs.iter_files(root)):
        if not is_supported_media(path):
            skipped.append(path)
            continue
        kind = classify_media(path)
        asset, created = catalog.upsert_scanned(path, kind, now=clock.now())
        if created:
            added.append(asset)
        else:
            updated.append(asset)

    return ScanResult(
        added=tuple(added),
        updated=tuple(updated),
        skipped=tuple(skipped),
    )
