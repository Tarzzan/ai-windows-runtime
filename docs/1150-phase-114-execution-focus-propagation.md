# Phase 114 - Execution Focus Propagation

## Objectif

Propager un focus d'exécution orienté P0 dans les artefacts et le dashboard via cadence et ownership.

## Livrables

- Nouveau module `compat_runtime.execution_focus`.
- Nouveau schema `schemas/execution-focus-report.schema.json`.
- Nouveau script `scripts/build-execution-focus-report.sh`.
- Dashboard enrichi avec `friction_band`, `friction_score`, `cadence`, `focus_items`.
- Intégration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de contrôle reflète la priorité exécution P0 la plus récente, alignée avec cadence et gouvernance.

## Fichiers modifies

- `src/compat_runtime/execution_focus/cli.py`
- `schemas/execution-focus-report.schema.json`
- `scripts/build-execution-focus-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
