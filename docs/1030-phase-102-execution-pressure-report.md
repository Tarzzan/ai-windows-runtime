# Phase 102 - Execution Pressure Report

## Objectif

Ajouter un indicateur de pression de livraison pour objectiver la charge de risque operationnelle avant les gates de signoff.

## Livrables

- Nouveau module `compat_runtime.execution_pressure`:
  - indice de pression (0-100)
  - niveau `low/medium/high/critical`
  - decomposition scoring (momentum + dependances + risques + couverture validation)
- Nouveau schema: `schemas/execution-pressure-report.schema.json`
- Nouveau script: `scripts/build-execution-pressure-report.sh`
- Integration pipeline et release bundle:
  - generation + validation
  - inclusion repro package/release bundle
  - regeneration dans la chaine policy-aware
- Dashboard local enrichi avec `pressure_level` et `pressure_index`.

## Impact

Le pilotage peut arbitrer la cadence de delivery avec un signal de pression directement actionnable pour la priorisation court terme.

## Fichiers modifies

- `src/compat_runtime/execution_pressure/cli.py`
- `schemas/execution-pressure-report.schema.json`
- `scripts/build-execution-pressure-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `README.md`
