# Phase 10 - Runtime telemetry hooks

## Scope livré
- Ajout d'un module `telemetry` dans `runtime-core`:
  - `TelemetryRecorder`
  - `RuntimeTelemetryEvent`
  - `TelemetryStage` (`Start`, `Success`, `Error`)
- Instrumentation de `RuntimeCore::simulate_win32_call(...)`:
  - événement `Start` avant exécution
  - événement `Success` en cas de succès avec type de résultat
  - événement `Error` en cas d'échec avec détail texte
- Exposition des hooks de collecte:
  - `telemetry_events()`
  - `take_telemetry_events()`
  - `clear_telemetry_events()`
- Ajout d'un jalon API runtime phase 10:
  - `register_phase10_runtime_apis()` (inclut `ntdll.NtTraceEvent`, `advapi32.EventWrite`, `advapi32.EventRegister`)

## Capacités ajoutées
1. Traçabilité structurée des appels simulés Win32.
2. Séquencement déterministe des événements (`seq` monotone).
3. Support test-friendly via lecture et drain des événements.

## Fichiers clés
- `runtime-core/src/telemetry.rs`
- `runtime-core/src/runtime.rs`
- `runtime-core/src/lib.rs`
- `runtime-core/tests/runtime_flow.rs`

## Validation locale
```bash
cargo fmt --manifest-path runtime-core/Cargo.toml
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
. .venv/bin/activate && pytest -q && ruff check .
```
