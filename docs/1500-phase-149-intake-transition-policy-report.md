# Phase 149 - Intake Transition Policy Report

## Objectif

Deriver une politique de transition intake (`hold/stage/advance`) a partir de la readiness de transition et du pacing intake.

## Livrables

- Nouveau module `compat_runtime.intake_transition_policy`.
- Nouveau schema `schemas/intake-transition-policy-report.schema.json`.
- Nouveau script `scripts/build-intake-transition-policy-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle affiche une politique de transition intake explicite pour limiter les decisions ad hoc.

## Fichiers modifies

- `src/compat_runtime/intake_transition_policy/cli.py`
- `schemas/intake-transition-policy-report.schema.json`
- `scripts/build-intake-transition-policy-report.sh`
- `tests/test_intake_transition_policy.py`
