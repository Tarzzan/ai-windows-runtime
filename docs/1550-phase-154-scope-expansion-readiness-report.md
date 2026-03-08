# Phase 154 - Scope Expansion Readiness Report

## Objectif

Produire un indice de readiness d'expansion scope (`blocked/watch/ready`) pour piloter l'ouverture progressive du perimetre.

## Livrables

- Nouveau module `compat_runtime.scope_expansion_readiness`.
- Nouveau schema `schemas/scope-expansion-readiness-report.schema.json`.
- Nouveau script `scripts/build-scope-expansion-readiness-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle expose un signal de readiness d'expansion scope base sur deblocage, reentree et pression P0.

## Fichiers modifies

- `src/compat_runtime/scope_expansion_readiness/cli.py`
- `schemas/scope-expansion-readiness-report.schema.json`
- `scripts/build-scope-expansion-readiness-report.sh`
- `tests/test_scope_expansion_readiness.py`
