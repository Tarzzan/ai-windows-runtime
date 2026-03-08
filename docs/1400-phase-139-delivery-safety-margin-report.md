# Phase 139 - Delivery Safety Margin Report

## Objectif

Ajouter un signal de marge de securite delivery (`narrow/guarded/comfortable`) derive du stability guard, du flow control et du capacity buffer.

## Livrables

- Nouveau module `compat_runtime.delivery_safety_margin`.
- Nouveau schema `schemas/delivery-safety-margin-report.schema.json`.
- Nouveau script `scripts/build-delivery-safety-margin-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un signal de marge delivery exploitable avant ouverture de nouveaux engagements.

## Fichiers modifies

- `src/compat_runtime/delivery_safety_margin/cli.py`
- `schemas/delivery-safety-margin-report.schema.json`
- `scripts/build-delivery-safety-margin-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
