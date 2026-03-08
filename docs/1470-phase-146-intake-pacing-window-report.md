# Phase 146 - Intake Pacing Window Report

## Objectif

Deriver une fenetre de pacing intake (`slow/moderate/fast`) depuis le stress delivery, la politique de slots et la fenetre intake release.

## Livrables

- Nouveau module `compat_runtime.intake_pacing_window`.
- Nouveau schema `schemas/intake-pacing-window-report.schema.json`.
- Nouveau script `scripts/build-intake-pacing-window-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance dispose d'un signal de cadence intake operable avant ouverture de nouveaux lots.

## Fichiers modifies

- `src/compat_runtime/intake_pacing_window/cli.py`
- `schemas/intake-pacing-window-report.schema.json`
- `scripts/build-intake-pacing-window-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
