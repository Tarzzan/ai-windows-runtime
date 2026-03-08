# Phase 127 - Scope Budget Report

## Objectif

Ajouter un signal de budget de scope (`tight/balanced/flexible`) derive du pacing d'engagement, du readiness score et de l'horizon forecast.

## Livrables

- Nouveau module `compat_runtime.scope_budget`.
- Nouveau schema `schemas/scope-budget-report.schema.json`.
- Nouveau script `scripts/build-scope-budget-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un score budget scope explicite pour cadrer l'ouverture de nouveau travail.

## Fichiers modifies

- `src/compat_runtime/scope_budget/cli.py`
- `schemas/scope-budget-report.schema.json`
- `scripts/build-scope-budget-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
