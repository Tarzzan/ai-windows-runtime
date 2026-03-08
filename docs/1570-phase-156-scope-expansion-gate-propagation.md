# Phase 156 - Scope Expansion Gate Propagation

## Objectif

Propager un gate d'expansion scope (`closed/guarded/open`) base sur la politique d'expansion intake, le gate de deblocage et le statut policy.

## Livrables

- Nouveau module `compat_runtime.scope_expansion_gate`.
- Nouveau schema `schemas/scope-expansion-gate-report.schema.json`.
- Nouveau script `scripts/build-scope-expansion-gate-report.sh`.
- Dashboard enrichi avec readiness/politique/gate d'expansion.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle ajoute un signal d'expansion scope actionnable avant extension de perimetre.

## Fichiers modifies

- `src/compat_runtime/scope_expansion_gate/cli.py`
- `schemas/scope-expansion-gate-report.schema.json`
- `scripts/build-scope-expansion-gate-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
