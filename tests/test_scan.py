"""Tests for scan_directory use case with injected fakes."""

from __future__ import annotations

from pathlib import PurePath

import pytest
from fakes import FakeClock, FakeFileSystem, InMemoryCatalog

from madify.errors import ScanError
from madify.models import MediaKind
from madify.scan import scan_directory


def _p(*parts: str) -> str:
    return str(PurePath(*parts))


def test_scan_adds_supported_skips_others() -> None:
    root = _p("/library")
    fs = FakeFileSystem()
    fs.add_dir(root)
    fs.add_file(_p("/library/a.jpg"))
    fs.add_file(_p("/library/b.psd"))
    fs.add_file(_p("/library/c.mp4"))
    fs.add_file(_p("/library/readme.txt"))
    catalog = InMemoryCatalog()
    clock = FakeClock()

    result = scan_directory(root, fs=fs, catalog=catalog, clock=clock)

    assert len(result.added) == 3
    assert result.updated == ()
    assert result.skipped == (_p("/library/readme.txt"),)
    kinds = {a.path: a.kind for a in result.added}
    assert kinds[_p("/library/a.jpg")] == MediaKind.IMAGE
    assert kinds[_p("/library/b.psd")] == MediaKind.PSD
    assert kinds[_p("/library/c.mp4")] == MediaKind.VIDEO
    assert all(a.created_at == clock.now() for a in result.added)


def test_scan_updates_existing_paths() -> None:
    root = _p("/library")
    fs = FakeFileSystem()
    fs.add_dir(root)
    fs.add_file(_p("/library/a.jpg"))
    catalog = InMemoryCatalog()
    clock = FakeClock()
    first = scan_directory(root, fs=fs, catalog=catalog, clock=clock)
    assert len(first.added) == 1
    clock.advance(hours=1)
    second = scan_directory(root, fs=fs, catalog=catalog, clock=clock)
    assert second.added == ()
    assert len(second.updated) == 1
    assert second.updated[0].id == first.added[0].id
    assert second.updated[0].updated_at == clock.now()


def test_scan_rejects_missing_root() -> None:
    fs = FakeFileSystem()
    with pytest.raises(ScanError, match="not a directory"):
        scan_directory(
            _p("/missing"),
            fs=fs,
            catalog=InMemoryCatalog(),
            clock=FakeClock(),
        )


def test_scan_empty_directory() -> None:
    root = _p("/empty")
    fs = FakeFileSystem()
    fs.add_dir(root)
    result = scan_directory(
        root,
        fs=fs,
        catalog=InMemoryCatalog(),
        clock=FakeClock(),
    )
    assert result.added == ()
    assert result.updated == ()
    assert result.skipped == ()
