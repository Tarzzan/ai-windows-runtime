# Phase 157 - Scope Acceleration Readiness Report

## Objectif

Produire un indice de readiness d'acceleration scope (`blocked/watch/ready`) pour piloter une acceleration progressive du perimetre.

## Livrables

- Nouveau module `compat_runtime.scope_acceleration_readiness`.
- Nouveau schema `schemas/scope-acceleration-readiness-report.schema.json`.
- Nouveau script `scripts/build-scope-acceleration-readiness-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle expose un signal de readiness d'acceleration scope base sur gate d'expansion, readiness d'expansion et pression P0.

## Fichiers modifies

- `src/compat_runtime/scope_acceleration_readiness/cli.py`
- `schemas/scope-acceleration-readiness-report.schema.json`
- `scripts/build-scope-acceleration-readiness-report.sh`
- `tests/test_scope_acceleration_readiness.py`
