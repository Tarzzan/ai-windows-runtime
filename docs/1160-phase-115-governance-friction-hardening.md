# Phase 115 - Governance Friction Hardening

## Objectif

Ajouter une mesure explicite de friction gouvernance pour objectiver la surcharge de pilotage sur les cycles actifs.

## Livrables

- Nouveau module `compat_runtime.governance_friction`.
- Nouveau schema `schemas/governance-friction-report.schema.json`.
- Nouveau script `scripts/build-governance-friction-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un signal unique pour quantifier la difficulte de gouvernance a court terme.

## Fichiers modifies

- `src/compat_runtime/governance_friction/cli.py`
- `schemas/governance-friction-report.schema.json`
- `scripts/build-governance-friction-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
