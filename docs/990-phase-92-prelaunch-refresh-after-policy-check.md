# Phase 92 - Prelaunch Refresh After Policy Check

## Objectif

Garantir la coherence des artefacts prelaunch apres la regeneration policy tardive.

## Livrables

- Dans `run-full-pipeline` et `build-release-bundle`, apres `check-release-policy` et la regeneration communication:
  - regeneration `handoff-checklist-report`
  - regeneration `launch-readiness-report`
  - regeneration `release-packet-report`

## Impact

`release-packet-report` integre des signaux launch/handoff alignes avec l'etat policy le plus recent du run courant.

## Fichiers modifies

- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

