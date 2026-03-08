# Phase 158 - Intake Acceleration Policy Report

## Objectif

Deriver une politique d'acceleration intake (`hold/stage/accelerate`) a partir de la readiness d'acceleration scope, de la politique d'expansion intake et de la bande passante delivery.

## Livrables

- Nouveau module `compat_runtime.intake_acceleration_policy`.
- Nouveau schema `schemas/intake-acceleration-policy-report.schema.json`.
- Nouveau script `scripts/build-intake-acceleration-policy-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle affiche une politique d'acceleration intake explicite avant toute acceleration d'admission.

## Fichiers modifies

- `src/compat_runtime/intake_acceleration_policy/cli.py`
- `schemas/intake-acceleration-policy-report.schema.json`
- `scripts/build-intake-acceleration-policy-report.sh`
- `tests/test_intake_acceleration_policy.py`
