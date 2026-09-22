# guard-core-rs

The Rust port of the guard-core detection engine. Cargo workspace (`crates/*`), edition 2024, MSRV 1.92, `unsafe_code = "forbid"`.

## State

Version 0.0.1, no git tags, nothing on crates.io. Workspace members:

- `guard-core-rs` 0.0.1: the facade crate (unstable API surface).
- `guard-core-engine` 0.0.1: the engine crate, marked `publish = false`.
- `guard-core-python` 0.0.1: PyO3 cdylib binding.
- `guard-core-benchmark` and `guard-core-conformance`: internal.

The README still reads "Work in progress - namespace placeholder", which undersells the tree but means it documents no dependency usage.

## Setup

Adapters (tower-guard-rs, axum-guard-rs, actix-guard-rs, rocket-guard-rs) all bypass the facade and depend on the engine crate directly, because the facade currently re-exports only `preprocessor` and `semantic` and not the detect path:

```toml
guard-core-engine = { path = "../guard-core-rs/crates/guard-core-engine" }
```

Engine view: `detect(content, context, config)` with `DetectConfig::max_full_scan_bytes` (262,144 bytes, the ecosystem default). The engine never scans the HTTP method, and its header view skips `sec-*` plus a fixed set of standard hop headers.

## Conformance

`conformance/` holds the spec 4.0.2 corpus (163 cases across 11 suites, pinned at reference commit `886f8013`), a `pattern_ledger.toml`, and an `xfail_baseline.toml` of 124 baselined cases: with zero drift the gate reports 39 passed / 124 xfail (163 total). The xfail reason is that the Rust engine lacks the 4.x pattern-table scan stage. AGENTS.md instructs: do not claim parity with the Python engine in any doc, issue, or PR.

## Footguns

- The facade crate is not the integration point; use `guard-core-engine` until a tagged crates.io release re-exports the detect path.
- All adapter and engine crates are path dependencies (`../guard-core-rs/...`): builds only work when the repos sit next to each other, and cargo/git dependencies cannot be written until tagging.
- No `.agents` skill and no docs/ directory; AGENTS.md (mirrored byte-identically in CLAUDE.md) is the real documentation.
