# Phase 142 - Throughput Guard Band Report

## Objectif

Ajouter une bande de garde de debit (`tight/balanced/wide`) derivee du scope lock state, de la marge safety et de la reserve d'execution.

## Livrables

- Nouveau module `compat_runtime.throughput_guard_band`.
- Nouveau schema `schemas/throughput-guard-band-report.schema.json`.
- Nouveau script `scripts/build-throughput-guard-band-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'un signal de garde debit explicite pour reguler l'acceptation de charge.

## Fichiers modifies

- `src/compat_runtime/throughput_guard_band/cli.py`
- `schemas/throughput-guard-band-report.schema.json`
- `scripts/build-throughput-guard-band-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
