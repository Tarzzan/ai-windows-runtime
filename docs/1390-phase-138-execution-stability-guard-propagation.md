# Phase 138 - Execution Stability Guard Propagation

## Objectif

Propager un guard de stabilite execution (`strict/elevated/normal`) derive de la fenetre intake release, de la pression P0 et du statut post-release.

## Livrables

- Nouveau module `compat_runtime.execution_stability_guard`.
- Nouveau schema `schemas/execution-stability-guard-report.schema.json`.
- Nouveau script `scripts/build-execution-stability-guard-report.sh`.
- Dashboard enrichi avec flow control, intake release window et stability guard.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose un niveau de stabilite execution operable avant arbitrage de cadence.

## Fichiers modifies

- `src/compat_runtime/execution_stability_guard/cli.py`
- `schemas/execution-stability-guard-report.schema.json`
- `scripts/build-execution-stability-guard-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
