# Graph Report - Madify  (2026-07-19)

## Corpus Check
- 26 files · ~5,271 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 245 nodes · 690 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 214 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `57d00292`
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
- naming.py

## God Nodes (most connected - your core abstractions)
1. `MediaAsset` - 41 edges
2. `InMemoryCatalog` - 35 edges
3. `SqliteCatalog` - 29 edges
4. `FakeClock` - 28 edges
5. `FakeFileSystem` - 26 edges
6. `MediaMetadata` - 21 edges
7. `AssetNotFoundError` - 20 edges
8. `CatalogError` - 20 edges
9. `MediaKind` - 19 edges
10. `rename_assets()` - 19 edges

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
Cohesion: 0.11
Nodes (18): ArgumentParser, CaptureFixture, Namespace, _build_parser(), _cmd_rename(), _cmd_scan(), _cmd_tag(), _dispatch() (+10 more)

### Community 1 - "test_cli.py"
Cohesion: 0.18
Nodes (23): rename_assets(), FakeClock, FakeFileSystem, InMemoryCatalog, _is_under(), _norm(), Deterministic fakes for Clock / FileSystem / CatalogStore seams., In-memory filesystem: directories and files keyed by normalized path strings. (+15 more)

### Community 5 - "MediaAsset"
Cohesion: 0.12
Nodes (24): Path, Row, CatalogError, Catalog store operation failed., MediaAsset, MediaKind, Insert or refresh a scanned path. Returns (asset, created)., _iso() (+16 more)

### Community 6 - "errors.py"
Cohesion: 0.18
Nodes (22): MetadataValidationError, Title, description, or tags failed validation., MediaMetadata, build_metadata(), normalize_description(), normalize_tags(), normalize_title(), Validate and normalize titles, descriptions, and tags. (+14 more)

### Community 7 - "models.py"
Cohesion: 0.11
Nodes (28): Enum, Exception, MadifyError, Domain and application errors with explicit failure modes., Scan root is missing or not a directory., Base error for expected Madify failures., Path is not a supported image, PSD, or video file., ScanError (+20 more)

### Community 8 - "FileSystem"
Cohesion: 0.09
Nodes (21): Protocol, CatalogStore, Clock, FileSystem, datetime, Narrow I/O ports injected into core use cases., Return the current timezone-aware UTC timestamp., Return True when path exists and is a directory. (+13 more)

### Community 9 - "CatalogStore"
Cohesion: 0.21
Nodes (17): AssetNotFoundError, Requested catalog asset does not exist., TagRequest, Apply title, description, and tags to a catalogued asset., _resolve_asset(), tag_asset(), datetime, _p() (+9 more)

### Community 11 - "naming.py"
Cohesion: 0.17
Nodes (21): File cannot be renamed (missing title, collision, or filesystem failure)., RenameError, allocate_unique_path(), proposed_filename(), proposed_path(), Pure filename construction for metadata-driven renames., Pick desired path, or desired stem_2/stem_3… if taken (casefold keys)., sanitize_filename_stem() (+13 more)

## Knowledge Gaps
- **2 isolated node(s):** `madify`, `Madify`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MediaAsset` connect `MediaAsset` to `test_cli.py`, `models.py`, `FileSystem`, `CatalogStore`, `naming.py`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `SqliteCatalog` connect `MediaAsset` to `test_main_prints_app_name_and_version`, `CatalogStore`, `errors.py`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
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