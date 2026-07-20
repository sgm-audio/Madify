"""Core domain types for catalogued media assets.

These dataclasses are pure value objects: no I/O, no clock access. Timestamps
are supplied by callers through the :class:`~madify.ports.Clock` port.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class MediaKind(str, Enum):
    """Coarse media classification used for cataloguing and reporting."""

    IMAGE = "image"
    PSD = "psd"
    VIDEO = "video"


@dataclass(frozen=True, slots=True)
class MediaMetadata:
    """User-editable descriptive metadata for an asset.

    Attributes:
        title: Display title; empty means untitled (bulk rename skips it).
        description: Free-text description; may contain internal newlines.
        tags: Ordered unique tags (casefold-deduped at write time).
    """

    title: str = ""
    description: str = ""
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MediaAsset:
    """A single catalogued media file with metadata and audit timestamps.

    Attributes:
        id: Stable catalog primary key.
        path: Absolute filesystem path at last write.
        kind: Image, PSD, or video classification.
        metadata: Title, description, and tags.
        created_at: When the row was first inserted (timezone-aware UTC).
        updated_at: When path or metadata last changed (timezone-aware UTC).
    """

    id: int
    path: str
    kind: MediaKind
    metadata: MediaMetadata
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Outcome of scanning a directory into the catalog.

    Attributes:
        added: Newly inserted assets.
        updated: Existing paths refreshed (e.g. kind stamp).
        skipped: Absolute paths that were not supported media.
    """

    added: tuple[MediaAsset, ...] = ()
    updated: tuple[MediaAsset, ...] = ()
    skipped: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RenameResult:
    """Outcome of a rename pass.

    Attributes:
        renamed: Assets whose on-disk path and catalog path changed.
        unchanged: Assets left as-is (untitled in bulk mode, or already named).
    """

    renamed: tuple[MediaAsset, ...] = ()
    unchanged: tuple[MediaAsset, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class TagRequest:
    """Partial metadata update; ``None`` fields leave the existing value.

    At least one of ``title``, ``description``, or ``tags`` must be set when
    applied through :func:`madify.tagging.build_metadata`.

    Attributes:
        title: New title, or ``None`` to keep the current title.
        description: New description, or ``None`` to keep the current one.
        tags: Full replacement tag list, or ``None`` to keep current tags.
    """

    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
