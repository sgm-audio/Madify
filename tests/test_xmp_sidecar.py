"""Tests for XMP sidecar writer."""

from __future__ import annotations

from pathlib import Path

from madify.models import MediaMetadata
from madify.xmp_sidecar import XmpSidecarWriter, sidecar_path_for


def test_sidecar_path_for() -> None:
    assert sidecar_path_for(str(Path("/a/b/c.jpg"))).endswith("c.xmp")


def test_write_creates_xmp_with_fields(tmp_path: Path) -> None:
    media = tmp_path / "shot.jpg"
    media.write_bytes(b"fake")
    meta = MediaMetadata(title="Clip One", description="demo", tags=("a", "b"))
    XmpSidecarWriter().write(str(media), meta)
    sidecar = tmp_path / "shot.xmp"
    assert sidecar.is_file()
    text = sidecar.read_text(encoding="utf-8")
    assert "Clip One" in text
    assert "demo" in text
    assert ">a<" in text or ">a</" in text
    assert "xpacket" in text
