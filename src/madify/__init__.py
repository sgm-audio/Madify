"""Madify — photo cataloguer and metadata assistant.

Public entry point is :func:`main`. With no arguments it prints the version;
otherwise it delegates to :func:`madify.cli.run_cli`.
"""

from __future__ import annotations

import os
import sys
from importlib.metadata import version

from madify.cli import run_cli

__version__ = version("madify")


def _init_sentry() -> None:
    """Optional error reporting when SENTRY_DSN is set."""
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        return
    try:
        import sentry_sdk
    except ImportError:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=os.environ.get("ENVIRONMENT", "development"),
        traces_sample_rate=0.0,
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entry. Empty argv prints version; otherwise runs subcommands.

    Args:
        argv: Argument list without the program name. When ``None``, uses
            ``sys.argv[1:]``.
    """
    _init_sentry()
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(f"Madify {__version__}")
        return
    raise SystemExit(run_cli(argv))
