"""SQLite catalog store adapter.

Implements :class:`~madify.ports.CatalogStore` with the stdlib ``sqlite3``
module. Tags are stored as a JSON array string. Corrupt ``tags_json`` values
raise :class:`~madify.errors.CatalogError` on read.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from madify.errors import AssetNotFoundError, CatalogError
from madify.models import MediaAsset, MediaKind, MediaMetadata

_SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    tags_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


class SqliteCatalog:
    """File-backed SQLite implementation of the catalog port.

    Args:
        db_path: Path to the SQLite database file. Parent directories are
            created when needed.
    """

    def __init__(self, db_path: str) -> None:
        """Open (or create) the database and ensure the schema exists."""
        self._db_path = db_path
        parent = Path(db_path).parent
        if str(parent) not in {"", "."}:
            parent.mkdir(parents=True, exist_ok=True)
        try:
            self._conn = sqlite3.connect(db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.executescript(_SCHEMA)
            self._conn.commit()
        except sqlite3.Error as exc:
            message = f"failed to open catalog {db_path}: {exc}"
            raise CatalogError(message) from exc

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        self._conn.close()

    def get_by_id(self, asset_id: int) -> MediaAsset | None:
        """Load one asset by primary key, or ``None`` if missing."""
        row = self._conn.execute(
            "SELECT * FROM assets WHERE id = ?",
            (asset_id,),
        ).fetchone()
        return None if row is None else self._row_to_asset(row)

    def get_by_path(self, path: str) -> MediaAsset | None:
        """Load one asset by absolute path, or ``None`` if missing."""
        row = self._conn.execute(
            "SELECT * FROM assets WHERE path = ?",
            (path,),
        ).fetchone()
        return None if row is None else self._row_to_asset(row)

    def list_assets(self) -> list[MediaAsset]:
        """Return all assets ordered by ascending id."""
        rows = self._conn.execute("SELECT * FROM assets ORDER BY id ASC").fetchall()
        return [self._row_to_asset(row) for row in rows]

    def upsert_scanned(
        self,
        path: str,
        kind: MediaKind,
        *,
        now: datetime,
    ) -> tuple[MediaAsset, bool]:
        """Insert a new scanned path or refresh kind/timestamp on an existing one.

        Args:
            path: Absolute media path.
            kind: Classified media kind.
            now: Timestamp for created/updated fields.

        Returns:
            ``(asset, created)`` where ``created`` is True on insert.

        Raises:
            CatalogError: Underlying SQLite failure.
        """
        existing = self.get_by_path(path)
        stamp = _iso(now)
        try:
            if existing is None:
                return self._insert_scanned(path, kind, stamp), True
            return self._refresh_scanned(existing, kind, stamp), False
        except sqlite3.Error as exc:
            message = f"catalog upsert failed for {path}: {exc}"
            raise CatalogError(message) from exc

    def _insert_scanned(
        self,
        path: str,
        kind: MediaKind,
        stamp: str,
    ) -> MediaAsset:
        """Insert a blank-metadata row for a newly scanned file."""
        cur = self._conn.execute(
            """
            INSERT INTO assets (
                path, kind, title, description, tags_json,
                created_at, updated_at
            ) VALUES (?, ?, '', '', '[]', ?, ?)
            """,
            (path, kind.value, stamp, stamp),
        )
        self._conn.commit()
        asset_id = int(cur.lastrowid)
        asset = self.get_by_id(asset_id)
        if asset is None:
            message = f"failed to load inserted asset for {path}"
            raise CatalogError(message)
        return asset

    def _refresh_scanned(
        self,
        existing: MediaAsset,
        kind: MediaKind,
        stamp: str,
    ) -> MediaAsset:
        """Update kind and ``updated_at`` for an already-catalogued path."""
        self._conn.execute(
            """
            UPDATE assets
            SET kind = ?, updated_at = ?
            WHERE id = ?
            """,
            (kind.value, stamp, existing.id),
        )
        self._conn.commit()
        asset = self.get_by_id(existing.id)
        if asset is None:
            message = f"failed to load updated asset id={existing.id}"
            raise CatalogError(message)
        return asset

    def update_metadata(
        self,
        asset_id: int,
        metadata: MediaMetadata,
        *,
        now: datetime,
    ) -> MediaAsset:
        """Replace title, description, and tags for ``asset_id``.

        Raises:
            AssetNotFoundError: No row with that id.
            CatalogError: SQLite failure.
        """
        try:
            cur = self._conn.execute(
                """
                UPDATE assets
                SET title = ?, description = ?, tags_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    metadata.title,
                    metadata.description,
                    json.dumps(list(metadata.tags)),
                    _iso(now),
                    asset_id,
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            message = f"catalog metadata update failed for id={asset_id}: {exc}"
            raise CatalogError(message) from exc
        if cur.rowcount != 1:
            message = f"asset not found: id={asset_id}"
            raise AssetNotFoundError(message)
        asset = self.get_by_id(asset_id)
        if asset is None:
            message = f"asset not found after update: id={asset_id}"
            raise AssetNotFoundError(message)
        return asset

    def update_path(
        self,
        asset_id: int,
        new_path: str,
        *,
        now: datetime,
    ) -> MediaAsset:
        """Update the stored path after a successful filesystem rename.

        Raises:
            AssetNotFoundError: No row with that id.
            CatalogError: Path uniqueness conflict or other SQLite failure.
        """
        try:
            cur = self._conn.execute(
                """
                UPDATE assets
                SET path = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_path, _iso(now), asset_id),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as exc:
            message = f"path already catalogued: {new_path}"
            raise CatalogError(message) from exc
        except sqlite3.Error as exc:
            message = f"catalog path update failed for id={asset_id}: {exc}"
            raise CatalogError(message) from exc
        if cur.rowcount != 1:
            message = f"asset not found: id={asset_id}"
            raise AssetNotFoundError(message)
        asset = self.get_by_id(asset_id)
        if asset is None:
            message = f"asset not found after path update: id={asset_id}"
            raise AssetNotFoundError(message)
        return asset

    @staticmethod
    def _row_to_asset(row: sqlite3.Row) -> MediaAsset:
        """Map a SQLite row to a :class:`~madify.models.MediaAsset`."""
        try:
            raw_tags = json.loads(row["tags_json"])
        except json.JSONDecodeError as exc:
            message = f"corrupt tags_json for asset id={row['id']}"
            raise CatalogError(message) from exc
        if not isinstance(raw_tags, list) or not all(
            isinstance(tag, str) for tag in raw_tags
        ):
            message = f"corrupt tags_json for asset id={row['id']}"
            raise CatalogError(message)
        tags = tuple(raw_tags)
        return MediaAsset(
            id=int(row["id"]),
            path=str(row["path"]),
            kind=MediaKind(str(row["kind"])),
            metadata=MediaMetadata(
                title=str(row["title"]),
                description=str(row["description"]),
                tags=tags,
            ),
            created_at=_parse_iso(str(row["created_at"])),
            updated_at=_parse_iso(str(row["updated_at"])),
        )


def _iso(value: datetime) -> str:
    """Serialize a datetime to ISO-8601 text for SQLite storage."""
    return value.isoformat()


def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp from the catalog."""
    return datetime.fromisoformat(value)
