# AGENTS.md — Madify

Python ≥3.12 CLI (src-layout) that catalogues media into SQLite and writes XMP
sidecars. **Zero runtime dependencies** (`dependencies = []` in pyproject.toml).
Uses [uv](https://docs.astral.sh/uv/) exclusively — never `pip`.

## Commands

```bash
uv sync --group dev              # install dev deps (group, not extras)
uv run ruff format --check .     # hard CI gate — always run
uv run ruff check .
uv run pytest -q --cov=madify --cov-report=term-missing
uv run pytest tests/test_tagging.py -k tag_many   # single test
uv run pre-commit run --all-files
uv build                         # build (uv_build backend)
uv run pdoc madify -d google -o docs/api   # API docs (gitignored)
```

Order matters before claiming done: `format --check` → `check` → `pytest`.

## Ruff is strict — this will bite you

- `select = ["ALL"]`; only `COM812`/`ISC001` ignored.
- **Google pydocstyle**: every public function needs a docstring with `Args:`/`Returns:`/`Raises:` (check `tag_many` in `src/madify/tag_asset.py`).
- `T201` (`print`) banned except `__init__.py`/`__main__.py`/`cli.py`.
- Double quotes, LF line endings (`.editorconfig` too — 4-space indent; 2-space for toml/yml/json/md).
- Tests are exempt from `D S101 S603 INP001 SLF001 PLR2004` (per-file-ignores); everything else still applies to them.

## Coverage gate

`fail_under = 85`; `branch = false`. `cli.py`, `__main__.py`, `system_clock.py`,
`local_fs.py`, `ports.py` are **omitted** — write tests against the fakes instead.

## Architecture (hexagonal / ports & adapters)

Core use cases — `scan.py`, `tag_asset.py`, `untag.py`, `rename_assets.py`,
`query.py` — are pure: no filesystem, DB, or clock access. `Clock`/`FileSystem`/
`CatalogStore`/`MetadataWriter` protocols live in `ports.py` and are injected.
`cli.py` wires the production adapters (`sqlite_catalog.py`, `local_fs.py`,
`system_clock.py`, `xmp_sidecar.py`).

- Tests use `tests/fakes.py` (`FakeClock`, `FakeFileSystem`, `InMemoryCatalog`) — never the real adapters.
- **New features must follow this pattern**: add behavior to a use-case function taking injected ports, not to an adapter or `cli.py`.
- Sentry (`sentry_sdk`) is optional and lazily imported in `__init__.py` behind `SENTRY_DSN` — keep it that way; no runtime deps allowed.

## Behavioral gotchas

- `tag` writes an **XMP sidecar** next to the media file (`--no-sidecar` skips). `rename` also renames sibling `.xmp` files, skipping when the target already exists.
- Keep `madify.sqlite` **outside** the folder you scan, or the catalog file itself gets catalogued as media.
- Default catalog is `madify.sqlite` in cwd; commands default to the current folder.
- Version lives only in `pyproject.toml`; `__version__` reads it via `importlib.metadata` — bump there (and in `CHANGELOG.md`, Keep a Changelog + semver). Publishing is trusted-publishing on GitHub Release (workflow `publish.yml`, env `pypi`, no tokens).

## Repo state / gotchas

- `Madify-sentry-fix/` is a **stale, untracked nested clone** (own `.git`/`.venv`) — ignore it; glob/grep will surface duplicate source from it. The real root is this directory.
- `graphify-out/` is a knowledge graph. For codebase questions prefer `graphify query "…"` over raw grep; dirty graph files are expected. After modifying code run `graphify update .` (see global `~/.claude/CLAUDE.md`).
- `docs/api/`, `dist/`, `.venv/`, `*.sqlite` are gitignored — don't commit them.
- Working tree may carry uncommitted WIP (e.g. `tag --all/--auto`, `untag`); don't sweep unrelated changes into a commit.
