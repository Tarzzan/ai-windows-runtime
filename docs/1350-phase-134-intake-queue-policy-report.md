# Phase 134 - Intake Queue Policy Report

## Objectif

Deriver une politique de file intake (`restrictive/managed/permissive`) depuis le buffer capacite, le sync delivery/intake et le commitment guard.

## Livrables

- Nouveau module `compat_runtime.intake_queue_policy`.
- Nouveau schema `schemas/intake-queue-policy-report.schema.json`.
- Nouveau script `scripts/build-intake-queue-policy-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

La gouvernance obtient une politique intake directly actionnable au niveau file de priorisation.

## Fichiers modifies

- `src/compat_runtime/intake_queue_policy/cli.py`
- `schemas/intake-queue-policy-report.schema.json`
- `scripts/build-intake-queue-policy-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
