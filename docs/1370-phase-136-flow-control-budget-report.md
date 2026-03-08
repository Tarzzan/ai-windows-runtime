# Phase 136 - Flow Control Budget Report

## Objectif

Ajouter un budget de controle de flux (`tight/managed/open`) derive du scope rebalance, du capacity buffer et de la reserve d'execution.

## Livrables

- Nouveau module `compat_runtime.flow_control_budget`.
- Nouveau schema `schemas/flow-control-budget-report.schema.json`.
- Nouveau script `scripts/build-flow-control-budget-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un indicateur de pilotage de flux consolidant pression scope et reserve execution.

## Fichiers modifies

- `src/compat_runtime/flow_control_budget/cli.py`
- `schemas/flow-control-budget-report.schema.json`
- `scripts/build-flow-control-budget-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
