# Phase 95 - Policy Propagation Risk To Sprint

## Objectif

Etendre les signaux `release_policy_*` sur la chaine planning (`risk-watchlist` -> `ownership-assignment` -> `remediation-sprint`) et re-evaluer les artefacts downstream en fin de pipeline.

## Livrables

- `risk-watchlist-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
- `ownership-assignment-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
- `remediation-sprint-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`

## Orchestration

- Apres `check-release-policy`, regeneration:
  - `build-risk-watchlist-report.sh`
  - `build-ownership-assignment-report.sh`
  - `build-remediation-sprint-report.sh`
  - puis chaine communication/prelaunch/packet.

## Fichiers modifies

- `src/compat_runtime/risk_watchlist/cli.py`
- `src/compat_runtime/ownership_assignment/cli.py`
- `src/compat_runtime/remediation_sprint/cli.py`
- `scripts/build-risk-watchlist-report.sh`
- `schemas/risk-watchlist-report.schema.json`
- `schemas/ownership-assignment-report.schema.json`
- `schemas/remediation-sprint-report.schema.json`
- `tests/test_risk_watchlist.py`
- `tests/test_ownership_assignment.py`
- `tests/test_remediation_sprint.py`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

