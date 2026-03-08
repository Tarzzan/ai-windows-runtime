# Phase 88 - Closure Policy Continuity

## Objectif

Propager les signaux `release_policy_*` dans les artefacts de cloture (`release-retrospective` et `stability-window`).

## Livrables

- `release-retrospective-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - lecons additionnelles si policy en echec
- `stability-window-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
  - `window_status=unstable` si policy en echec

## Fichiers modifies

- `src/compat_runtime/release_retrospective/cli.py`
- `src/compat_runtime/stability_window/cli.py`
- `schemas/release-retrospective-report.schema.json`
- `schemas/stability-window-report.schema.json`
- `tests/test_release_retrospective.py`
- `tests/test_stability_window.py`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_release_retrospective.py tests/test_stability_window.py tests/test_next_cycle_bootstrap.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
```

