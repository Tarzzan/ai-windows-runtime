# Phase 137 - Intake Release Window Report

## Objectif

Deriver une fenetre de release intake (`closed/limited/open`) depuis flow control, queue policy et admission window.

## Livrables

- Nouveau module `compat_runtime.intake_release_window`.
- Nouveau schema `schemas/intake-release-window-report.schema.json`.
- Nouveau script `scripts/build-intake-release-window-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance dispose d'un signal de fenetre intake explicite avant ouverture de nouveaux lots.

## Fichiers modifies

- `src/compat_runtime/intake_release_window/cli.py`
- `schemas/intake-release-window-report.schema.json`
- `scripts/build-intake-release-window-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
