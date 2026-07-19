from __future__ import annotations

import sys
from importlib.metadata import version

from madify.cli import run_cli

__version__ = version("madify")


def main(argv: list[str] | None = None) -> None:
    """CLI entry. No args / empty argv prints version; otherwise runs commands."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(f"Madify {__version__}")
        return
    raise SystemExit(run_cli(argv))
