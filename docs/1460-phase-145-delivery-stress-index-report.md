# Phase 145 - Delivery Stress Index Report

## Objectif

Ajouter un indice de stress delivery (`low/medium/high`) derive du scope freeze guard, de la bande debit et de la pression P0.

## Livrables

- Nouveau module `compat_runtime.delivery_stress_index`.
- Nouveau schema `schemas/delivery-stress-index-report.schema.json`.
- Nouveau script `scripts/build-delivery-stress-index-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un signal explicite de stress delivery pour cadrer le rythme d'admission.

## Fichiers modifies

- `src/compat_runtime/delivery_stress_index/cli.py`
- `schemas/delivery-stress-index-report.schema.json`
- `scripts/build-delivery-stress-index-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
