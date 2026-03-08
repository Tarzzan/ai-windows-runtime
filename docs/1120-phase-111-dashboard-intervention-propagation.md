# Phase 111 - Dashboard Intervention Propagation

## Objectif

Propager les signaux `control_efficiency` et `intervention_plan` dans le dashboard local et la regeneration policy-aware.

## Livrables

- Dashboard data enrichie avec `efficiency_band`, `efficiency_score`, `intervention_mode`.
- UI dashboard enrichie avec KPI efficiency/intervention.
- Regeneration policy-aware mise a jour pour recalculer efficiency/intervention avant packaging final.
- Tests unitaires ajoutes pour control efficiency + intervention plan.

## Impact

Le panneau de pilotage expose une posture d'intervention fiable et directement exploitable par l'equipe.

## Fichiers modifies

- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
- `tests/test_control_efficiency.py`
- `tests/test_intervention_plan.py`
