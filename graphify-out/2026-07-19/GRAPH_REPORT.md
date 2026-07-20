# Graph Report - Madify  (2026-07-19)

## Corpus Check
- 18 files · ~2,932 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 140 nodes · 318 edges · 16 communities (9 shown, 7 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 47 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0e9a8a98`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_main_prints_app_name_and_version
- test_cli.py
- README.md
- madify
- MediaAsset
- errors.py
- models.py
- FileSystem
- CatalogStore
- ports.py
- naming.py
- .exists
- .is_directory
- .iter_files
- .rename

## God Nodes (most connected - your core abstractions)
1. `MediaAsset` - 28 edges
2. `SqliteCatalog` - 22 edges
3. `CatalogStore` - 18 edges
4. `FileSystem` - 14 edges
5. `MediaKind` - 13 edges
6. `CatalogError` - 11 edges
7. `_dispatch()` - 10 edges
8. `MadifyError` - 10 edges
9. `Clock` - 10 edges
10. `rename_assets()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `test_main_prints_app_name_and_version()` --calls--> `main()`  [INFERRED]
  tests/test_cli.py → src/madify/__init__.py
- `_dispatch()` --calls--> `MadifyError`  [INFERRED]
  src/madify/cli.py → src/madify/errors.py
- `_cmd_scan()` --calls--> `scan_directory()`  [INFERRED]
  src/madify/cli.py → src/madify/scan.py
- `_cmd_tag()` --calls--> `TagRequest`  [INFERRED]
  src/madify/cli.py → src/madify/models.py
- `_cmd_tag()` --calls--> `tag_asset()`  [INFERRED]
  src/madify/cli.py → src/madify/tag_asset.py

## Import Cycles
- None detected.

## Communities (16 total, 7 thin omitted)

### Community 0 - "test_main_prints_app_name_and_version"
Cohesion: 0.14
Nodes (16): ArgumentParser, Namespace, _build_parser(), _cmd_rename(), _cmd_scan(), _cmd_tag(), _dispatch(), CLI for scan, tag, and rename against a SQLite catalog. (+8 more)

### Community 5 - "MediaAsset"
Cohesion: 0.22
Nodes (13): Row, AssetNotFoundError, CatalogError, Requested catalog asset does not exist., Catalog store operation failed., MediaAsset, MediaKind, _iso() (+5 more)

### Community 6 - "errors.py"
Cohesion: 0.13
Nodes (21): Exception, MadifyError, MetadataValidationError, Domain and application errors with explicit failure modes., Title, description, or tags failed validation., File cannot be renamed (missing title, collision, or filesystem failure)., Scan root is missing or not a directory., Base error for expected Madify failures. (+13 more)

### Community 7 - "models.py"
Cohesion: 0.23
Nodes (10): Enum, classify_media(), extension_of(), is_supported_media(), Classify media files by extension (images, PSD, video)., Core domain types for catalogued media assets., RenameResult, ScanResult (+2 more)

### Community 8 - "FileSystem"
Cohesion: 0.40
Nodes (9): Protocol, Clock, FileSystem, _assets_to_rename(), _build_taken_paths(), _existing_neighbor_paths(), Rename catalogued files from their titles via injected filesystem., rename_assets() (+1 more)

### Community 9 - "CatalogStore"
Cohesion: 0.22
Nodes (6): MediaMetadata, CatalogStore, Load one asset by id, or None., Load one asset by absolute path, or None., Return all assets ordered by id., Replace metadata for an existing asset.

### Community 10 - "ports.py"
Cohesion: 0.22
Nodes (5): datetime, Narrow I/O ports injected into core use cases., Return the current timezone-aware UTC timestamp., Insert or refresh a scanned path. Returns (asset, created)., Update stored path after a successful rename.

### Community 11 - "naming.py"
Cohesion: 0.38
Nodes (6): allocate_unique_path(), proposed_filename(), proposed_path(), Pure filename construction for metadata-driven renames., Pick desired path, or desired stem_2/stem_3… if taken (casefold keys)., sanitize_filename_stem()

## Knowledge Gaps
- **2 isolated node(s):** `madify`, `Madify`
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MediaAsset` connect `MediaAsset` to `errors.py`, `models.py`, `FileSystem`, `CatalogStore`, `ports.py`, `naming.py`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `SqliteCatalog` connect `MediaAsset` to `test_main_prints_app_name_and_version`, `CatalogStore`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `FileSystem` connect `FileSystem` to `MediaAsset`, `models.py`, `CatalogStore`, `ports.py`, `.exists`, `.is_directory`, `.iter_files`, `.rename`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `MediaAsset` (e.g. with `CatalogStore` and `Clock`) actually correct?**
  _`MediaAsset` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SqliteCatalog` (e.g. with `AssetNotFoundError` and `CatalogError`) actually correct?**
  _`SqliteCatalog` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `CatalogStore` (e.g. with `MediaAsset` and `MediaKind`) actually correct?**
  _`CatalogStore` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `FileSystem` (e.g. with `MediaAsset` and `MediaKind`) actually correct?**
  _`FileSystem` has 3 INFERRED edges - model-reasoned connections that need verification._