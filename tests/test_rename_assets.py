"""Tests for rename_assets use case with injected fakes."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import PurePath

import pytest
from fakes import FakeClock, FakeFileSystem, InMemoryCatalog

from madify.errors import AssetNotFoundError, RenameError
from madify.models import MediaAsset, MediaKind, MediaMetadata
from madify.rename_assets import rename_assets


def _p(*parts: str) -> str:
    return str(PurePath(*parts))


def _asset(
    asset_id: int,
    path: str,
    title: str,
    *,
    kind: MediaKind = MediaKind.IMAGE,
) -> MediaAsset:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return MediaAsset(
        id=asset_id,
        path=path,
        kind=kind,
        metadata=MediaMetadata(title=title),
        created_at=now,
        updated_at=now,
    )


def test_rename_all_titled_assets() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    fs.add_file(_p("/library/b.psd"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), "Clip One"))
    catalog.seed(
        _asset(2, _p("/library/b.psd"), "Layer Comp", kind=MediaKind.PSD),
    )
    clock = FakeClock()

    result = rename_assets(catalog=catalog, fs=fs, clock=clock)

    assert len(result.renamed) == 2
    assert result.unchanged == ()
    paths = {a.id: a.path for a in result.renamed}
    assert paths[1] == _p("/library/Clip_One.jpg")
    assert paths[2] == _p("/library/Layer_Comp.psd")
    assert _p("/library/Clip_One.jpg") in fs.files
    assert _p("/library/a.jpg") not in fs.files
    assert catalog.get_by_id(1) is not None
    assert catalog.get_by_id(1).path == _p("/library/Clip_One.jpg")  # type: ignore[union-attr]


def test_bulk_rename_skips_untitled() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), ""))
    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock())
    assert result.renamed == ()
    assert len(result.unchanged) == 1
    assert _p("/library/a.jpg") in fs.files


def test_rename_already_correct_name_is_unchanged() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/Clip_One.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/Clip_One.jpg"), "Clip One"))
    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)
    assert result.renamed == ()
    assert len(result.unchanged) == 1


def test_rename_single_id_without_title_errors() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), "  "))
    with pytest.raises(RenameError, match="has no title"):
        rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)


def test_rename_missing_id() -> None:
    with pytest.raises(AssetNotFoundError, match="id=99"):
        rename_assets(
            catalog=InMemoryCatalog(),
            fs=FakeFileSystem(),
            clock=FakeClock(),
            asset_id=99,
        )


def test_rename_collision_with_neighbor_file() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    fs.add_file(_p("/library/Clip_One.jpg"))  # neighbor, not catalogued
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), "Clip One"))
    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)
    assert result.renamed[0].path == _p("/library/Clip_One_2.jpg")
    assert _p("/library/Clip_One_2.jpg") in fs.files


def test_rename_filesystem_failure_wraps_oserror() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    fs.rename_error = OSError("disk full")
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), "Clip One"))
    with pytest.raises(RenameError, match="failed to rename"):
        rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)
    assert _p("/library/a.jpg") in fs.files


def test_rename_case_only_change_counts_unchanged() -> None:
    """Same path ignoring case → no filesystem rename (Windows-safe)."""
    path = _p("/library/clip_one.jpg")
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(path)
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, path, "Clip One"))
    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)
    assert result.renamed == ()
    assert len(result.unchanged) == 1
    assert path in fs.files


def test_rename_errors_if_destination_exists_on_fs() -> None:
    """Force exists() True for the proposed destination after allocation."""
    src = _p("/library/a.jpg")
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(src)
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, src, "Clip One"))

    class ExistsTrap(FakeFileSystem):
        def exists(self, path: str) -> bool:
            if PurePath(path).name.casefold() == "clip_one.jpg":
                return True
            return super().exists(path)

    trap = ExistsTrap(directories=set(fs.directories), files=set(fs.files))
    with pytest.raises(RenameError, match="destination already exists"):
        rename_assets(catalog=catalog, fs=trap, clock=FakeClock(), asset_id=1)


def test_rename_moves_sibling_xmp_sidecar() -> None:
    """Media rename also renames a same-stem ``.xmp`` sidecar when present."""
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/foo.jpg"))
    fs.add_file(_p("/library/foo.xmp"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/foo.jpg"), "Golden Hour"))

    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)

    assert result.renamed[0].path == _p("/library/Golden_Hour.jpg")
    assert _p("/library/Golden_Hour.jpg") in fs.files
    assert _p("/library/Golden_Hour.xmp") in fs.files
    assert _p("/library/foo.jpg") not in fs.files
    assert _p("/library/foo.xmp") not in fs.files
    # Catalog stores media path only — sidecar is filesystem-only.
    assert catalog.get_by_id(1) is not None
    assert catalog.get_by_id(1).path == _p("/library/Golden_Hour.jpg")  # type: ignore[union-attr]


def test_rename_without_sidecar_is_unchanged_happy_path() -> None:
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/foo.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/foo.jpg"), "Golden Hour"))

    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)

    assert result.renamed[0].path == _p("/library/Golden_Hour.jpg")
    assert _p("/library/Golden_Hour.xmp") not in fs.files


def test_rename_skips_sidecar_when_target_xmp_exists() -> None:
    """Do not clobber an existing destination ``.xmp``; leave the old sidecar."""
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/foo.jpg"))
    fs.add_file(_p("/library/foo.xmp"))
    fs.add_file(_p("/library/Golden_Hour.xmp"))  # pre-existing target
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/foo.jpg"), "Golden Hour"))

    result = rename_assets(catalog=catalog, fs=fs, clock=FakeClock(), asset_id=1)

    assert result.renamed[0].path == _p("/library/Golden_Hour.jpg")
    assert _p("/library/Golden_Hour.jpg") in fs.files
    assert _p("/library/Golden_Hour.xmp") in fs.files
    assert _p("/library/foo.xmp") in fs.files  # left in place; not clobbered target


def test_rename_dry_run_plans_without_touching_files() -> None:
    """Dry-run reports proposed destinations but changes nothing on disk/catalog."""
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), "Clip One"))

    result = rename_assets(
        catalog=catalog,
        fs=fs,
        clock=FakeClock(),
        asset_id=1,
        dry_run=True,
    )

    assert result.renamed[0].path == _p("/library/Clip_One.jpg")
    assert _p("/library/a.jpg") in fs.files
    assert _p("/library/Clip_One.jpg") not in fs.files
    assert catalog.get_by_id(1) is not None
    assert catalog.get_by_id(1).path == _p("/library/a.jpg")  # type: ignore[union-attr]


def test_rename_dry_run_collision_suffixes_are_deterministic() -> None:
    """Dry-run and real-run produce the same collision suffixes."""
    fs = FakeFileSystem()
    fs.add_dir(_p("/library"))
    fs.add_file(_p("/library/a.jpg"))
    fs.add_file(_p("/library/Clip_One.jpg"))
    catalog = InMemoryCatalog()
    catalog.seed(_asset(1, _p("/library/a.jpg"), "Clip One"))

    plan = rename_assets(
        catalog=catalog,
        fs=fs,
        clock=FakeClock(),
        asset_id=1,
        dry_run=True,
    )
    assert plan.renamed[0].path == _p("/library/Clip_One_2.jpg")
    assert _p("/library/Clip_One_2.jpg") not in fs.files
