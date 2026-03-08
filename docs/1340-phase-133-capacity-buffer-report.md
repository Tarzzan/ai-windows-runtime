# Phase 133 - Capacity Buffer Report

## Objectif

Ajouter un signal de buffer capacite (`low/medium/high`) derive de la reserve d'execution, de la surcharge owner et de la pression backlog.

## Livrables

- Nouveau module `compat_runtime.capacity_buffer`.
- Nouveau schema `schemas/capacity-buffer-report.schema.json`.
- Nouveau script `scripts/build-capacity-buffer-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'une mesure explicite de marge capacite avant admission de nouveaux items.

## Fichiers modifies

- `src/compat_runtime/capacity_buffer/cli.py`
- `schemas/capacity-buffer-report.schema.json`
- `scripts/build-capacity-buffer-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
