# Phase 108 - Dashboard Control Efficiency And Intervention Propagation

## Objectif

Propager les nouveaux signaux d'efficacite de controle et de mode d'intervention jusqu'au dashboard local et aux chaines de regeneration policy-aware.

## Livrables

- Dashboard data enrichie avec `efficiency_band`, `efficiency_score`, `intervention_mode`.
- UI dashboard enrichie avec KPIs et resume qualite correspondants.
- Regeneration policy-aware mise a jour pour recalculer ces artefacts avant packaging.
- Tests unitaires ajoutes pour control efficiency et intervention plan.

## Impact

Le panneau de pilotage reflète la posture d'intervention operationnelle en continu avec les signaux les plus recents.

## Fichiers modifies

- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
- `tests/test_control_efficiency.py`
- `tests/test_intervention_plan.py`
