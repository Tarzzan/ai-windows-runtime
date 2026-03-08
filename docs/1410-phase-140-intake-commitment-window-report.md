# Phase 140 - Intake Commitment Window Report

## Objectif

Deriver une fenetre d'engagement intake (`locked/managed/open`) depuis la marge safety, la fenetre intake release et le stability guard.

## Livrables

- Nouveau module `compat_runtime.intake_commitment_window`.
- Nouveau schema `schemas/intake-commitment-window-report.schema.json`.
- Nouveau script `scripts/build-intake-commitment-window-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance dispose d'une fenetre d'engagement explicite pour piloter l'ouverture de lot.

## Fichiers modifies

- `src/compat_runtime/intake_commitment_window/cli.py`
- `schemas/intake-commitment-window-report.schema.json`
- `scripts/build-intake-commitment-window-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
