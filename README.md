# Madify

[![CI](https://github.com/scottmills306/Madify/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/scottmills306/Madify/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Madify is a local CLI that catalogues photo, PSD, and video files in SQLite, lets you set titles/descriptions/tags, and renames files from those titles. Metadata lives in the catalog today (file embed/sidecars are planned); the core stays free of direct filesystem/DB/clock access so it stays unit-testable.

## Features

- Recursive **scan** of a directory into a SQLite catalog (images, Photoshop `.psd`/`.psb`, common video)
- **Tag** assets by id or path (title, description, repeatable tags)
- **Rename** files from sanitized titles (`Clip One` → `Clip_One.jpg`), with `_2`, `_3`, … on collisions
- Zero runtime dependencies (stdlib `sqlite3` + `pathlib`)
- Injectable clock / filesystem / catalog ports for deterministic tests

## Install

Requires **Python ≥ 3.12** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/scottmills306/Madify.git
cd Madify
uv sync --group dev
```

```text
Resolved 13 packages in 0.89ms
Checked 13 packages in 1ms
```

```bash
uv run madify
```

```text
Madify 0.1.0
```
## Quickstart

Commands below were run on Windows with a temp media folder and a catalog **outside** that folder (so the `.sqlite` file is not counted as a skipped scan path).

```bash
# Prepare a demo library (PowerShell)
$demo = Join-Path $env:TEMP "madify-docs-qs"
$dbdir = Join-Path $env:TEMP "madify-docs-db"
New-Item -ItemType Directory -Path $demo, $dbdir -Force | Out-Null
Set-Content "$demo\a.jpg" "x"
Set-Content "$demo\b.psd" "x"
Set-Content "$demo\c.mp4" "x"
Set-Content "$demo\readme.txt" "skip"
$db = Join-Path $dbdir "catalog.sqlite"
```

**Version**

```bash
uv run madify
```

```text
Madify 0.1.0
```

**Scan**

```bash
uv run madify --db $db scan $demo
```

```text
scan complete: added=3 updated=0 skipped=1
  + id=1 [image] C:\Users\scott\AppData\Local\Temp\madify-docs-qs\a.jpg
  + id=2 [psd] C:\Users\scott\AppData\Local\Temp\madify-docs-qs\b.psd
  + id=3 [video] C:\Users\scott\AppData\Local\Temp\madify-docs-qs\c.mp4
```

**Tag**

```bash
uv run madify --db $db tag --id 1 --title "Clip One" --description "demo shot" --tag demo --tag photo
```

```text
tagged id=1 title='Clip One' description='demo shot' tags=[demo,photo]
```

**Rename**

```bash
uv run madify --db $db rename --id 1
```

```text
rename complete: renamed=1 unchanged=0
  -> id=1 C:\Users\scott\AppData\Local\Temp\madify-docs-qs\Clip_One.jpg
```

After rename, `$demo` contained: `b.psd`, `c.mp4`, `Clip_One.jpg`, `readme.txt`.

**Help**

```bash
uv run madify --help
```

```text
usage: madify [-h] [--db DB] {scan,tag,rename} ...

Photo cataloguer and metadata assistant.

positional arguments:
  {scan,tag,rename}
    scan             Scan a directory into the catalog
    tag              Set title, description, and/or tags
    rename           Rename files from their catalog titles

options:
  -h, --help         show this help message and exit
  --db DB            SQLite catalog path (default: madify.sqlite)
```

Global option `--db` defaults to `madify.sqlite` in the current working directory.

## Architecture

Core use cases take narrow ports (`Clock`, `FileSystem`, `CatalogStore`). Adapters implement those ports for production; tests inject fakes.

| Module | Role |
|--------|------|
| `madify/__init__.py` | Package version + CLI entry (`main`) |
| `madify/__main__.py` | `python -m madify` |
| `madify/cli.py` | Argparse wiring for `scan` / `tag` / `rename` |
| `madify/models.py` | Domain value types (`MediaAsset`, results, `TagRequest`) |
| `madify/errors.py` | Explicit domain/application error types |
| `madify/media_kinds.py` | Extension → image / PSD / video |
| `madify/tagging.py` | Normalize/validate title, description, tags |
| `madify/naming.py` | Title → safe filename + collision allocation |
| `madify/ports.py` | `Clock` / `FileSystem` / `CatalogStore` protocols |
| `madify/scan.py` | Scan use case |
| `madify/tag_asset.py` | Tag use case |
| `madify/rename_assets.py` | Rename use case |
| `madify/sqlite_catalog.py` | SQLite `CatalogStore` adapter |
| `madify/local_fs.py` | Local filesystem adapter |
| `madify/system_clock.py` | UTC system clock adapter |

## Development

```bash
uv sync --group dev
uv build
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run pytest -q --cov=madify --cov-report=term-missing
uv run pdoc madify -d google -o docs/api
```

Verified (this checkout):

```text
Building source distribution (uv build backend)...
Building wheel from source distribution (uv build backend)...
Successfully built dist\madify-0.1.0.tar.gz
Successfully built dist\madify-0.1.0-py3-none-any.whl
```

```text
All checks passed!
24 files already formatted
......................................................................   [100%]
70 passed in 0.31s
```

```text
# uv run pdoc madify -d google -o docs/api
# exit code 0, no warnings printed; writes docs/api/index.html and module pages
```

API HTML lands in `docs/api/` (gitignored generated output).

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Scott Mills.

## Appendix: Supported extensions

Classification is **extension-only** (case-insensitive). Anything else is skipped on scan.

| Kind | Extensions |
|------|------------|
| **Image** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.tif`, `.tiff`, `.bmp`, `.heic`, `.heif`, `.raw`, `.cr2`, `.nef`, `.arw`, `.dng`, `.orf`, `.rw2` |
| **Photoshop** | `.psd`, `.psb` |
| **Video** | `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.m4v`, `.wmv`, `.mpg`, `.mpeg`, `.3gp` |
