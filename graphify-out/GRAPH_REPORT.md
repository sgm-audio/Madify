# Graph Report - Madify  (2026-07-19)

## Corpus Check
- 26 files · ~7,357 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 307 nodes · 752 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 72% EXTRACTED · 28% INFERRED · 0% AMBIGUOUS · INFERRED: 214 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91fa3c90`
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
- naming.py

## God Nodes (most connected - your core abstractions)
1. `MediaAsset` - 42 edges
2. `InMemoryCatalog` - 35 edges
3. `SqliteCatalog` - 30 edges
4. `FakeClock` - 28 edges
5. `FakeFileSystem` - 26 edges
6. `MediaMetadata` - 22 edges
7. `AssetNotFoundError` - 20 edges
8. `CatalogError` - 20 edges
9. `MediaKind` - 20 edges
10. `rename_assets()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `FakeClock` --uses--> `AssetNotFoundError`  [INFERRED]
  tests/fakes.py → src/madify/errors.py
- `FakeFileSystem` --uses--> `AssetNotFoundError`  [INFERRED]
  tests/fakes.py → src/madify/errors.py
- `InMemoryCatalog` --uses--> `AssetNotFoundError`  [INFERRED]
  tests/fakes.py → src/madify/errors.py
- `test_rename_missing_id()` --indirect_call--> `AssetNotFoundError`  [INFERRED]
  tests/test_rename_assets.py → src/madify/errors.py
- `test_sqlite_update_metadata_missing_id()` --indirect_call--> `AssetNotFoundError`  [INFERRED]
  tests/test_sqlite_catalog.py → src/madify/errors.py

## Import Cycles
- None detected.

## Communities (11 total, 2 thin omitted)

### Community 0 - "test_main_prints_app_name_and_version"
Cohesion: 0.07
Nodes (32): ArgumentParser, CaptureFixture, Namespace, _build_parser(), _cmd_rename(), _cmd_scan(), _cmd_tag(), _dispatch() (+24 more)

### Community 1 - "test_cli.py"
Cohesion: 0.11
Nodes (36): _assets_to_rename(), _build_taken_paths(), _existing_neighbor_paths(), Rename catalogued files from their titles via injected filesystem.  Bulk rename, List files in each unique parent directory of ``assets``., Rename one asset or every titled asset in the catalog.      Args:         catalo, Return the asset list for a rename pass., Casefolded set of catalog paths plus on-disk neighbor files. (+28 more)

### Community 2 - "README.md"
Cohesion: 0.25
Nodes (7): Architecture, Development, Features, Install, License, Madify, Quickstart

### Community 5 - "MediaAsset"
Cohesion: 0.09
Nodes (33): Path, Row, CatalogError, Raised when a catalog store operation fails., _iso(), _parse_iso(), datetime, SQLite catalog store adapter.  Implements :class:`~madify.ports.CatalogStore` wi (+25 more)

### Community 6 - "errors.py"
Cohesion: 0.14
Nodes (27): MetadataValidationError, Raised when title, description, or tags fail validation rules., MediaMetadata, User-editable descriptive metadata for an asset.      Attributes:         title:, build_metadata(), normalize_description(), normalize_tags(), normalize_title() (+19 more)

### Community 7 - "models.py"
Cohesion: 0.09
Nodes (32): Enum, Exception, MadifyError, Domain and application errors with explicit failure modes.  All expected Madify, Raised when a path is not a supported image, PSD, or video file., Raised when a scan root is missing or not a directory., Base error for expected Madify failures., ScanError (+24 more)

### Community 8 - "FileSystem"
Cohesion: 0.07
Nodes (23): Protocol, MediaAsset, A single catalogued media file with metadata and audit timestamps.      Attribut, CatalogStore, Clock, FileSystem, datetime, Narrow I/O ports injected into core use cases.  Core modules depend only on thes (+15 more)

### Community 9 - "CatalogStore"
Cohesion: 0.16
Nodes (20): AssetNotFoundError, Raised when a requested catalog asset does not exist or is ambiguous., Partial metadata update; ``None`` fields leave the existing value.      At least, TagRequest, Apply title, description, and tags to a catalogued asset.  Resolves the target b, Update metadata for one asset identified by id or path.      Args:         catal, Load an asset by exactly one of ``asset_id`` or ``path``., _resolve_asset() (+12 more)

### Community 11 - "naming.py"
Cohesion: 0.13
Nodes (26): Raised when a file cannot be renamed (missing title, collision, FS)., RenameError, allocate_unique_path(), proposed_filename(), proposed_path(), Pure filename construction for metadata-driven renames.  Stems are derived from, Turn a title into a filesystem-safe stem (no extension).      Args:         titl, Return ``{sanitized_title}{lowercased_suffix}`` for ``asset``.      Args: (+18 more)

## Knowledge Gaps
- **7 isolated node(s):** `madify`, `Features`, `Install`, `Quickstart`, `Architecture` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MediaAsset` connect `FileSystem` to `test_cli.py`, `MediaAsset`, `models.py`, `CatalogStore`, `naming.py`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `SqliteCatalog` connect `MediaAsset` to `test_main_prints_app_name_and_version`, `errors.py`, `models.py`, `FileSystem`, `CatalogStore`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Why does `MediaMetadata` connect `errors.py` to `test_cli.py`, `MediaAsset`, `models.py`, `FileSystem`, `CatalogStore`, `naming.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `MediaAsset` (e.g. with `CatalogStore` and `Clock`) actually correct?**
  _`MediaAsset` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `InMemoryCatalog` (e.g. with `AssetNotFoundError` and `CatalogError`) actually correct?**
  _`InMemoryCatalog` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `SqliteCatalog` (e.g. with `AssetNotFoundError` and `CatalogError`) actually correct?**
  _`SqliteCatalog` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `FakeClock` (e.g. with `AssetNotFoundError` and `CatalogError`) actually correct?**
  _`FakeClock` has 25 INFERRED edges - model-reasoned connections that need verification._