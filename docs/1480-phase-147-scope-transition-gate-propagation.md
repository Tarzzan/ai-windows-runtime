# Phase 147 - Scope Transition Gate Propagation

## Objectif

Propager un gate de transition scope (`blocked/conditional/open`) derive du pacing intake, du freeze guard et du statut policy.

## Livrables

- Nouveau module `compat_runtime.scope_transition_gate`.
- Nouveau schema `schemas/scope-transition-gate-report.schema.json`.
- Nouveau script `scripts/build-scope-transition-gate-report.sh`.
- Dashboard enrichi avec delivery stress, intake pacing window et scope transition gate.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose un gate de transition de scope actionnable avant ajustement de perimetre.

## Fichiers modifies

- `src/compat_runtime/scope_transition_gate/cli.py`
- `schemas/scope-transition-gate-report.schema.json`
- `scripts/build-scope-transition-gate-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
