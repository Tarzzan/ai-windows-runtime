# Phase 110 - Intervention Mode Planning

## Objectif

Deriver un mode d'intervention operationnel (`routine/targeted/urgent`) depuis l'efficacite de controle, les risques P0 et les dependances bloquantes.

## Livrables

- Nouveau module `compat_runtime.intervention_plan`.
- Nouveau schema `schemas/intervention-plan-report.schema.json`.
- Nouveau script `scripts/build-intervention-plan-report.sh`.
- Integration generation/validation pipeline + release bundle.

## Impact

Le flux de delivery dispose d'une orientation d'intervention immediate, exploitable pour l'allocation court terme.

## Fichiers modifies

- `src/compat_runtime/intervention_plan/cli.py`
- `schemas/intervention-plan-report.schema.json`
- `scripts/build-intervention-plan-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
