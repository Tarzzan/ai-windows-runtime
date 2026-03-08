# Phase 124 - Intake Capacity Report

## Objectif

Ajouter un signal de capacite d'intake (`constrained/balanced/expandable`) derive du guard d'intake, de la bande passante delivery et de la pression de file.

## Livrables

- Nouveau module `compat_runtime.intake_capacity`.
- Nouveau schema `schemas/intake-capacity-report.schema.json`.
- Nouveau script `scripts/build-intake-capacity-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un score capacite explicite pour arbitrer l'ouverture de nouveaux engagements.

## Fichiers modifies

- `src/compat_runtime/intake_capacity/cli.py`
- `schemas/intake-capacity-report.schema.json`
- `scripts/build-intake-capacity-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
