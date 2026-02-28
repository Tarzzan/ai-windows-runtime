# Phase 15 - KPI tracker et dashboard export

## Scope livré
- Ajout d'un module KPI:
  - `compat_runtime.kpi_tracker.cli`
  - génère `kpi-report.json` à partir d'`execution-report.json` (+ `trend-report.json` optionnel)
- Export dashboard timeseries:
  - `dashboard-timeseries.json` avec séries de runs pour visualisation
- Ajout des schémas dédiés:
  - `schemas/kpi-report.schema.json`
  - `schemas/dashboard-timeseries.schema.json`
- Intégration dans le pipeline complet:
  - `scripts/run-full-pipeline.sh` génère/valide KPI + dashboard
- Script dédié:
  - `scripts/build-kpi-report.sh`

## Capacités ajoutées
1. Suivi KPI de stabilité pipeline:
- `total_runs`, `ok_rate`, `risk_level`
- moyennes et dernier niveau de gaps/proposals

2. Synthèse opérationnelle:
- liste `actions` guidant les prochaines priorités

3. Observabilité multi-run:
- série structurée compatible dashboard (`points[]`)

## Fichiers clés
- `src/compat_runtime/kpi_tracker/cli.py`
- `src/compat_runtime/kpi_tracker/__init__.py`
- `schemas/kpi-report.schema.json`
- `schemas/dashboard-timeseries.schema.json`
- `scripts/build-kpi-report.sh`
- `scripts/run-full-pipeline.sh`
- `tests/test_kpi_tracker.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-trend-report.sh out/execution-report.json
scripts/build-kpi-report.sh out/execution-report.json out/trend-report.json

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
