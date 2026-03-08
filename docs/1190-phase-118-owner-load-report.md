# Phase 118 - Owner Load Report

## Objectif

Ajouter un artefact de charge owner pour visualiser les zones de surcharge de responsabilite execution.

## Livrables

- Nouveau module `compat_runtime.owner_load`.
- Nouveau schema `schemas/owner-load-report.schema.json`.
- Nouveau script `scripts/build-owner-load-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage peut reequilibrer la charge d'execution entre owners avant de degrader le flux delivery.

## Fichiers modifies

- `src/compat_runtime/owner_load/cli.py`
- `schemas/owner-load-report.schema.json`
- `scripts/build-owner-load-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
