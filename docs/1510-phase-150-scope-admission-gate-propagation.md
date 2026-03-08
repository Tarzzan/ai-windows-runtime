# Phase 150 - Scope Admission Gate Propagation

## Objectif

Propager un gate d'admission scope (`closed/guarded/open`) base sur la politique de transition intake, le freeze guard et le statut policy release.

## Livrables

- Nouveau module `compat_runtime.scope_admission_gate`.
- Nouveau schema `schemas/scope-admission-gate-report.schema.json`.
- Nouveau script `scripts/build-scope-admission-gate-report.sh`.
- Dashboard enrichi avec readiness transition, politique transition et gate admission.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle ajoute un gate d'admission scope decisionnel avant extension de perimetre.

## Fichiers modifies

- `src/compat_runtime/scope_admission_gate/cli.py`
- `schemas/scope-admission-gate-report.schema.json`
- `scripts/build-scope-admission-gate-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
