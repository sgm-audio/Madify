import subprocess
import sys
from importlib.metadata import version

import pytest

from madify import __version__, main


def test_version_matches_package_metadata() -> None:
    assert __version__ == version("madify")
    assert __version__ == "0.2.0"


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
