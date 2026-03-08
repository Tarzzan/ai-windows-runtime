# Phase 113 - Cadence Recommendation Report

## Objectif

Dériver une cadence d'exécution (`slow/moderate/fast`) à partir de la friction gouvernance, de la température delivery et du mode de contrôle.

## Livrables

- Nouveau module `compat_runtime.cadence_recommendation`.
- Nouveau schema `schemas/cadence-recommendation-report.schema.json`.
- Nouveau script `scripts/build-cadence-recommendation-report.sh`.
- Intégration génération/validation dans pipeline et release bundle.

## Impact

Le flux d'exécution dispose d'une recommandation de cadence exploitable pour l'ordonnancement court terme.

## Fichiers modifies

- `src/compat_runtime/cadence_recommendation/cli.py`
- `schemas/cadence-recommendation-report.schema.json`
- `scripts/build-cadence-recommendation-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
