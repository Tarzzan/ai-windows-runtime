# Phase 155 - Intake Expansion Policy Report

## Objectif

Deriver une politique d'expansion intake (`hold/stage/expand`) a partir de la readiness d'expansion scope, de la reprise intake et de la bande passante delivery.

## Livrables

- Nouveau module `compat_runtime.intake_expansion_policy`.
- Nouveau schema `schemas/intake-expansion-policy-report.schema.json`.
- Nouveau script `scripts/build-intake-expansion-policy-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle affiche une politique d'expansion intake explicite avant toute acceleration d'admission.

## Fichiers modifies

- `src/compat_runtime/intake_expansion_policy/cli.py`
- `schemas/intake-expansion-policy-report.schema.json`
- `scripts/build-intake-expansion-policy-report.sh`
- `tests/test_intake_expansion_policy.py`
