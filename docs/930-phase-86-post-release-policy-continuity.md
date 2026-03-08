# Phase 86 - Post-Release Policy Continuity

## Objectif

Propager les signaux `release_policy_*` apres signoff pour conserver une traçabilite continue jusqu'aux artefacts d'incident.

## Livrables

- `post-release-monitor-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - escalation `monitor_status=critical` si `release_policy_status=fail`
- `incident-feedback-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`

## Fichiers modifies

- `src/compat_runtime/post_release_monitor/cli.py`
- `src/compat_runtime/incident_feedback/cli.py`
- `schemas/post-release-monitor-report.schema.json`
- `schemas/incident-feedback-report.schema.json`
- `tests/test_post_release_monitor.py`
- `tests/test_incident_feedback.py`

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_post_release_monitor.py tests/test_incident_feedback.py tests/test_delivery_signoff.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
```

