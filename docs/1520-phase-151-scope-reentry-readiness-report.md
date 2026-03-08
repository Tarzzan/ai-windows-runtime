# Phase 151 - Scope Reentry Readiness Report

## Objectif

Produire un indice de readiness de reentree scope (`blocked/watch/ready`) pour piloter la reprise de perimetre apres stabilisation.

## Livrables

- Nouveau module `compat_runtime.scope_reentry_readiness`.
- Nouveau schema `schemas/scope-reentry-readiness-report.schema.json`.
- Nouveau script `scripts/build-scope-reentry-readiness-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle expose un signal de reentree scope priorisable selon pression P0 et readiness de transition.

## Fichiers modifies

- `src/compat_runtime/scope_reentry_readiness/cli.py`
- `schemas/scope-reentry-readiness-report.schema.json`
- `scripts/build-scope-reentry-readiness-report.sh`
- `tests/test_scope_reentry_readiness.py`
