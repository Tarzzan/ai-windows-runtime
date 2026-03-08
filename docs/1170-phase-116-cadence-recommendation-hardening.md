# Phase 116 - Cadence Recommendation Hardening

## Objectif

Deriver une recommandation de cadence execution (`slow/moderate/fast`) a partir des signaux de friction, temperature et mode de controle.

## Livrables

- Nouveau module `compat_runtime.cadence_recommendation`.
- Nouveau schema `schemas/cadence-recommendation-report.schema.json`.
- Nouveau script `scripts/build-cadence-recommendation-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

L'equipe obtient une recommandation de vitesse d'execution explicite et alignable avec la gouvernance.

## Fichiers modifies

- `src/compat_runtime/cadence_recommendation/cli.py`
- `schemas/cadence-recommendation-report.schema.json`
- `scripts/build-cadence-recommendation-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
