# Phase 131 - Delivery Intake Sync Report

## Objectif

Deriver un etat de synchronisation delivery/intake (`blocked/aligned/expanding`) depuis budget risque, fenetre d'admission et cadence.

## Livrables

- Nouveau module `compat_runtime.delivery_intake_sync`.
- Nouveau schema `schemas/delivery-intake-sync-report.schema.json`.
- Nouveau script `scripts/build-delivery-intake-sync-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance visualise un signal de synchronisation operable avant ouverture de flux intake.

## Fichiers modifies

- `src/compat_runtime/delivery_intake_sync/cli.py`
- `schemas/delivery-intake-sync-report.schema.json`
- `scripts/build-delivery-intake-sync-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
