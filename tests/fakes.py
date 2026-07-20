"""Deterministic fakes for Clock / FileSystem / CatalogStore seams."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import PurePath

from madify.errors import AssetNotFoundError, CatalogError
from madify.models import MediaAsset, MediaKind, MediaMetadata


@dataclass
class FakeClock:
    _now: datetime = field(
        default_factory=lambda: datetime(2026, 7, 19, 12, 0, 0, tzinfo=UTC),
    )

    def now(self) -> datetime:
        return self._now

    def advance(self, **delta: float) -> None:
        self._now = self._now + timedelta(**delta)


@dataclass
class FakeFileSystem:
    """In-memory filesystem: directories and files keyed by normalized path strings."""

    directories: set[str] = field(default_factory=set)
    files: set[str] = field(default_factory=set)
    rename_error: OSError | None = None

    def add_dir(self, path: str) -> None:
        self.directories.add(_norm(path))

    def add_file(self, path: str) -> None:
        path = _norm(path)
        parent = str(PurePath(path).parent)
        if parent not in {".", ""}:
            self.directories.add(parent)
        self.files.add(path)

    def is_directory(self, path: str) -> bool:
        return _norm(path) in self.directories

    def iter_files(self, root: str) -> list[str]:
        root_n = _norm(root)
        prefix = root_n.rstrip("/\\") + "/"
        # also match Windows-style via PurePath parts
        found: list[str] = []
        for path in self.files:
            if path == root_n:
                continue
            if path.startswith(prefix) or _is_under(path, root_n):
                found.append(path)
        return sorted(found)

    def exists(self, path: str) -> bool:
        path = _norm(path)
        return path in self.files or path in self.directories

    def rename(self, source: str, destination: str) -> None:
        if self.rename_error is not None:
            raise self.rename_error
        source = _norm(source)
        destination = _norm(destination)
        if source not in self.files:
            raise FileNotFoundError(source)
        if destination in self.files:
            raise FileExistsError(destination)
        self.files.remove(source)
        parent = str(PurePath(destination).parent)
        if parent not in {".", ""}:
            self.directories.add(parent)
        self.files.add(destination)


@dataclass
class InMemoryCatalog:
    """In-memory CatalogStore for isolated core tests."""

    _assets: dict[int, MediaAsset] = field(default_factory=dict)
    _by_path: dict[str, int] = field(default_factory=dict)
    _next_id: int = 1
    fail_upsert: bool = False

    def get_by_id(self, asset_id: int) -> MediaAsset | None:
        return self._assets.get(asset_id)

    def get_by_path(self, path: str) -> MediaAsset | None:
        asset_id = self._by_path.get(path)
        if asset_id is None:
            return None
        return self._assets.get(asset_id)

    def list_assets(self) -> list[MediaAsset]:
        return [self._assets[i] for i in sorted(self._assets)]

    def upsert_scanned(
        self,
        path: str,
        kind: MediaKind,
        *,
        now: datetime,
    ) -> tuple[MediaAsset, bool]:
        if self.fail_upsert:
            message = f"catalog upsert failed for {path}"
            raise CatalogError(message)
        existing_id = self._by_path.get(path)
        if existing_id is None:
            asset = MediaAsset(
                id=self._next_id,
                path=path,
                kind=kind,
                metadata=MediaMetadata(),
                created_at=now,
                updated_at=now,
            )
            self._assets[asset.id] = asset
            self._by_path[path] = asset.id
            self._next_id += 1
            return asset, True
        old = self._assets[existing_id]
        updated = MediaAsset(
            id=old.id,
            path=old.path,
            kind=kind,
            metadata=old.metadata,
            created_at=old.created_at,
            updated_at=now,
        )
        self._assets[existing_id] = updated
        return updated, False

    def update_metadata(
        self,
        asset_id: int,
        metadata: MediaMetadata,
        *,
        now: datetime,
    ) -> MediaAsset:
        old = self._assets.get(asset_id)
        if old is None:
            message = f"asset not found: id={asset_id}"
            raise AssetNotFoundError(message)
        updated = MediaAsset(
            id=old.id,
            path=old.path,
            kind=old.kind,
            metadata=metadata,
            created_at=old.created_at,
            updated_at=now,
        )
        self._assets[asset_id] = updated
        return updated

    def update_path(
        self,
        asset_id: int,
        new_path: str,
        *,
        now: datetime,
    ) -> MediaAsset:
        old = self._assets.get(asset_id)
        if old is None:
            message = f"asset not found: id={asset_id}"
            raise AssetNotFoundError(message)
        if new_path in self._by_path and self._by_path[new_path] != asset_id:
            message = f"path already catalogued: {new_path}"
            raise CatalogError(message)
        del self._by_path[old.path]
        updated = MediaAsset(
            id=old.id,
            path=new_path,
            kind=old.kind,
            metadata=old.metadata,
            created_at=old.created_at,
            updated_at=now,
        )
        self._assets[asset_id] = updated
        self._by_path[new_path] = asset_id
        return updated

    def seed(self, asset: MediaAsset) -> MediaAsset:
        """Insert a fully formed asset (tests only)."""
        if asset.id in self._assets:
            message = f"duplicate id={asset.id}"
            raise CatalogError(message)
        if asset.path in self._by_path:
            message = f"path already catalogued: {asset.path}"
            raise CatalogError(message)
        self._assets[asset.id] = asset
        self._by_path[asset.path] = asset.id
        self._next_id = max(self._next_id, asset.id + 1)
        return asset


def _norm(path: str) -> str:
    return str(PurePath(path))


def _is_under(path: str, root: str) -> bool:
    try:
        PurePath(path).relative_to(PurePath(root))
    except ValueError:
        return False
    return PurePath(path) != PurePath(root)
