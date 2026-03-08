# Phase 112 - Governance Friction Report

## Objectif

Ajouter un indicateur de friction de gouvernance qui synthétise efficacité de contrôle, mode d'intervention et couverture validation.

## Livrables

- Nouveau module `compat_runtime.governance_friction`.
- Nouveau schema `schemas/governance-friction-report.schema.json`.
- Nouveau script `scripts/build-governance-friction-report.sh`.
- Intégration génération/validation dans pipeline et release bundle.

## Impact

Le pilotage obtient une mesure explicite de la charge de friction gouvernance avant décision de cadence.

## Fichiers modifies

- `src/compat_runtime/governance_friction/cli.py`
- `schemas/governance-friction-report.schema.json`
- `scripts/build-governance-friction-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
