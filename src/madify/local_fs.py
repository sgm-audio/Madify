"""Local filesystem adapter."""

from __future__ import annotations

from pathlib import Path


class LocalFileSystem:
    def is_directory(self, path: str) -> bool:
        return Path(path).is_dir()

    def iter_files(self, root: str) -> list[str]:
        base = Path(root)
        return sorted(str(p.resolve()) for p in base.rglob("*") if p.is_file())

    def exists(self, path: str) -> bool:
        return Path(path).exists()

    def rename(self, source: str, destination: str) -> None:
        Path(source).rename(destination)
