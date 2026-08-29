import contextlib
import io
import subprocess
import sys
from importlib.metadata import entry_points, version
from pathlib import Path

import pytest

from madify import __version__, main
from madify.cli import run_cli


def test_version_matches_package_metadata() -> None:
    assert __version__ == version("madify")
    assert __version__ == "0.2.1"


def test_main_prints_app_name_and_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    main([])
    captured = capsys.readouterr()
    assert captured.out == f"Madify {__version__}\n"
    assert captured.err == ""


def test_module_entry_prints_app_name_and_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "madify"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout == f"Madify {__version__}\n"
    assert result.stderr == ""


def test_console_script_entry_point_registered() -> None:
    """The installed ``madify`` console script resolves to ``madify:main``."""
    scripts = {ep.name: ep.value for ep in entry_points(group="console_scripts")}
    assert scripts["madify"] == "madify:main"


def test_run_cli_scan_list_end_to_end(tmp_path: Path) -> None:
    """Scan + list against real SQLite/FS adapters (no fakes)."""
    media = tmp_path / "a.jpg"
    media.write_bytes(b"fake")
    db = tmp_path / "catalog.sqlite"

    assert run_cli(["--db", str(db), "scan", str(tmp_path)]) == 0

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = run_cli(["--db", str(db), "list"])
    assert code == 0
    assert media.name in out.getvalue()


def test_run_cli_scan_missing_root_returns_1(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    db = tmp_path / "catalog.sqlite"
    code = run_cli(["--db", str(db), "scan", str(tmp_path / "missing")])
    captured = capsys.readouterr()
    assert code == 1
    assert "not a directory" in captured.err
