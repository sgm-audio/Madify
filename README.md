# Madify

[![CI](https://github.com/sgm-audio/Madify/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/sgm-audio/Madify/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/sgm-audio/Madify)](https://github.com/sgm-audio/Madify/releases/latest)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-%E2%89%A585%25-brightgreen)](https://github.com/sgm-audio/Madify/actions/workflows/ci.yml)
[![Discussions](https://img.shields.io/badge/discussions-join-blue?logo=github)](https://github.com/sgm-audio/Madify/discussions)
[![Sponsor](https://img.shields.io/github/sponsors/sgm-audio?style=flat&logo=GitHub-Sponsors)](https://github.com/sponsors/sgm-audio)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Madify is a local CLI that catalogues photo, PSD, and video files in SQLite, lets you set titles/descriptions/tags, and renames files from those titles. On `tag`, it also writes an **XMP sidecar** next to the media file (catalog stays source of truth). The core never touches the filesystem, database, or clock directly — those are injected ports so unit tests stay deterministic.

## Features

- Recursive **scan** into SQLite (images, Photoshop `.psd`/`.psb`, common video)
- **Tag** by id or path — tags **merge** by default; `--replace-tags` replaces the set
- **XMP sidecar** write-back on tag (`--no-sidecar` to skip)
- **List** / **search** the catalog
- **Rename** from sanitized titles (`Clip One` → `Clip_One.jpg`), collisions → `_2`, `_3`, …
- Zero runtime dependencies (stdlib only)
- Injectable Clock / FileSystem / CatalogStore / MetadataWriter ports

## Install

Requires **Python ≥ 3.12** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/sgm-audio/Madify.git
cd Madify
uv sync --group dev
uv run madify
```

```text
Madify 0.2.1
```

After PyPI trusted publishing is configured (see below):

```bash
uv tool install madify
# or: pip install madify
```

## Quickstart

The catalog is stored at `./madify.sqlite` (override with `--db`). Commands
default to the **current folder**, so the most common workflow is:

```bash
cd /your/photos
madify scan                  # scan the current folder
madify tag --all --auto      # auto-title from filename + add extension tag
madify tag --all --tag archive --tag 2026
madify list                  # see what got catalogued
madify rename --yes          # rename files from their titles
```

That's it. No `uv run`, no `--db`, no paths to type.

## Install

Pick one:

```bash
# A) use the venv already in this repo
.venv\Scripts\madify.exe

# B) install as a tool (then `madify` is on your PATH)
uv tool install .

# C) dev install from source
uv sync --group dev
uv run madify
```

## Commands

| Command | Purpose |
|---------|---------|
| `madify scan [dir]` | Upsert supported media (default: current folder) |
| `madify tag --id N \| --path P` | Set title/description/tags (+ XMP sidecar) |
| `madify tag --all [--auto] [--title T] [--tag X]` | Apply to every asset |
| `madify tag --all --kind image` | Apply to images only |
| `madify untag --all [--tag X] [--title] [--description]` | Remove tags |
| `madify rename [--id N] [--yes]` | Rename from titles (previews unless `--yes`) |
| `madify list` | List all assets |
| `madify search [--query Q] [--tag T]` | Filter assets |

Global: `--db PATH` (default `madify.sqlite` in cwd).

> Keep the `.sqlite` **outside** the media folder you scan, or the catalog
> file itself gets treated as media on subsequent scans.

## Safety

`rename` moves files on disk, so it **previews by default** and changes
nothing until you pass `--yes`:

```bash
madify rename              # dry-run: print the plan, touch nothing
madify rename --dry-run    # same, explicit
madify rename --yes        # actually move files (and sibling .xmp sidecars)
```

`tag`/`untag` only ever create or overwrite the `.xmp` sidecar next to the
media file (never the media itself); pass `--no-sidecar` to skip.

## Maturity

Madify is **beta software**, not production software. What is verified:

- Clean `uv tool install` / wheel install on Python 3.12 (CI-tested); 3.13 is
  supported per `requires-python`/classifiers but not CI-tested.
- The `madify` console entry point, `scan`, `tag`, `untag`, `rename`, `list`,
  and `search` work end-to-end from an installed package.
- SQLite indexing, XMP sidecar write-back, deterministic rename/collision
  handling, and Windows/Unicode path handling are unit-tested (≥85% coverage).

What is **not** yet verified and should not be assumed:

- No PyPI release exists yet (trusted publishing is configured but unclaimed).
- `rename --yes` has not been exercised against a large, real media library;
  back up files before bulk-renaming.
- XMP sidecars are written with a stdlib XML writer; they have not been
  validated in Lightroom/Photoshop.
- Classification is extension-only; corrupt media bytes are catalogued, not
  detected.

## Architecture

| Module | Role |
|--------|------|
| `cli.py` | Argparse wiring |
| `models.py` / `errors.py` | Domain types and errors |
| `media_kinds.py` | Extension → image / PSD / video |
| `tagging.py` | Normalize/validate; tag merge/replace |
| `naming.py` | Title → filename + collisions |
| `ports.py` | Clock / FS / Catalog / MetadataWriter protocols |
| `scan.py` / `tag_asset.py` / `rename_assets.py` | Use cases |
| `query.py` | List / search filters |
| `xmp_sidecar.py` | XMP sidecar writer |
| `sqlite_catalog.py` / `local_fs.py` / `system_clock.py` | Adapters |

## Development

```bash
uv sync --group dev
uv run pre-commit install
uv build
uv run ruff check .
uv run ruff format --check .
uv run pytest -q --cov=madify --cov-report=term-missing
uv run pdoc madify -d google -o docs/api
```

API HTML lands in `docs/api/` (gitignored).

See [CHANGELOG.md](CHANGELOG.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

### PyPI trusted publishing (one-time, manual)

1. Create a PyPI project named `madify` (or claim the name).
2. On PyPI → Publishing → add a trusted publisher:
   - Owner: `sgm-audio`
   - Repository: `Madify`
   - Workflow: `publish.yml`
   - Environment: `pypi`
3. On GitHub → Settings → Environments → create **`pypi`** (optional protection rules).
4. Publish a GitHub Release — the Publish workflow uploads wheels via OIDC (no API token).

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Scott Mills.

## Appendix: Supported extensions

Classification is **extension-only** (case-insensitive). Anything else is skipped on scan.

| Kind | Extensions |
|------|------------|
| **Image** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.tif`, `.tiff`, `.bmp`, `.heic`, `.heif`, `.raw`, `.cr2`, `.nef`, `.arw`, `.dng`, `.orf`, `.rw2` |
| **Photoshop** | `.psd`, `.psb` |
| **Video** | `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.m4v`, `.wmv`, `.mpg`, `.mpeg`, `.3gp` |
