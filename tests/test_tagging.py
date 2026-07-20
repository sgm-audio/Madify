"""Tests for metadata validation and normalization."""

from __future__ import annotations

import pytest

from madify.errors import MetadataValidationError
from madify.models import MediaMetadata
from madify.tagging import (
    build_metadata,
    normalize_description,
    normalize_tags,
    normalize_title,
)


def test_normalize_title_collapses_whitespace() -> None:
    assert normalize_title("  Clip   One  ") == "Clip One"


def test_normalize_title_empty_allowed() -> None:
    assert normalize_title("   ") == ""


def test_normalize_title_too_long() -> None:
    with pytest.raises(MetadataValidationError, match="title exceeds"):
        normalize_title("x" * 201)


def test_normalize_description_strips_edges_keeps_internal() -> None:
    assert normalize_description("  line1\n\nline2  ") == "line1\n\nline2"


def test_normalize_description_too_long() -> None:
    with pytest.raises(MetadataValidationError, match="description exceeds"):
        normalize_description("y" * 4001)


def test_normalize_tags_dedupes_casefold_preserves_first() -> None:
    assert normalize_tags(["Demo", "demo", "Other"]) == ("Demo", "Other")


def test_normalize_tags_collapses_inner_whitespace() -> None:
    assert normalize_tags(["  foo   bar  "]) == ("foo bar",)


def test_normalize_tags_rejects_empty() -> None:
    with pytest.raises(MetadataValidationError, match="non-empty"):
        normalize_tags(["ok", "  "])


def test_normalize_tags_rejects_too_long() -> None:
    with pytest.raises(MetadataValidationError, match="tag exceeds"):
        normalize_tags(["z" * 65])


def test_normalize_tags_rejects_too_many() -> None:
    with pytest.raises(MetadataValidationError, match="tag count exceeds"):
        normalize_tags([f"t{i}" for i in range(51)])


def test_build_metadata_requires_at_least_one_field() -> None:
    with pytest.raises(MetadataValidationError, match="at least one"):
        build_metadata()


def test_build_metadata_merges_onto_base() -> None:
    base = MediaMetadata(title="Old", description="keep", tags=("a",))
    result = build_metadata(title="New", tags=["b", "c"], base=base)
    assert result == MediaMetadata(title="New", description="keep", tags=("b", "c"))


def test_build_metadata_partial_description_only() -> None:
    base = MediaMetadata(title="T", description="", tags=("x",))
    result = build_metadata(description="  hi  ", base=base)
    assert result.title == "T"
    assert result.description == "hi"
    assert result.tags == ("x",)
