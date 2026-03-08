# Phase 135 - Scope Rebalance Propagation

## Objectif

Propager un mode de rebalance de scope (`reduce/hold/expand`) derive de la politique intake, du budget risque et du mode scope budget.

## Livrables

- Nouveau module `compat_runtime.scope_rebalance`.
- Nouveau schema `schemas/scope-rebalance-report.schema.json`.
- Nouveau script `scripts/build-scope-rebalance-report.sh`.
- Dashboard enrichi avec capacity buffer, intake queue policy et scope rebalance.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose un arbitrage scope clair avant le lancement du cycle suivant.

## Fichiers modifies

- `src/compat_runtime/scope_rebalance/cli.py`
- `schemas/scope-rebalance-report.schema.json`
- `scripts/build-scope-rebalance-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
