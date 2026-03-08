# Phase 148 - Transition Readiness Index Report

## Objectif

Produire un indice de readiness de transition (`blocked/watch/ready`) pour piloter les passages de scope avec un score explicite.

## Livrables

- Nouveau module `compat_runtime.transition_readiness_index`.
- Nouveau schema `schemas/transition-readiness-index-report.schema.json`.
- Nouveau script `scripts/build-transition-readiness-index-report.sh`.
- Integration dans pipeline, bundle, repro package et validation.

## Impact

Le panneau de controle expose un signal readiness actionnable avant chaque decision de transition.

## Fichiers modifies

- `src/compat_runtime/transition_readiness_index/cli.py`
- `schemas/transition-readiness-index-report.schema.json`
- `scripts/build-transition-readiness-index-report.sh`
- `tests/test_transition_readiness_index.py`
