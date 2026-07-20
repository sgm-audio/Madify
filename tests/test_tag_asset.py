"""Tests for tag_asset use case with injected fakes."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import PurePath

import pytest
from fakes import FakeClock, InMemoryCatalog

from madify.errors import AssetNotFoundError, MetadataValidationError
from madify.models import MediaAsset, MediaKind, MediaMetadata, TagRequest
from madify.tag_asset import tag_asset


def _p(*parts: str) -> str:
    return str(PurePath(*parts))


def _seed(catalog: InMemoryCatalog, *, asset_id: int = 1) -> MediaAsset:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return catalog.seed(
        MediaAsset(
            id=asset_id,
            path=_p("/library/a.jpg"),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(title="Old", description="d", tags=("x",)),
            created_at=now,
            updated_at=now,
        ),
    )


def test_tag_by_id_updates_metadata_and_clock() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    clock = FakeClock()
    clock.advance(minutes=5)
    updated = tag_asset(
        catalog=catalog,
        clock=clock,
        asset_id=1,
        request=TagRequest(title="New", tags=["demo", "clip"]),
    )
    assert updated.metadata.title == "New"
    assert updated.metadata.description == "d"
    assert updated.metadata.tags == ("demo", "clip")
    assert updated.updated_at == clock.now()


def test_tag_by_path() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    updated = tag_asset(
        catalog=catalog,
        clock=FakeClock(),
        path=_p("/library/a.jpg"),
        request=TagRequest(description="hello"),
    )
    assert updated.metadata.description == "hello"
    assert updated.metadata.title == "Old"


def test_tag_requires_id_or_path() -> None:
    with pytest.raises(AssetNotFoundError, match="provide asset id or path"):
        tag_asset(
            catalog=InMemoryCatalog(),
            clock=FakeClock(),
            request=TagRequest(title="x"),
        )


def test_tag_rejects_both_id_and_path() -> None:
    with pytest.raises(AssetNotFoundError, match="not both"):
        tag_asset(
            catalog=InMemoryCatalog(),
            clock=FakeClock(),
            asset_id=1,
            path=_p("/x"),
            request=TagRequest(title="x"),
        )


def test_tag_missing_id() -> None:
    with pytest.raises(AssetNotFoundError, match="asset not found: id=99"):
        tag_asset(
            catalog=InMemoryCatalog(),
            clock=FakeClock(),
            asset_id=99,
            request=TagRequest(title="x"),
        )


def test_tag_missing_path() -> None:
    with pytest.raises(AssetNotFoundError, match="asset not found: path="):
        tag_asset(
            catalog=InMemoryCatalog(),
            clock=FakeClock(),
            path=_p("/nope.jpg"),
            request=TagRequest(title="x"),
        )


def test_tag_propagates_validation_error() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    with pytest.raises(MetadataValidationError, match="at least one"):
        tag_asset(
            catalog=catalog,
            clock=FakeClock(),
            asset_id=1,
            request=TagRequest(),
        )
