# Phase 2 - Native Runtime Core

## Scope delivered
- Rust crate `runtime-core` added.
- Minimal PE metadata loader (`parse_pe_metadata`).
- API dispatcher with three states:
  - `Implemented`
  - `Stubbed`
  - `Missing`
- Runtime façade `RuntimeCore` to connect loader and dispatcher.
- CLI probe binary `runtime_probe`.
- Unit + integration tests.

## Design intent
This phase introduces deterministic native primitives to support future compatibility work:
1. Load and classify PE payloads early.
2. Route API calls through an explicit registry.
3. Produce predictable behavior for missing/stubbed APIs.

## Main files
- `runtime-core/src/pe.rs`
- `runtime-core/src/dispatcher.rs`
- `runtime-core/src/runtime.rs`
- `runtime-core/src/bin/runtime_probe.rs`
- `runtime-core/tests/runtime_flow.rs`

## Local validation
```bash
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
