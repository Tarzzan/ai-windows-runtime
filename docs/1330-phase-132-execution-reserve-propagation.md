# Phase 132 - Execution Reserve Propagation

## Objectif

Propager une reserve d'execution (`protected/managed/surplus`) derivee du sync delivery/intake, du scope budget et de la surcharge owner.

## Livrables

- Nouveau module `compat_runtime.execution_reserve`.
- Nouveau schema `schemas/execution-reserve-report.schema.json`.
- Nouveau script `scripts/build-execution-reserve-report.sh`.
- Dashboard enrichi avec risk budget, delivery-intake sync et execution reserve.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose la reserve d'execution exploitable pour arbitrer la capacite court terme.

## Fichiers modifies

- `src/compat_runtime/execution_reserve/cli.py`
- `schemas/execution-reserve-report.schema.json`
- `scripts/build-execution-reserve-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
