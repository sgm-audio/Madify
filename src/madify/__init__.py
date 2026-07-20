"""Madify — photo cataloguer and metadata assistant.

Public entry point is :func:`main`. With no arguments it prints the version;
otherwise it delegates to :func:`madify.cli.run_cli`.
"""

from __future__ import annotations

import sys
from importlib.metadata import version

from madify.cli import run_cli

__version__ = version("madify")


def main(argv: list[str] | None = None) -> None:
    """CLI entry. Empty argv prints version; otherwise runs subcommands.

    Args:
        argv: Argument list without the program name. When ``None``, uses
            ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(f"Madify {__version__}")
        return
    raise SystemExit(run_cli(argv))
