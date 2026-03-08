# Phase 121 - Queue Pressure Report

## Objectif

Ajouter un indicateur de pression de file pour objectiver la congestion execution issue des owners, du throttle et du corridor de priorite.

## Livrables

- Nouveau module `compat_runtime.queue_pressure`.
- Nouveau schema `schemas/queue-pressure-report.schema.json`.
- Nouveau script `scripts/build-queue-pressure-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un signal direct de congestion de file avant ouverture de nouvelles entrées.

## Fichiers modifies

- `src/compat_runtime/queue_pressure/cli.py`
- `schemas/queue-pressure-report.schema.json`
- `scripts/build-queue-pressure-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
