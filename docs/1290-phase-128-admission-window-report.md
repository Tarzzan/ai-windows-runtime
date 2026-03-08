# Phase 128 - Admission Window Report

## Objectif

Deriver une fenetre d'admission (`restricted/controlled/open`) depuis scope budget, etat d'admission et saturation focus P0.

## Livrables

- Nouveau module `compat_runtime.admission_window`.
- Nouveau schema `schemas/admission-window-report.schema.json`.
- Nouveau script `scripts/build-admission-window-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance visualise une fenetre d'admission actionnable pour reguler le flux de nouvelles demandes.

## Fichiers modifies

- `src/compat_runtime/admission_window/cli.py`
- `schemas/admission-window-report.schema.json`
- `scripts/build-admission-window-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
