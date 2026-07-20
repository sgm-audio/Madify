"""Tests for media kind classification."""

from __future__ import annotations

import pytest

from madify.errors import UnsupportedMediaError
from madify.media_kinds import classify_media, extension_of, is_supported_media
from madify.models import MediaKind


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("photo.JPG", ".jpg"),
        ("/a/b/c.PNG", ".png"),
        ("noext", ""),
        ("archive.tar.gz", ".gz"),
    ],
)
def test_extension_of_lowercases_suffix(path: str, expected: str) -> None:
    assert extension_of(path) == expected


@pytest.mark.parametrize(
    ("path", "kind"),
    [
        ("a.jpg", MediaKind.IMAGE),
        ("a.JPEG", MediaKind.IMAGE),
        ("a.heic", MediaKind.IMAGE),
        ("a.dng", MediaKind.IMAGE),
        ("layer.psd", MediaKind.PSD),
        ("big.PSB", MediaKind.PSD),
        ("clip.mp4", MediaKind.VIDEO),
        ("clip.MOV", MediaKind.VIDEO),
        ("clip.mkv", MediaKind.VIDEO),
    ],
)
def test_classify_media_supported(path: str, kind: MediaKind) -> None:
    assert classify_media(path) == kind
    assert is_supported_media(path) is True


@pytest.mark.parametrize(
    "path",
    ["readme.txt", "script.py", "archive.zip", "noext", "image.xyz"],
)
def test_classify_media_unsupported(path: str) -> None:
    with pytest.raises(UnsupportedMediaError, match="unsupported media type"):
        classify_media(path)
    assert is_supported_media(path) is False
