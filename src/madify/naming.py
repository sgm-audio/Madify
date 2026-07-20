"""Pure filename construction for metadata-driven renames.

Stems are derived from titles only. Collision resolution appends ``_2``,
``_3``, … while comparing paths with :meth:`str.casefold` so Windows-style
case-insensitive filesystems are handled correctly.
"""

from __future__ import annotations

import re
from pathlib import PurePath
from typing import TYPE_CHECKING

from madify.errors import RenameError

if TYPE_CHECKING:
    from madify.models import MediaAsset

_UNSAFE = re.compile(r"[^\w.\-]+", re.UNICODE)
_COLLAPSE = re.compile(r"_{2,}")
_MAX_COLLISION_ATTEMPTS = 10_000


def sanitize_filename_stem(title: str) -> str:
    """Turn a title into a filesystem-safe stem (no extension).

    Args:
        title: Asset title.

    Returns:
        Sanitized stem, truncated to 120 characters.

    Raises:
        RenameError: Title is blank or sanitizes to an empty stem.
    """
    cleaned = title.strip()
    if not cleaned:
        message = "cannot rename asset without a title"
        raise RenameError(message)
    stem = _UNSAFE.sub("_", cleaned)
    stem = _COLLAPSE.sub("_", stem).strip("._")
    if not stem:
        message = f"title produces an empty filename: {title!r}"
        raise RenameError(message)
    return stem[:120]


def proposed_filename(asset: MediaAsset) -> str:
    """Return ``{sanitized_title}{lowercased_suffix}`` for ``asset``.

    Args:
        asset: Catalogued asset whose title and path drive the name.

    Returns:
        Filename only (no parent directory).
    """
    path = PurePath(asset.path)
    stem = sanitize_filename_stem(asset.metadata.title)
    return f"{stem}{path.suffix.lower()}"


def proposed_path(asset: MediaAsset) -> str:
    """Return the desired absolute path after a title-based rename.

    Args:
        asset: Catalogued asset.

    Returns:
        Path in the same directory as ``asset.path`` with a new filename.
    """
    path = PurePath(asset.path)
    return str(path.with_name(proposed_filename(asset)))


def allocate_unique_path(desired: str, taken: set[str]) -> str:
    """Pick ``desired``, or ``stem_2`` / ``stem_3`` … if already taken.

    Args:
        desired: Preferred absolute path.
        taken: Set of casefolded paths that must not be reused.

    Returns:
        An unused absolute path string.

    Raises:
        RenameError: Exhausted collision attempts without a free name.
    """
    path = PurePath(desired)
    parent = path.parent
    stem = path.stem
    suffix = path.suffix
    candidate = desired
    n = 2
    while candidate.casefold() in taken:
        candidate = str(parent / f"{stem}_{n}{suffix}")
        n += 1
        if n > _MAX_COLLISION_ATTEMPTS:
            message = f"could not allocate unique name for {desired}"
            raise RenameError(message)
    return candidate
