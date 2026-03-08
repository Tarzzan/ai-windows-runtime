# Phase 159 - Scope Acceleration Gate Propagation

## Objectif

Propager un gate d'acceleration scope (`closed/guarded/open`) base sur la politique d'acceleration intake, le gate d'expansion et le statut policy.

## Livrables

- Nouveau module `compat_runtime.scope_acceleration_gate`.
- Nouveau schema `schemas/scope-acceleration-gate-report.schema.json`.
- Nouveau script `scripts/build-scope-acceleration-gate-report.sh`.
- Dashboard enrichi avec readiness/politique/gate d'acceleration.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle ajoute un signal d'acceleration scope actionnable avant acceleration de perimetre.

## Fichiers modifies

- `src/compat_runtime/scope_acceleration_gate/cli.py`
- `schemas/scope-acceleration-gate-report.schema.json`
- `scripts/build-scope-acceleration-gate-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
