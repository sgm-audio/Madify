"""System clock adapter for :class:`~madify.ports.Clock`."""

from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Production clock returning timezone-aware UTC timestamps."""

    def now(self) -> datetime:
        """Return ``datetime.now(UTC)``."""
        return datetime.now(UTC)
