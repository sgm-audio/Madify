"""Tests for SqliteCatalog adapter (temp-file / in-memory, no wall clock)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from madify.errors import AssetNotFoundError, CatalogError
from madify.models import MediaKind, MediaMetadata
from madify.sqlite_catalog import SqliteCatalog


def _now() -> datetime:
    return datetime(2026, 7, 19, 15, 0, 0, tzinfo=UTC)


def test_sqlite_upsert_get_list_and_update(tmp_path: Path) -> None:
    db = str(tmp_path / "catalog.sqlite")
    catalog = SqliteCatalog(db)
    try:
        asset, created = catalog.upsert_scanned(
            str(tmp_path / "a.jpg"),
            MediaKind.IMAGE,
            now=_now(),
        )
        assert created is True
        assert asset.metadata == MediaMetadata()
        assert catalog.get_by_id(asset.id) == asset
        assert catalog.get_by_path(asset.path) == asset
        assert catalog.list_assets() == [asset]

        later = datetime(2026, 7, 19, 16, 0, 0, tzinfo=UTC)
        refreshed, created2 = catalog.upsert_scanned(
            asset.path,
            MediaKind.IMAGE,
            now=later,
        )
        assert created2 is False
        assert refreshed.id == asset.id
        assert refreshed.updated_at == later

        meta = MediaMetadata(title="T", description="D", tags=("x", "y"))
        tagged = catalog.update_metadata(asset.id, meta, now=later)
        assert tagged.metadata == meta

        new_path = str(tmp_path / "T.jpg")
        moved = catalog.update_path(asset.id, new_path, now=later)
        assert moved.path == new_path
        assert catalog.get_by_path(asset.path) is None
        assert catalog.get_by_path(new_path) == moved
    finally:
        catalog.close()


def test_sqlite_update_metadata_missing_id(tmp_path: Path) -> None:
    catalog = SqliteCatalog(str(tmp_path / "c.sqlite"))
    try:
        with pytest.raises(AssetNotFoundError, match="id=42"):
            catalog.update_metadata(42, MediaMetadata(title="x"), now=_now())
    finally:
        catalog.close()


def test_sqlite_update_path_missing_id(tmp_path: Path) -> None:
    catalog = SqliteCatalog(str(tmp_path / "c.sqlite"))
    try:
        with pytest.raises(AssetNotFoundError, match="id=42"):
            catalog.update_path(42, "/nope.jpg", now=_now())
    finally:
        catalog.close()


def test_sqlite_update_path_duplicate_raises(tmp_path: Path) -> None:
    catalog = SqliteCatalog(str(tmp_path / "c.sqlite"))
    try:
        a, _ = catalog.upsert_scanned(
            str(tmp_path / "a.jpg"),
            MediaKind.IMAGE,
            now=_now(),
        )
        b, _ = catalog.upsert_scanned(
            str(tmp_path / "b.jpg"),
            MediaKind.IMAGE,
            now=_now(),
        )
        with pytest.raises(CatalogError, match="path already catalogued"):
            catalog.update_path(b.id, a.path, now=_now())
    finally:
        catalog.close()


def test_sqlite_corrupt_tags_json(tmp_path: Path) -> None:
    db = str(tmp_path / "c.sqlite")
    catalog = SqliteCatalog(db)
    try:
        asset, _ = catalog.upsert_scanned(
            str(tmp_path / "a.jpg"),
            MediaKind.IMAGE,
            now=_now(),
        )
        catalog._conn.execute(
            "UPDATE assets SET tags_json = ? WHERE id = ?",
            ("not-json", asset.id),
        )
        catalog._conn.commit()
        with pytest.raises(CatalogError, match="corrupt tags_json"):
            catalog.get_by_id(asset.id)
    finally:
        catalog.close()


def test_sqlite_corrupt_tags_not_string_list(tmp_path: Path) -> None:
    db = str(tmp_path / "c.sqlite")
    catalog = SqliteCatalog(db)
    try:
        asset, _ = catalog.upsert_scanned(
            str(tmp_path / "a.jpg"),
            MediaKind.IMAGE,
            now=_now(),
        )
        catalog._conn.execute(
            "UPDATE assets SET tags_json = ? WHERE id = ?",
            ("[1, 2]", asset.id),
        )
        catalog._conn.commit()
        with pytest.raises(CatalogError, match="corrupt tags_json"):
            catalog.get_by_id(asset.id)
    finally:
        catalog.close()


def test_sqlite_creates_parent_dirs(tmp_path: Path) -> None:
    db = str(tmp_path / "nested" / "dir" / "c.sqlite")
    catalog = SqliteCatalog(db)
    try:
        assert Path(db).is_file()
    finally:
        catalog.close()


def test_sqlite_corrupt_database_file_raises_useful_error(tmp_path: Path) -> None:
    """A non-SQLite file at the db path fails with a clear CatalogError."""
    db = tmp_path / "not_a_db.sqlite"
    db.write_text("this is not a sqlite database", encoding="utf-8")
    with pytest.raises(CatalogError, match="failed to open catalog"):
        SqliteCatalog(str(db))


def test_sqlite_unicode_roundtrip(tmp_path: Path) -> None:
    """Unicode paths and metadata survive a catalog roundtrip."""
    catalog = SqliteCatalog(str(tmp_path / "c.sqlite"))
    try:
        asset, _ = catalog.upsert_scanned(
            str(tmp_path / "café.jpg"),
            MediaKind.IMAGE,
            now=_now(),
        )
        meta = MediaMetadata(title="日本語の写真", tags=("café", "旅行"))
        tagged = catalog.update_metadata(asset.id, meta, now=_now())
        reloaded = catalog.get_by_id(asset.id)
        assert reloaded is not None
        assert reloaded.path == str(tmp_path / "café.jpg")
        assert reloaded.metadata.title == "日本語の写真"
        assert reloaded.metadata.tags == ("café", "旅行")
        assert tagged == reloaded
    finally:
        catalog.close()
