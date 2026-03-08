# Phase 123 - Intake Guard Propagation

## Objectif

Propager un guard d'intake (`strict/moderate/open`) derive de la bande passante, de la policy et du corridor de priorite.

## Livrables

- Nouveau module `compat_runtime.intake_guard`.
- Nouveau schema `schemas/intake-guard-report.schema.json`.
- Nouveau script `scripts/build-intake-guard-report.sh`.
- Dashboard enrichi avec queue pressure, bandwidth mode et intake guard.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose un niveau de garde intake actionnable avant chaque cycle de planification.

## Fichiers modifies

- `src/compat_runtime/intake_guard/cli.py`
- `schemas/intake-guard-report.schema.json`
- `scripts/build-intake-guard-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
