"""Classify media files by extension (images, PSD, video).

Classification is extension-only (no magic-byte sniffing). Unsupported
extensions raise :class:`~madify.errors.UnsupportedMediaError`.
"""

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
    """Return the lowercased file suffix, including the leading dot.

    Args:
        path: Filesystem path or filename.

    Returns:
        Suffix such as ``.jpg``, or empty string when there is no extension.
    """
    return PurePath(path).suffix.lower()


def classify_media(path: str) -> MediaKind:
    """Map a path to :class:`~madify.models.MediaKind` by extension.

    Args:
        path: Filesystem path or filename.

    Returns:
        ``IMAGE``, ``PSD``, or ``VIDEO``.

    Raises:
        UnsupportedMediaError: Extension is not in the supported sets.
    """
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
    """Return whether ``path`` would succeed under :func:`classify_media`.

    Args:
        path: Filesystem path or filename.

    Returns:
        ``True`` for supported image/PSD/video extensions; otherwise ``False``.
    """
    try:
        classify_media(path)
    except UnsupportedMediaError:
        return False
    return True
