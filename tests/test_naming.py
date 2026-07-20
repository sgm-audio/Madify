"""Tests for title→filename allocation."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import PurePath

import pytest

from madify.errors import RenameError
from madify.models import MediaAsset, MediaKind, MediaMetadata
from madify.naming import (
    allocate_unique_path,
    proposed_filename,
    proposed_path,
    sanitize_filename_stem,
)


def _p(*parts: str) -> str:
    """Platform-native path string (PurePath normalizes separators)."""
    return str(PurePath(*parts))


def _asset(path: str, title: str) -> MediaAsset:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return MediaAsset(
        id=1,
        path=path,
        kind=MediaKind.IMAGE,
        metadata=MediaMetadata(title=title),
        created_at=now,
        updated_at=now,
    )


def test_sanitize_filename_stem_replaces_unsafe() -> None:
    assert sanitize_filename_stem("Clip One!") == "Clip_One"
    assert sanitize_filename_stem("  a/b:c*d  ") == "a_b_c_d"


def test_sanitize_filename_stem_rejects_blank_title() -> None:
    with pytest.raises(RenameError, match="without a title"):
        sanitize_filename_stem("   ")


def test_sanitize_filename_stem_rejects_all_unsafe() -> None:
    with pytest.raises(RenameError, match="empty filename"):
        sanitize_filename_stem("!!!")


def test_sanitize_filename_stem_truncates_to_120() -> None:
    stem = sanitize_filename_stem("a" * 200)
    assert len(stem) == 120


def test_proposed_filename_lowercases_suffix() -> None:
    assert proposed_filename(_asset(_p("C:/media/shot.JPG"), "Clip One")) == (
        "Clip_One.jpg"
    )


def test_proposed_path_same_directory() -> None:
    asset = _asset(_p("/media/shot.jpg"), "Clip One")
    assert proposed_path(asset) == _p("/media/Clip_One.jpg")


def test_allocate_unique_path_uses_desired_when_free() -> None:
    taken: set[str] = set()
    desired = _p("/m/Clip.jpg")
    assert allocate_unique_path(desired, taken) == desired


def test_allocate_unique_path_collisions_increment() -> None:
    desired = _p("/m/Clip.jpg")
    taken = {
        desired.casefold(),
        _p("/m/Clip_2.jpg").casefold(),
    }
    assert allocate_unique_path(desired, taken) == _p("/m/Clip_3.jpg")


def test_allocate_unique_path_exhaustion() -> None:
    desired = _p("/m/Clip.jpg")
    parent = PurePath(desired).parent
    stem = PurePath(desired).stem
    suffix = PurePath(desired).suffix
    taken = {desired.casefold()}
    taken.update(
        {str(parent / f"{stem}_{n}{suffix}").casefold() for n in range(2, 10_002)},
    )
    with pytest.raises(RenameError, match="could not allocate"):
        allocate_unique_path(desired, taken)
