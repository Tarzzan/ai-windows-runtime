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

## Current scope (Phase 24)
This repository currently ships:
1. Planning baseline (vision, architecture, roadmap, risk model).
2. AI compatibility loop prototype (trace -> gaps -> patch plan).
3. Native runtime core prototype in Rust (PE loader + section mapping + import/export parser + relocations + API dispatcher + mini linker + NT process/thread primitives + memory + Win32 sync/file/registry simulation + telemetry hooks).
4. Python telemetry adapter prototype to convert runtime telemetry artifacts into normalized trace artifacts.

Core runtime capabilities in this phase:
1. Parse execution traces.
2. Detect likely compatibility gaps.
3. Produce ranked patch proposals for engineering review.
4. Parse core PE metadata from executable payloads.
5. Map PE headers/sections into an in-memory image model.
6. Parse import descriptors and thunk lists (named APIs + ordinal imports).
7. Parse export tables (DLL name, ordinals, RVAs, exported names).
8. Resolve imports against loaded export modules (mini linker report).
9. Produce per-DLL import/export details in runtime load reports.
10. Apply base relocations (DIR64/HIGHLOW) when image base differs.
11. Resolve imports across multiple provider modules with lookup cache.
12. Report ambiguous symbol matches and collision candidates.
13. Dispatch known APIs as implemented/stubbed/missing decisions.
14. Launch synthetic runtime processes with primary thread + handles.
15. Manage thread lifecycle transitions (running/waiting/resume/exit).
16. Cascade process termination to owned threads with state snapshots.
17. Manage virtual memory regions (alloc/protect/read/write/free) per synthetic process.
18. Simulate first kernel32 calls (CreateProcess/CreateThread/VirtualAlloc/VirtualProtect/ReadWriteProcessMemory/GetExitCodeProcess/TerminateProcess/CloseHandle).
19. Simulate synchronization waits (event/mutex + WaitForSingleObject/WaitForMultipleObjects).
20. Simulate minimal file adapter calls (CreateFile/Open, Read/Write, SetFilePointer, CloseHandle).
21. Simulate minimal registry adapter calls (RegSetValueEx/RegQueryValueEx/RegDeleteValue).
22. Emit structured runtime telemetry events (`start/success/error`) for each simulated Win32 call.
23. Expose telemetry capture API for extraction/drain in deterministic validation flows.
24. Adapt runtime telemetry artifacts into `trace.json` compatible events.
25. Merge telemetry-derived events with baseline traces for unified gap/patch planning.
26. Validate generated artifacts against repository schemas via native validator CLI.
27. Produce machine-readable validation reports for trace/gaps/patch-plan outputs.
28. Generate machine-readable end-to-end execution report artifacts.
29. Run complete pipeline gate (base + runtime + schema validation + execution report) in one script.
30. Generate trend reports from execution artifacts (current vs baseline).
31. Track metric deltas (gaps/proposals/events) and regression/improvement direction.
32. Generate KPI reports from execution/trend artifacts (run health, risk level, action hints).
33. Export dashboard timeseries artifacts for observability and milestone tracking.
34. Generate compatibility matrix and alpha release checklist artifacts.
35. Build release bundle manifest with checksum inventory for packaged deliverables.
36. Publish contributor runbook, corpus contribution protocol, and security review checklist.
37. Validate productization governance artifacts automatically in pipeline gates.
38. Generate deterministic reproduction packages for failing scenarios.
39. Capture environment fingerprint and artifact checksum inventory in repro packages.
40. Validate repro-package artifacts automatically in full pipeline and release bundle flows.
41. Generate root-cause clustering summary artifacts from base/runtime gaps.
42. Correlate gap clusters with patch priorities for actionable triage.
43. Validate root-cause summary artifacts automatically in pipeline gates.
44. Generate patch-plan diff artifacts against optional baseline plans.
45. Detect added/removed/changed proposals with reviewer-focused action hints.
46. Validate patch-plan diff artifacts automatically in pipeline and bundle gates.
47. Generate proposal provenance artifacts linking patch proposals back to gaps and traces.
48. Compute per-proposal provenance scores and evidence excerpts for reviewer traceability.
49. Validate proposal provenance artifacts automatically in pipeline and bundle gates.
50. Generate test impact report artifacts from patch proposals and gap categories.
51. Prioritize suggested test suites with estimated effort and execution commands.
52. Validate test impact report artifacts automatically in pipeline and release bundle gates.
53. Generate rollback hints artifacts aligned with proposal priority and risk levels.
54. Define rollback trigger signals, staged rollback steps, and validation commands per proposal.
55. Validate rollback hints artifacts automatically in pipeline and release bundle gates.
56. Generate proposal review checklist artifacts for engineering approval workflows.
57. Gate approval readiness using provenance, diff, rollback, and test-impact evidence.
58. Validate proposal review checklist artifacts automatically in pipeline and release bundle gates.

## Quick start
```bash
cd /home/tarzzan/Wine/ai-windows-runtime
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m compat_runtime.trace_collector.cli --input examples/sample-trace.log --output out/trace.json
python -m compat_runtime.gap_detector.cli --trace out/trace.json --output out/gaps.json
python -m compat_runtime.patch_orchestrator.cli --gaps out/gaps.json --output out/patch-plan.json
python -m compat_runtime.schema_validator.cli --input out/trace.json --schema schemas/trace.schema.json
python -m compat_runtime.schema_validator.cli --input out/gaps.json --schema schemas/gaps.schema.json
python -m compat_runtime.schema_validator.cli --input out/patch-plan.json --schema schemas/patch-plan.schema.json

# Adapt runtime telemetry into trace artifact (optional)
python -m compat_runtime.telemetry_adapter.cli --telemetry examples/sample-runtime-telemetry.json --output out/runtime-trace.json
python -m compat_runtime.gap_detector.cli --trace out/runtime-trace.json --output out/runtime-gaps.json
python -m compat_runtime.patch_orchestrator.cli --gaps out/runtime-gaps.json --output out/runtime-patch-plan.json
python -m compat_runtime.schema_validator.cli --input out/runtime-trace.json --schema schemas/trace.schema.json

# Validate full artifact batch with reports
scripts/validate-artifacts.sh out
scripts/run-full-pipeline.sh out
# out/execution-report.json is generated and schema-validated
scripts/build-trend-report.sh out/execution-report.json
# out/trend-report.json is generated and schema-validated
scripts/build-kpi-report.sh out/execution-report.json out/trend-report.json
# out/kpi-report.json and out/dashboard-timeseries.json are generated and schema-validated
scripts/build-release-bundle.sh out out/release-bundle
# out/compatibility-matrix.json, out/alpha-release-checklist.json and out/release-bundle-manifest.json are generated and schema-validated
scripts/check-productization-readiness.sh out
# out/productization-readiness.json is generated and schema-validated
scripts/build-root-cause-summary.sh out
# out/root-cause-summary.json is generated and schema-validated
scripts/build-patch-plan-diff.sh out
# out/patch-plan-diff.json is generated and schema-validated
scripts/build-proposal-provenance.sh out
# out/proposal-provenance.json is generated and schema-validated
scripts/build-test-impact-report.sh out
# out/test-impact-report.json is generated and schema-validated
scripts/build-rollback-hints.sh out
# out/rollback-hints.json is generated and schema-validated
scripts/build-proposal-review-checklist.sh out
# out/proposal-review-checklist.json is generated and schema-validated
scripts/build-repro-package.sh out
# out/repro-package.json is generated and schema-validated
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
