# Phase 119 - Execution Throttle Report

## Objectif

Deriver un mode de throttle execution (`tight/balanced/open`) a partir de la cadence, friction gouvernance et surcharge owner.

## Livrables

- Nouveau module `compat_runtime.execution_throttle`.
- Nouveau schema `schemas/execution-throttle-report.schema.json`.
- Nouveau script `scripts/build-execution-throttle-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le projet obtient un signal operatoire pour controler explicitement l'entree de nouvelles taches.

## Fichiers modifies

- `src/compat_runtime/execution_throttle/cli.py`
- `schemas/execution-throttle-report.schema.json`
- `scripts/build-execution-throttle-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
