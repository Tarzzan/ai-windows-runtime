# Phase 101 - Execution Momentum Report

## Objectif

Ajouter un indicateur de momentum d'execution pour guider les decisions de cadence entre acceleration, maintien controle et stabilisation.

## Livrables

- Nouveau module `compat_runtime.execution_momentum`:
  - indice de momentum (0-100)
  - posture `advancing/holding/fragile`
  - synthese des penalites (blockers, incidents P0, pression P0)
- Nouveau schema: `schemas/execution-momentum-report.schema.json`
- Nouveau script: `scripts/build-execution-momentum-report.sh`
- Integration pipeline et release bundle:
  - generation + validation
  - inclusion dans le repro package et le release bundle
  - regeneration dans la chaine policy-aware
- Dashboard local enrichi avec `momentum_posture` et `momentum_index`.

## Impact

Le pilotage dispose d'un signal global de vitesse utile pour arbitrer scope, priorites et capacite de livraison a court terme.

## Fichiers modifies

- `src/compat_runtime/execution_momentum/cli.py`
- `scripts/build-execution-momentum-report.sh`
- `schemas/execution-momentum-report.schema.json`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `README.md`
