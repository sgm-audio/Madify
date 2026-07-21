# Contributing to Madify

## Setup

```bash
uv sync --group dev
uv run pre-commit install
```

## Before opening a PR

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest -q --cov=madify --cov-report=term-missing
```

Follow the PR template checklist. Be kind — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Questions and ideas (not bugs or concrete feature specs) belong in
[Discussions](https://github.com/sgm-audio/Madify/discussions).
