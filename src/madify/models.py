"""Core domain types for catalogued media assets."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


class MediaKind(str, Enum):
    IMAGE = "image"
    PSD = "psd"
    VIDEO = "video"


@dataclass(frozen=True, slots=True)
class MediaMetadata:
    title: str = ""
    description: str = ""
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MediaAsset:
    id: int
    path: str
    kind: MediaKind
    metadata: MediaMetadata
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ScanResult:
    added: tuple[MediaAsset, ...] = ()
    updated: tuple[MediaAsset, ...] = ()
    skipped: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RenameResult:
    renamed: tuple[MediaAsset, ...] = ()
    unchanged: tuple[MediaAsset, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class TagRequest:
    title: str | None = None
    description: str | None = None
    tags: list[str] | None = None
