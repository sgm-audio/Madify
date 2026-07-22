# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-07-22

### Fixed

- `rename` also renames sibling `.xmp` sidecars with the media file (skips when
  the target `.xmp` already exists so nothing is clobbered)

## [0.2.0] - 2026-07-20

### Added

- `madify list` and `madify search` commands
- Tag merge by default; `--replace-tags` for full replacement
- XMP sidecar metadata write-back on `tag` (`--no-sidecar` to skip)
- Repo hygiene: Dependabot, PR/issue templates, CODEOWNERS, SECURITY, Code of Conduct
- Pre-commit hooks, coverage gate in CI, PyPI publish workflow on release
- Project URLs / classifiers for PyPI

## [0.1.0] - 2026-07-20

### Added

- Initial public release: `scan`, `tag`, `rename` with SQLite catalog
- Support for common images, Photoshop `.psd`/`.psb`, and video extensions
- Injectable Clock / FileSystem / CatalogStore ports and unit tests
- GitHub Actions CI (format, lint, test)

[Unreleased]: https://github.com/sgm-audio/Madify/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/sgm-audio/Madify/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/sgm-audio/Madify/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/sgm-audio/Madify/releases/tag/v0.1.0
