"""Classify media files by extension (images, PSD, video)."""

from __future__ import annotations

from pathlib import PurePath

from madify.errors import UnsupportedMediaError
from madify.models import MediaKind

_IMAGE_EXTENSIONS = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".tif",
        ".tiff",
        ".bmp",
        ".heic",
        ".heif",
        ".raw",
        ".cr2",
        ".nef",
        ".arw",
        ".dng",
        ".orf",
        ".rw2",
    }
)
_PSD_EXTENSIONS = frozenset({".psd", ".psb"})
_VIDEO_EXTENSIONS = frozenset(
    {
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".m4v",
        ".wmv",
        ".mpg",
        ".mpeg",
        ".3gp",
    }
)


def extension_of(path: str) -> str:
    return PurePath(path).suffix.lower()


def classify_media(path: str) -> MediaKind:
    ext = extension_of(path)
    if ext in _IMAGE_EXTENSIONS:
        return MediaKind.IMAGE
    if ext in _PSD_EXTENSIONS:
        return MediaKind.PSD
    if ext in _VIDEO_EXTENSIONS:
        return MediaKind.VIDEO
    message = f"unsupported media type for path: {path}"
    raise UnsupportedMediaError(message)


def is_supported_media(path: str) -> bool:
    try:
        classify_media(path)
    except UnsupportedMediaError:
        return False
    return True
