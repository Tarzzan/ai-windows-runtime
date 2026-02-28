# AI Windows Runtime

AI Windows Runtime is a new Linux-native Windows compatibility runtime, designed from day one for AI-assisted compatibility iteration.

## Why this project
Current compatibility layers were not built around modern feedback loops (large-scale trace analysis, automated gap detection, patch generation, reproducible validation). This project targets a new architecture where runtime engineering and AI tooling are first-class citizens.

## Primary objective
Deliver a native Ubuntu-compatible runtime that can execute modern Windows installers/apps incrementally, starting with high-friction enterprise scenarios (Office Click-to-Run class installers).

## Repository map
- `docs/` product and engineering strategy
- `src/compat_runtime/` MVP tooling for trace -> gap -> patch proposal loop
- `runtime-core/` native Rust runtime core prototype (PE loader metadata + API dispatcher)
- `schemas/` JSON schemas for runtime evidence artifacts
- `scripts/` reproducible workflows
- `tests/` automated validation
- `.github/workflows/` CI

## Current scope (Phase 3)
This repository currently ships:
1. Planning baseline (vision, architecture, roadmap, risk model).
2. AI compatibility loop prototype (trace -> gaps -> patch plan).
3. Native runtime core prototype in Rust (PE loader + section mapping + import parser + API dispatcher).

Core runtime capabilities in this phase:
1. Parse execution traces.
2. Detect likely compatibility gaps.
3. Produce ranked patch proposals for engineering review.
4. Parse core PE metadata from executable payloads.
5. Map PE headers/sections into an in-memory image model.
6. Parse minimal import table descriptors and extract imported DLL names.
7. Dispatch known APIs as implemented/stubbed/missing decisions.

## Quick start
```bash
cd /home/tarzzan/Wine/ai-windows-runtime
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m compat_runtime.trace_collector.cli --input examples/sample-trace.log --output out/trace.json
python -m compat_runtime.gap_detector.cli --trace out/trace.json --output out/gaps.json
python -m compat_runtime.patch_orchestrator.cli --gaps out/gaps.json --output out/patch-plan.json
pytest -q

# Native runtime core checks
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

## Product deliverables included
- Vision and strategy
- Architecture blueprint
- 30/60/90 roadmap
- AI compatibility loop design
- Implementation operating model
- Prioritized backlog (50 tasks)
- Risks and mitigations
- Ubuntu proof-of-feasibility plan
- Executable Sprint 01 plan
