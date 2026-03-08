# Phase 141 - Scope Lock State Propagation

## Objectif

Propager un etat de verrou scope (`locked/controlled/flexible`) derive de la fenetre d'engagement, du rebalance scope et de la pression P0.

## Livrables

- Nouveau module `compat_runtime.scope_lock_state`.
- Nouveau schema `schemas/scope-lock-state-report.schema.json`.
- Nouveau script `scripts/build-scope-lock-state-report.sh`.
- Dashboard enrichi avec safety margin, intake commitment window et scope lock state.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose l'etat de verrou scope pour cadrer les arbitrages de priorite.

## Fichiers modifies

- `src/compat_runtime/scope_lock_state/cli.py`
- `schemas/scope-lock-state-report.schema.json`
- `scripts/build-scope-lock-state-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
