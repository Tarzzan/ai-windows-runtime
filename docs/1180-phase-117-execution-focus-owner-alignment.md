# Phase 117 - Execution Focus Owner Alignment

## Objectif

Introduire un artefact de focus execution pour cadrer les priorites P0 et la portee proprietaire active en fonction de la cadence.

## Livrables

- Nouveau module `compat_runtime.execution_focus`.
- Nouveau schema `schemas/execution-focus-report.schema.json`.
- Nouveau script `scripts/build-execution-focus-report.sh`.
- Dashboard enrichi avec friction/cadence/focus/owners.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose une vue actionnable des points P0 et de la capacite owner en phase courante.

## Fichiers modifies

- `src/compat_runtime/execution_focus/cli.py`
- `schemas/execution-focus-report.schema.json`
- `scripts/build-execution-focus-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
