"""Validate and normalize titles, descriptions, and tags.

Normalization is pure: no I/O. Empty titles are allowed (assets may be
untitled until the user tags them). Tag lists are casefold-deduped while
preserving the first-seen spelling and order.
"""

from __future__ import annotations

from madify.errors import MetadataValidationError
from madify.models import MediaMetadata

_MAX_TITLE_LEN = 200
_MAX_DESCRIPTION_LEN = 4000
_MAX_TAG_LEN = 64
_MAX_TAG_COUNT = 50


def normalize_title(title: str) -> str:
    """Collapse internal whitespace and enforce the title length limit.

    Args:
        title: Raw title string.

    Returns:
        Cleaned title (may be empty).

    Raises:
        MetadataValidationError: Title exceeds ``_MAX_TITLE_LEN`` characters.
    """
    cleaned = " ".join(title.split())
    if len(cleaned) > _MAX_TITLE_LEN:
        message = f"title exceeds {_MAX_TITLE_LEN} characters"
        raise MetadataValidationError(message)
    return cleaned


def normalize_description(description: str) -> str:
    """Strip leading/trailing whitespace; keep internal newlines.

    Args:
        description: Raw description string.

    Returns:
        Cleaned description (may be empty).

    Raises:
        MetadataValidationError: Description exceeds the length limit.
    """
    cleaned = description.strip()
    if len(cleaned) > _MAX_DESCRIPTION_LEN:
        message = f"description exceeds {_MAX_DESCRIPTION_LEN} characters"
        raise MetadataValidationError(message)
    return cleaned


def normalize_tags(tags: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    """Validate, collapse whitespace, and dedupe tags case-insensitively.

    Args:
        tags: Candidate tag strings.

    Returns:
        Ordered unique tags (first spelling wins per casefold key).

    Raises:
        MetadataValidationError: Empty tag, oversize tag, or too many tags.
    """
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
    """Merge a partial update onto ``base`` (or empty metadata).

    Args:
        title: New title, or ``None`` to keep ``base.title``.
        description: New description, or ``None`` to keep ``base.description``.
        tags: Replacement tag list, or ``None`` to keep ``base.tags``.
        base: Existing metadata; defaults to empty fields.

    Returns:
        A new :class:`~madify.models.MediaMetadata` instance.

    Raises:
        MetadataValidationError: No fields provided, or a field fails
            normalization.
    """
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
