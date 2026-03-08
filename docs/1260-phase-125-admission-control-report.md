# Phase 125 - Admission Control Report

## Objectif

Deriver un etat d'admission (`gated/selective/open`) depuis la capacite d'intake, la policy de release et le corridor de priorite.

## Livrables

- Nouveau module `compat_runtime.admission_control`.
- Nouveau schema `schemas/admission-control-report.schema.json`.
- Nouveau script `scripts/build-admission-control-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance peut verrouiller ou ouvrir les admissions avec un signal deterministic aligne policy/capacite.

## Fichiers modifies

- `src/compat_runtime/admission_control/cli.py`
- `schemas/admission-control-report.schema.json`
- `scripts/build-admission-control-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
