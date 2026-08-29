"""Cross-platform tests for Windows-style paths and Unicode filenames.

Split into two halves: portable Unicode behavior (works identically on any
platform) and Windows-specific concerns (drive letters, backslashes, and
case-insensitive collision) exercised through the pure string/path helpers so
they pass on Linux CI too.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path, PurePath, PureWindowsPath

from fakes import FakeClock, FakeFileSystem, InMemoryCatalog

from madify.media_kinds import classify_media, extension_of
from madify.models import MediaAsset, MediaKind, MediaMetadata, TagRequest
from madify.naming import (
    allocate_unique_path,
    proposed_filename,
    sanitize_filename_stem,
)
from madify.rename_assets import rename_assets
from madify.scan import scan_directory
from madify.tag_asset import tag_asset
from madify.xmp_sidecar import XmpSidecarWriter, sidecar_path_for


def _p(*parts: str) -> str:
    return str(PurePath(*parts))


def _asset(path: str, title: str, *, asset_id: int = 1) -> MediaAsset:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return MediaAsset(
        id=asset_id,
        path=path,
        kind=MediaKind.IMAGE,
        metadata=MediaMetadata(title=title),
        created_at=now,
        updated_at=now,
    )


# --- Unicode filenames (portable) -------------------------------------------------


def test_sanitize_preserves_unicode_letters() -> None:
    assert sanitize_filename_stem("Café Date") == "Café_Date"
    assert sanitize_filename_stem("日本語の写真") == "日本語の写真"


def test_sanitize_replaces_emoji_with_underscore() -> None:
    assert sanitize_filename_stem("sunset 📷 beach") == "sunset_beach"


def test_scan_unicode_filenames_roundtrip() -> None:
    root = _p("/photos")
    fs = FakeFileSystem()
    fs.add_dir(root)
    fs.add_file(_p("/photos/café.jpg"))
    fs.add_file(_p("/photos/日本語.mp4"))
    catalog = InMemoryCatalog()

    result = scan_directory(root, fs=fs, catalog=catalog, clock=FakeClock())

    paths = {a.path for a in result.added}
    assert _p("/photos/café.jpg") in paths
    assert _p("/photos/日本語.mp4") in paths


def test_rename_unicode_title_moves_file() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/photos"))
    fs.add_file(_p("/photos/a.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(_p("/photos/a.jpg"), "Café Au Lait"))

    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)

    assert result.renamed[0].path == _p("/photos/Café_Au_Lait.jpg")
    assert _p("/photos/Café_Au_Lait.jpg") in fs.files


def test_allocate_unique_path_unicode_collision() -> None:
    desired = _p("/m/写真.jpg")
    taken = {desired.casefold()}
    assert allocate_unique_path(desired, taken) == _p("/m/写真_2.jpg")


def test_sidecar_path_preserves_unicode() -> None:
    assert sidecar_path_for(_p("/m/café.jpg")) == _p("/m/café.xmp")


def test_tag_writes_unicode_sidecar(tmp_path: Path) -> None:
    media = tmp_path / "café.jpg"
    media.write_bytes(b"x")
    catalog = InMemoryCatalog()
    catalog.seed(
        MediaAsset(
            id=1,
            path=str(media),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(),
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        ),
    )
    tag_asset(
        catalog=catalog,
        clock=FakeClock(),
        asset_id=1,
        request=TagRequest(title="日本語の写真", tags=["café"]),
        metadata_writer=XmpSidecarWriter(),
    )
    sidecar = tmp_path / "café.xmp"
    assert sidecar.is_file()
    assert "日本語の写真" in sidecar.read_text(encoding="utf-8")


# --- Windows-style paths (portable pure helpers) ----------------------------------


def test_extension_of_windows_drive_path() -> None:
    assert extension_of(r"C:\photos\IMG_0001.JPG") == ".jpg"


def test_classify_windows_drive_path() -> None:
    assert classify_media(r"C:\photos\clip.MOV") == MediaKind.VIDEO


def test_proposed_filename_keeps_windows_parent_on_native_paths() -> None:
    win = str(PureWindowsPath("C:/photos/shot.JPG"))
    asset = _asset(win, "Clip One")
    assert proposed_filename(asset) == "Clip_One.jpg"


def test_casefold_collision_detects_windows_case_insensitive_duplicate() -> None:
    a = r"C:\Photos\CLIP.jpg"
    b = r"c:\photos\clip.jpg"
    assert a.casefold() == b.casefold()
    assert allocate_unique_path(a, {b.casefold()}) != a
