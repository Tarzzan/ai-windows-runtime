# Phase 153 - Scope Unlock Gate Propagation

## Objectif

Propager un gate de deblocage scope (`locked/guarded/unlocked`) base sur la politique de reprise intake, le gate admission et le statut policy.

## Livrables

- Nouveau module `compat_runtime.scope_unlock_gate`.
- Nouveau schema `schemas/scope-unlock-gate-report.schema.json`.
- Nouveau script `scripts/build-scope-unlock-gate-report.sh`.
- Dashboard enrichi avec reentree scope, reprise intake et gate de deblocage.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle ajoute un signal de deblocage scope decisionnel avant extension de perimetre.

## Fichiers modifies

- `src/compat_runtime/scope_unlock_gate/cli.py`
- `schemas/scope-unlock-gate-report.schema.json`
- `scripts/build-scope-unlock-gate-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
