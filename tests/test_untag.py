"""Tests for the untag use cases with injected fakes."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path, PurePath

import pytest
from fakes import FakeClock, InMemoryCatalog

from madify.errors import AssetNotFoundError, MetadataWriteError
from madify.models import MediaAsset, MediaKind, MediaMetadata, UntagRequest
from madify.untag import untag_asset, untag_many
from madify.xmp_sidecar import XmpSidecarWriter


def _p(*parts: str) -> str:
    return str(PurePath(*parts))


def _seed(
    catalog: InMemoryCatalog,
    *,
    asset_id: int = 1,
    path: str = "/library/a.jpg",
) -> MediaAsset:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return catalog.seed(
        MediaAsset(
            id=asset_id,
            path=_p(path),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(title="Old", description="d", tags=("x", "y")),
            created_at=now,
            updated_at=now,
        ),
    )


def test_untag_by_id_removes_all_tags_by_default() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    clock = FakeClock()
    clock.advance(minutes=5)
    updated = untag_asset(catalog, clock, UntagRequest(), asset_id=1)
    assert updated.metadata.tags == ()
    assert updated.metadata.title == "Old"
    assert updated.metadata.description == "d"
    assert updated.updated_at == clock.now()


def test_untag_removes_specific_tags_casefold() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    updated = untag_asset(
        catalog,
        FakeClock(),
        UntagRequest(tags=("X",)),
        asset_id=1,
    )
    assert updated.metadata.tags == ("y",)


def test_untag_clears_title_and_description() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    updated = untag_asset(
        catalog,
        FakeClock(),
        UntagRequest(clear_title=True, clear_description=True),
        asset_id=1,
    )
    assert updated.metadata.title == ""
    assert updated.metadata.description == ""
    assert updated.metadata.tags == ()


def test_untag_by_path() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    updated = untag_asset(
        catalog,
        FakeClock(),
        UntagRequest(),
        path=_p("/library/a.jpg"),
    )
    assert updated.metadata.tags == ()


def test_untag_requires_id_or_path() -> None:
    with pytest.raises(AssetNotFoundError, match="provide asset id or path"):
        untag_asset(InMemoryCatalog(), FakeClock(), UntagRequest())


def test_untag_rejects_both_id_and_path() -> None:
    with pytest.raises(AssetNotFoundError, match="not both"):
        untag_asset(
            InMemoryCatalog(),
            FakeClock(),
            UntagRequest(),
            asset_id=1,
            path=_p("/x"),
        )


def test_untag_missing_asset() -> None:
    with pytest.raises(AssetNotFoundError, match="asset not found: id=99"):
        untag_asset(InMemoryCatalog(), FakeClock(), UntagRequest(), asset_id=99)


def test_untag_many_applies_to_all() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    _seed(catalog, asset_id=2, path="/library/b.jpg")
    updated = untag_many(catalog, FakeClock(), UntagRequest())
    assert [a.id for a in updated] == [1, 2]
    assert all(a.metadata.tags == () for a in updated)


def test_untag_many_respects_kind_filter() -> None:
    catalog = InMemoryCatalog()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    catalog.seed(
        MediaAsset(
            id=1,
            path=_p("/a.jpg"),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(tags=("x",)),
            created_at=now,
            updated_at=now,
        ),
    )
    catalog.seed(
        MediaAsset(
            id=2,
            path=_p("/b.mp4"),
            kind=MediaKind.VIDEO,
            metadata=MediaMetadata(tags=("y",)),
            created_at=now,
            updated_at=now,
        ),
    )
    updated = untag_many(
        catalog,
        FakeClock(),
        UntagRequest(),
        kind=MediaKind.IMAGE,
    )
    assert [a.id for a in updated] == [1]
    assert updated[0].metadata.tags == ()
    assert catalog.get_by_id(2).metadata.tags == ("y",)


def test_untag_many_removes_only_named_tag() -> None:
    catalog = InMemoryCatalog()
    _seed(catalog)
    _seed(catalog, asset_id=2, path="/library/b.jpg")
    updated = untag_many(catalog, FakeClock(), UntagRequest(tags=("x",)))
    assert all(a.metadata.tags == ("y",) for a in updated)


def test_untag_writes_sidecar(tmp_path: Path) -> None:
    media = tmp_path / "a.jpg"
    media.write_bytes(b"x")
    catalog = InMemoryCatalog()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    catalog.seed(
        MediaAsset(
            id=1,
            path=str(media),
            kind=MediaKind.IMAGE,
            metadata=MediaMetadata(tags=("x",)),
            created_at=now,
            updated_at=now,
        ),
    )
    untag_asset(
        catalog,
        FakeClock(),
        UntagRequest(),
        asset_id=1,
        metadata_writer=XmpSidecarWriter(),
    )
    assert (tmp_path / "a.xmp").is_file()


def test_untag_sidecar_oserror_wraps() -> None:
    class Boom:
        def write(self, path: str, metadata: MediaMetadata) -> None:
            del path, metadata
            message = "disk full"
            raise OSError(message)

    catalog = InMemoryCatalog()
    _seed(catalog)
    with pytest.raises(MetadataWriteError, match="failed to write metadata"):
        untag_asset(
            catalog,
            FakeClock(),
            UntagRequest(),
            asset_id=1,
            metadata_writer=Boom(),  # type: ignore[arg-type]
        )
