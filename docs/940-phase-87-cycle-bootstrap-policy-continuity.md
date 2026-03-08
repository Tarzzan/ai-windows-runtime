# Phase 87 - Cycle Bootstrap Policy Continuity

## Objectif

Etendre la propagation des signaux `release_policy_*` jusqu'aux artefacts de transition de cycle.

## Livrables

- `backlog-refresh-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
- `next-cycle-bootstrap-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - blocage explicite si `release_policy_status == fail`

## Fichiers modifies

- `src/compat_runtime/backlog_refresh/cli.py`
- `src/compat_runtime/next_cycle_bootstrap/cli.py`
- `schemas/backlog-refresh-report.schema.json`
- `schemas/next-cycle-bootstrap-report.schema.json`
- `tests/test_backlog_refresh.py`
- `tests/test_next_cycle_bootstrap.py`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_backlog_refresh.py tests/test_next_cycle_bootstrap.py tests/test_incident_feedback.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
```

