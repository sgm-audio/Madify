"""Scan a directory and upsert supported media into the catalog."""

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
