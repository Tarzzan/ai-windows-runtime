# Phase 90 - Prelaunch Policy Propagation

## Objectif

Propager `release_policy_status` et `release_policy_failures` dans la chaine prelaunch (`handoff-checklist` -> `launch-readiness`).

## Livrables

- `handoff-checklist-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - nouveau check `release_policy_alignment`
- `launch-readiness-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - blocage explicite si `release_policy_status == fail`

## Fichiers modifies

- `src/compat_runtime/handoff_checklist/cli.py`
- `src/compat_runtime/launch_readiness/cli.py`
- `schemas/handoff-checklist-report.schema.json`
- `schemas/launch-readiness-report.schema.json`
- `tests/test_handoff_checklist.py`
- `tests/test_launch_readiness.py`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

