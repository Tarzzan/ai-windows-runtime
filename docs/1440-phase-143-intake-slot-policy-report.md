# Phase 143 - Intake Slot Policy Report

## Objectif

Deriver une politique de slots intake (`minimal/moderate/expanded`) depuis la bande debit, la fenetre d'engagement et la politique de file intake.

## Livrables

- Nouveau module `compat_runtime.intake_slot_policy`.
- Nouveau schema `schemas/intake-slot-policy-report.schema.json`.
- Nouveau script `scripts/build-intake-slot-policy-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance dispose d'une politique de slots intake actionnable pour cadencer les admissions.

## Fichiers modifies

- `src/compat_runtime/intake_slot_policy/cli.py`
- `schemas/intake-slot-policy-report.schema.json`
- `scripts/build-intake-slot-policy-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
