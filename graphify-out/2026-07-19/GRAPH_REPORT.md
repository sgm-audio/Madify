# Graph Report - Madify  (2026-07-19)

## Corpus Check
- 5 files · ~223 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 11 nodes · 7 edges · 5 communities (3 shown, 2 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `09d6a8c9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_main_prints_app_name_and_version
- README.md
- madify

## God Nodes (most connected - your core abstractions)
1. `test_main_prints_app_name_and_version()` - 3 edges
2. `main()` - 2 edges
3. `Madify` - 1 edges
4. `madify` - 0 edges

## Surprising Connections (you probably didn't know these)
- `test_main_prints_app_name_and_version()` --calls--> `main()`  [INFERRED]
  tests/test_cli.py → src/madify/__init__.py

## Import Cycles
- None detected.

## Communities (5 total, 2 thin omitted)

### Community 0 - "test_main_prints_app_name_and_version"
Cohesion: 0.50
Nodes (3): CaptureFixture, main(), test_main_prints_app_name_and_version()

## Knowledge Gaps
- **2 isolated node(s):** `madify`, `Madify`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `test_main_prints_app_name_and_version()` connect `test_main_prints_app_name_and_version` to `test_cli.py`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **What connects `madify`, `Madify` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._