"""Tests for tag_asset use case with injected fakes."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path, PurePath

import pytest
from fakes import FakeClock, InMemoryCatalog

from madify.errors import (
    AssetNotFoundError,
    MetadataValidationError,
    MetadataWriteError,
)
from madify.models import MediaAsset, MediaKind, MediaMetadata, TagRequest
from madify.tag_asset import tag_asset
from madify.xmp_sidecar import XmpSidecarWriter


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
    assert updated.metadata.tags == ("x", "demo", "clip")
    assert updated.updated_at == clock.now()


def test_tag_replace_tags() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    updated = tag_asset(
        catalog=catalog,
        clock=FakeClock(),
        asset_id=1,
        request=TagRequest(tags=["only"], replace_tags=True),
    )
    assert updated.metadata.tags == ("only",)


def test_tag_writes_sidecar(tmp_path: Path) -> None:
    media = tmp_path / "a.jpg"
    media.write_bytes(b"x")
    catalog = InMemoryCatalog()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    catalog.seed(
        MediaAsset(
            id=1,
            path=str(media),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(),
            created_at=now,
            updated_at=now,
        ),
    )
    tag_asset(
        catalog=catalog,
        clock=FakeClock(),
        asset_id=1,
        request=TagRequest(title="T", tags=["z"]),
        metadata_writer=XmpSidecarWriter(),
    )
    assert (tmp_path / "a.xmp").is_file()


def test_tag_sidecar_oserror_wraps() -> None:
    class Boom:
        def write(self, path: str, metadata: MediaMetadata) -> None:
            del path, metadata
            message = "disk full"
            raise OSError(message)

    catalog = InMemoryCatalog()
    _seed(catalog)
    with pytest.raises(MetadataWriteError, match="failed to write metadata"):
        tag_asset(
            catalog=catalog,
            clock=FakeClock(),
            asset_id=1,
            request=TagRequest(title="T"),
            metadata_writer=Boom(),  # type: ignore[arg-type]
        )

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
