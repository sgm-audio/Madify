"""Tests for catalog list/search filtering."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import PurePath

import pytest
from fakes import InMemoryCatalog

from madify.models import MediaAsset, MediaKind, MediaMetadata
from madify.query import list_catalog, search_catalog


def _p(*parts: str) -> str:
    return str(PurePath(*parts))


def _seed(catalog: InMemoryCatalog) -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    catalog.seed(
        MediaAsset(
            id=1,
            path=_p("/lib/a.jpg"),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(title="Clip One", tags=("demo", "photo")),
            created_at=now,
            updated_at=now,
        ),
    )
    catalog.seed(
        MediaAsset(
            id=2,
            path=_p("/lib/b.psd"),
            kind=MediaKind.PSD,
            metadata=MediaMetadata(title="Layer", tags=("psd",)),
            created_at=now,
            updated_at=now,
        ),
    )


def test_list_catalog_returns_all() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    assert [a.id for a in list_catalog(catalog)] == [1, 2]


def test_search_by_query_title() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    hits = search_catalog(catalog, query="clip")
    assert [a.id for a in hits] == [1]


def test_search_by_tag() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    hits = search_catalog(catalog, tag="PSD")
    assert [a.id for a in hits] == [2]


def test_search_query_and_tag() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    hits = search_catalog(catalog, query="lib", tag="demo")
    assert [a.id for a in hits] == [1]


def test_search_requires_filter() -> None:
    with pytest.raises(ValueError, match="provide --query"):
        search_catalog(InMemoryCatalog())
