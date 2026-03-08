# Phase 105 - Dashboard Temperature And Control Propagation

## Objectif

Propager temperature et control mode dans le dashboard local et dans la regeneration policy-aware de fin de pipeline.

## Livrables

- Dashboard data enrichie avec `temperature`, `temperature_index`, `control_mode`.
- UI dashboard enrichie avec KPI et resume qualite correspondants.
- Regeneration post-policy mise a jour pour recalculer temperature/control apres refresh launch-readiness.
- Tests unitaires ajoutes pour temperature/control.

## Impact

Le panneau de pilotage local reflete l'etat de controle le plus recent du run avec les signaux de temperature et gouvernance.

## Fichiers modifies

- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
- `tests/test_delivery_temperature.py`
- `tests/test_control_recommendation.py`
