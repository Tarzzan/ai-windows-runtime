# Phase 103 - Delivery Temperature Report

## Objectif

Ajouter un indicateur de temperature de delivery qui combine pression d'execution, readiness de lancement et decision de release.

## Livrables

- Nouveau module `compat_runtime.delivery_temperature` avec `temperature_index` et `temperature` (`cool/warm/hot`).
- Nouveau schema `schemas/delivery-temperature-report.schema.json`.
- Nouveau script `scripts/build-delivery-temperature-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un signal simple pour evaluer si la cadence actuelle est soutenable avant signoff.

## Fichiers modifies

- `src/compat_runtime/delivery_temperature/cli.py`
- `schemas/delivery-temperature-report.schema.json`
- `scripts/build-delivery-temperature-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
