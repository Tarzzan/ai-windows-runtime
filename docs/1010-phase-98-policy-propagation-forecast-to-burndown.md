# Phase 98 - Policy Propagation Forecast To Burndown

## Objectif

Propager `release_policy_*` dans la chaine pre-planning quantifiee:

- `release-forecast-report`
- `readiness-scorecard-report`
- `execution-burndown-report`

## Livrables

- `release-forecast-report.summary`:
  - `release_policy_status`
  - `release_policy_failures`
- `readiness-scorecard-report.summary`:
  - `release_policy_status`
  - `release_policy_failures`
- `execution-burndown-report.summary`:
  - `release_policy_status`
  - `release_policy_failures`

## Orchestration

Apres `check-release-policy`, regeneration tardive ajoutee:

1. `build-release-forecast-report.sh`
2. `build-readiness-scorecard-report.sh`
3. `build-execution-burndown-report.sh`
4. puis chaine planning/comms/prelaunch/packet deja en place.

## Fichiers modifies

- `src/compat_runtime/release_forecast/cli.py`
- `src/compat_runtime/readiness_scorecard/cli.py`
- `src/compat_runtime/execution_burndown/cli.py`
- `scripts/build-release-forecast-report.sh`
- `schemas/release-forecast-report.schema.json`
- `schemas/readiness-scorecard-report.schema.json`
- `schemas/execution-burndown-report.schema.json`
- `tests/test_release_forecast.py`
- `tests/test_readiness_scorecard.py`
- `tests/test_execution_burndown.py`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

