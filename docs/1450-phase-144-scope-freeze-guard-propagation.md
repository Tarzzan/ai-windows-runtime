# Phase 144 - Scope Freeze Guard Propagation

## Objectif

Propager un garde de gel scope (`freeze/guarded/open`) derive de la politique de slots, du verrou scope et de la pression P0.

## Livrables

- Nouveau module `compat_runtime.scope_freeze_guard`.
- Nouveau schema `schemas/scope-freeze-guard-report.schema.json`.
- Nouveau script `scripts/build-scope-freeze-guard-report.sh`.
- Dashboard enrichi avec throughput guard band, intake slot policy et scope freeze guard.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle affiche un garde de gel scope exploitable pour prioriser les arbitrages.

## Fichiers modifies

- `src/compat_runtime/scope_freeze_guard/cli.py`
- `schemas/scope-freeze-guard-report.schema.json`
- `scripts/build-scope-freeze-guard-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
