"""Narrow I/O ports injected into core use cases.

Core modules depend only on these protocols. Production adapters live in
``local_fs``, ``system_clock``, and ``sqlite_catalog``; tests supply fakes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from madify.errors import MetadataWriteError

if TYPE_CHECKING:
    from datetime import datetime

    from madify.models import MediaAsset, MediaKind, MediaMetadata


class Clock(Protocol):
    """Time source for audit timestamps."""

    def now(self) -> datetime:
        """Return the current timezone-aware UTC timestamp."""


class FileSystem(Protocol):
    """Filesystem operations required by scan and rename."""

    def is_directory(self, path: str) -> bool:
        """Return True when path exists and is a directory."""

    def iter_files(self, root: str) -> list[str]:
        """Return absolute paths of all files under root (recursive)."""

    def exists(self, path: str) -> bool:
        """Return True when path exists."""

    def rename(self, source: str, destination: str) -> None:
        """Rename or move a file; raise OSError on failure."""


class CatalogStore(Protocol):
    """Persistent catalog of media assets and metadata."""

    def get_by_id(self, asset_id: int) -> MediaAsset | None:
        """Load one asset by id, or None."""

    def get_by_path(self, path: str) -> MediaAsset | None:
        """Load one asset by absolute path, or None."""

    def list_assets(self) -> list[MediaAsset]:
        """Return all assets ordered by id."""

    def upsert_scanned(
        self,
        path: str,
        kind: MediaKind,
        *,
        now: datetime,
    ) -> tuple[MediaAsset, bool]:
        """Insert or refresh a scanned path.

        Returns:
            ``(asset, created)`` where ``created`` is True on insert.
        """

    def update_metadata(
        self,
        asset_id: int,
        metadata: MediaMetadata,
        *,
        now: datetime,
    ) -> MediaAsset:
        """Replace metadata for an existing asset."""

    def update_path(
        self,
        asset_id: int,
        new_path: str,
        *,
        now: datetime,
    ) -> MediaAsset:
        """Update stored path after a successful rename."""


class MetadataWriter(Protocol):
    """Write descriptive metadata beside or into a media file."""

    def write(self, path: str, metadata: MediaMetadata) -> None:
        """Persist title, description, and tags for ``path``.

        Raises:
            OSError: Underlying write failed.
        """


def write_metadata(
    writer: MetadataWriter | None,
    path: str,
    metadata: MediaMetadata,
) -> None:
    """Write ``metadata`` through ``writer``, wrapping OSError uniformly.

    Shared by every use case that persists metadata after a catalog update, so
    all of them surface the same :class:`~madify.errors.MetadataWriteError`
    instead of leaking raw :class:`OSError`.

    Args:
        writer: Metadata writer port, or ``None`` to skip writing.
        path: Media path the metadata belongs to (used in error messages).
        metadata: Metadata to persist.

    Raises:
        MetadataWriteError: ``writer`` raised :class:`OSError`.
    """
    if writer is None:
        return
    try:
        writer.write(path, metadata)
    except OSError as exc:
        message = f"failed to write metadata for {path}: {exc}"
        raise MetadataWriteError(message) from exc
