# Phase 14 - Trend report generator

## Scope livré
- Ajout d'un générateur de tendance multi-runs:
  - `compat_runtime.trend_report.cli`
  - artefact de sortie `trend-report.json`
- Ajout d'un schéma dédié:
  - `schemas/trend-report.schema.json`
- Ajout d'un script dédié:
  - `scripts/build-trend-report.sh`
- Extension du script full pipeline:
  - `scripts/run-full-pipeline.sh` génère et valide aussi `trend-report.json`.
- Extension du validateur batch:
  - `scripts/validate-artifacts.sh` valide aussi `execution-report.json` et `trend-report.json` quand présents.

## Capacités ajoutées
1. Comparaison `current` vs `baseline` sur métriques clés:
- `base_trace_events`, `base_gaps`, `base_proposals`
- `runtime_trace_events`, `runtime_gaps`, `runtime_proposals`

2. Classification automatique des deltas:
- `improved`
- `stable`
- `regressed`

3. Synthèse de statut:
- `status_delta` entre baseline et current
- listes `improved_metrics` / `regressed_metrics`

## Fichiers clés
- `src/compat_runtime/trend_report/cli.py`
- `src/compat_runtime/trend_report/__init__.py`
- `schemas/trend-report.schema.json`
- `scripts/build-trend-report.sh`
- `scripts/run-full-pipeline.sh`
- `tests/test_trend_report.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-trend-report.sh out/execution-report.json

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
