# Phase 152 - Intake Resumption Policy Report

## Objectif

Deriver une politique de reprise intake (`hold/stage/resume`) a partir de la readiness de reentree scope et de la temperature delivery.

## Livrables

- Nouveau module `compat_runtime.intake_resumption_policy`.
- Nouveau schema `schemas/intake-resumption-policy-report.schema.json`.
- Nouveau script `scripts/build-intake-resumption-policy-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle affiche une politique de reprise intake explicite avant de relancer le flux d'admission.

## Fichiers modifies

- `src/compat_runtime/intake_resumption_policy/cli.py`
- `schemas/intake-resumption-policy-report.schema.json`
- `scripts/build-intake-resumption-policy-report.sh`
- `tests/test_intake_resumption_policy.py`
