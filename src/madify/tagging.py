"""Validate and normalize titles, descriptions, and tags."""

from __future__ import annotations

from madify.errors import MetadataValidationError
from madify.models import MediaMetadata

_MAX_TITLE_LEN = 200
_MAX_DESCRIPTION_LEN = 4000
_MAX_TAG_LEN = 64
_MAX_TAG_COUNT = 50


def normalize_title(title: str) -> str:
    cleaned = " ".join(title.split())
    if len(cleaned) > _MAX_TITLE_LEN:
        message = f"title exceeds {_MAX_TITLE_LEN} characters"
        raise MetadataValidationError(message)
    return cleaned


def normalize_description(description: str) -> str:
    cleaned = description.strip()
    if len(cleaned) > _MAX_DESCRIPTION_LEN:
        message = f"description exceeds {_MAX_DESCRIPTION_LEN} characters"
        raise MetadataValidationError(message)
    return cleaned


def normalize_tags(tags: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    if len(tags) > _MAX_TAG_COUNT:
        message = f"tag count exceeds {_MAX_TAG_COUNT}"
        raise MetadataValidationError(message)
    seen: dict[str, str] = {}
    for raw in tags:
        tag = " ".join(raw.split())
        if not tag:
            message = "tags must be non-empty"
            raise MetadataValidationError(message)
        if len(tag) > _MAX_TAG_LEN:
            message = f"tag exceeds {_MAX_TAG_LEN} characters: {tag!r}"
            raise MetadataValidationError(message)
        key = tag.casefold()
        if key not in seen:
            seen[key] = tag
    return tuple(seen.values())


def build_metadata(
    *,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    base: MediaMetadata | None = None,
) -> MediaMetadata:
    current = base or MediaMetadata()
    if title is None and description is None and tags is None:
        message = "provide at least one of title, description, or tags"
        raise MetadataValidationError(message)
    new_title = current.title if title is None else normalize_title(title)
    new_description = (
        current.description
        if description is None
        else normalize_description(description)
    )
    new_tags = current.tags if tags is None else normalize_tags(tags)
    return MediaMetadata(
        title=new_title,
        description=new_description,
        tags=new_tags,
    )
