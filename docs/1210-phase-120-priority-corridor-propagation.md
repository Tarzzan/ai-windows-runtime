# Phase 120 - Priority Corridor Propagation

## Objectif

Propager un corridor de priorite (`p0_only/p0_p1/full`) base sur throttle, focus P0 et watchlist risques.

## Livrables

- Nouveau module `compat_runtime.priority_corridor`.
- Nouveau schema `schemas/priority-corridor-report.schema.json`.
- Nouveau script `scripts/build-priority-corridor-report.sh`.
- Dashboard enrichi avec surcharge owner, throttle mode et priority corridor.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose clairement le couloir de priorite actif pour la phase courante.

## Fichiers modifies

- `src/compat_runtime/priority_corridor/cli.py`
- `schemas/priority-corridor-report.schema.json`
- `scripts/build-priority-corridor-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
