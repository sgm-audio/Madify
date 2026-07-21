# Graph Report - Madify  (2026-07-20)

## Corpus Check
- 35 files · ~9,448 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 383 nodes · 895 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 236 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `701e3b83`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_main_prints_app_name_and_version
- test_cli.py
- README.md
- madify
- __main__.py
- MediaAsset
- errors.py
- models.py
- FileSystem
- CatalogStore
- models.py
- naming.py
- PULL_REQUEST_TEMPLATE.md

## God Nodes (most connected - your core abstractions)
1. `MediaAsset` - 50 edges
2. `InMemoryCatalog` - 43 edges
3. `SqliteCatalog` - 32 edges
4. `MediaMetadata` - 31 edges
5. `FakeClock` - 30 edges
6. `FakeFileSystem` - 26 edges
7. `MediaKind` - 21 edges
8. `CatalogStore` - 21 edges
9. `AssetNotFoundError` - 20 edges
10. `CatalogError` - 20 edges

## Surprising Connections (you probably didn't know these)
- `FakeFileSystem` --uses--> `AssetNotFoundError`  [INFERRED]
  tests/fakes.py → src/madify/errors.py
- `InMemoryCatalog` --uses--> `AssetNotFoundError`  [INFERRED]
  tests/fakes.py → src/madify/errors.py
- `test_rename_missing_id()` --indirect_call--> `AssetNotFoundError`  [INFERRED]
  tests/test_rename_assets.py → src/madify/errors.py
- `test_sqlite_update_metadata_missing_id()` --indirect_call--> `AssetNotFoundError`  [INFERRED]
  tests/test_sqlite_catalog.py → src/madify/errors.py
- `test_sqlite_update_path_missing_id()` --indirect_call--> `AssetNotFoundError`  [INFERRED]
  tests/test_sqlite_catalog.py → src/madify/errors.py

## Import Cycles
- None detected.

## Communities (13 total, 2 thin omitted)

### Community 0 - "test_main_prints_app_name_and_version"
Cohesion: 0.06
Nodes (38): ArgumentParser, CaptureFixture, Namespace, _build_parser(), _cmd_list(), _cmd_rename(), _cmd_scan(), _cmd_search() (+30 more)

### Community 1 - "test_cli.py"
Cohesion: 0.09
Nodes (34): FileSystem, Filesystem operations required by scan and rename., Return True when path exists and is a directory., Return absolute paths of all files under root (recursive)., Return True when path exists., Rename or move a file; raise OSError on failure., _assets_to_rename(), _build_taken_paths() (+26 more)

### Community 2 - "README.md"
Cohesion: 0.06
Nodes (27): [0.1.0] - 2026-07-20, [0.2.0] - 2026-07-20, Added, Added, Changelog, [Unreleased], Attribution, Contributor Covenant Code of Conduct (+19 more)

### Community 5 - "MediaAsset"
Cohesion: 0.09
Nodes (33): Row, CatalogError, Raised when a catalog store operation fails., _iso(), _parse_iso(), datetime, SQLite catalog store adapter.  Implements :class:`~madify.ports.CatalogStore` wi, Insert a blank-metadata row for a newly scanned file. (+25 more)

### Community 6 - "errors.py"
Cohesion: 0.13
Nodes (28): MetadataValidationError, Raised when title, description, or tags fail validation rules., MediaMetadata, User-editable descriptive metadata for an asset.      Attributes:         title:, build_metadata(), normalize_description(), normalize_tags(), normalize_title() (+20 more)

### Community 7 - "models.py"
Cohesion: 0.11
Nodes (28): Exception, MadifyError, Domain and application errors with explicit failure modes.  All expected Madify, Raised when a path is not a supported image, PSD, or video file., Raised when a scan root is missing or not a directory., Base error for expected Madify failures., ScanError, UnsupportedMediaError (+20 more)

### Community 8 - "FileSystem"
Cohesion: 0.08
Nodes (31): MediaAsset, A single catalogued media file with metadata and audit timestamps.      Attribut, CatalogStore, datetime, Return the current timezone-aware UTC timestamp., Persistent catalog of media assets and metadata., Load one asset by id, or None., Load one asset by absolute path, or None. (+23 more)

### Community 9 - "CatalogStore"
Cohesion: 0.10
Nodes (37): AssetNotFoundError, MetadataWriteError, Raised when a requested catalog asset does not exist or is ambiguous., Raised when writing file/sidecar metadata fails after a catalog update., Partial metadata update; ``None`` fields leave the existing value.      At least, TagRequest, Apply title, description, and tags to a catalogued asset.  Resolves the target b, Update metadata for one asset identified by id or path.      Args:         catal (+29 more)

### Community 10 - "models.py"
Cohesion: 0.13
Nodes (16): Enum, Protocol, MediaKind, Core domain types for catalogued media assets.  These dataclasses are pure value, Coarse media classification used for cataloguing and reporting., Outcome of scanning a directory into the catalog.      Attributes:         added, Outcome of a rename pass.      Attributes:         renamed: Assets whose on-disk, RenameResult (+8 more)

### Community 11 - "naming.py"
Cohesion: 0.13
Nodes (26): Raised when a file cannot be renamed (missing title, collision, FS)., RenameError, allocate_unique_path(), proposed_filename(), proposed_path(), Pure filename construction for metadata-driven renames.  Stems are derived from, Turn a title into a filesystem-safe stem (no extension).      Args:         titl, Return ``{sanitized_title}{lowercased_suffix}`` for ``asset``.      Args: (+18 more)

### Community 12 - "PULL_REQUEST_TEMPLATE.md"
Cohesion: 0.50
Nodes (3): Checklist, Summary, Test plan

## Knowledge Gaps
- **23 isolated node(s):** `madify`, `Summary`, `Test plan`, `Checklist`, `[Unreleased]` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MediaAsset` connect `FileSystem` to `test_main_prints_app_name_and_version`, `test_cli.py`, `MediaAsset`, `CatalogStore`, `models.py`, `naming.py`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Why does `SqliteCatalog` connect `MediaAsset` to `test_main_prints_app_name_and_version`, `errors.py`, `FileSystem`, `CatalogStore`, `models.py`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `MediaMetadata` connect `errors.py` to `test_cli.py`, `MediaAsset`, `FileSystem`, `CatalogStore`, `models.py`, `naming.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `MediaAsset` (e.g. with `CatalogStore` and `Clock`) actually correct?**
  _`MediaAsset` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `InMemoryCatalog` (e.g. with `AssetNotFoundError` and `CatalogError`) actually correct?**
  _`InMemoryCatalog` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `SqliteCatalog` (e.g. with `AssetNotFoundError` and `CatalogError`) actually correct?**
  _`SqliteCatalog` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `MediaMetadata` (e.g. with `CatalogStore` and `Clock`) actually correct?**
  _`MediaMetadata` has 20 INFERRED edges - model-reasoned connections that need verification._