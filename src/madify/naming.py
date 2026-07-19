"""Pure filename construction for metadata-driven renames."""

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
    path = PurePath(asset.path)
    stem = sanitize_filename_stem(asset.metadata.title)
    return f"{stem}{path.suffix.lower()}"


def proposed_path(asset: MediaAsset) -> str:
    path = PurePath(asset.path)
    return str(path.with_name(proposed_filename(asset)))


def allocate_unique_path(desired: str, taken: set[str]) -> str:
    """Pick desired path, or desired stem_2/stem_3… if taken (casefold keys)."""
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
