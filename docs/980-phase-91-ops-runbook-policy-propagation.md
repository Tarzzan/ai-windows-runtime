# Phase 91 - Ops Runbook Policy Propagation

## Objectif

Etendre les signaux `release_policy_*` au runbook operationnel pour que la readiness terrain reflète la conformité policy.

## Livrables

- `ops-runbook-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - `runbook_readiness=needs_attention` si `release_policy_status=fail`

## Fichiers modifies

- `src/compat_runtime/ops_runbook/cli.py`
- `schemas/ops-runbook-report.schema.json`
- `tests/test_ops_runbook.py`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

