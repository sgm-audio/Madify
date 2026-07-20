"""Local filesystem adapter for :class:`~madify.ports.FileSystem`."""

from __future__ import annotations

from pathlib import Path


class LocalFileSystem:
    """Production filesystem backed by :mod:`pathlib`."""

    def is_directory(self, path: str) -> bool:
        """Return True when ``path`` exists and is a directory."""
        return Path(path).is_dir()

    def iter_files(self, root: str) -> list[str]:
        """Return sorted absolute paths of all files under ``root``."""
        base = Path(root)
        return sorted(str(p.resolve()) for p in base.rglob("*") if p.is_file())

    def exists(self, path: str) -> bool:
        """Return True when ``path`` exists."""
        return Path(path).exists()

    def rename(self, source: str, destination: str) -> None:
        """Rename ``source`` to ``destination``; may raise :class:`OSError`."""
        Path(source).rename(destination)
