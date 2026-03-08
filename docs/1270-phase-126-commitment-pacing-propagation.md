# Phase 126 - Commitment Pacing Propagation

## Objectif

Propager un mode de pacing d'engagement (`stabilize/paced/expand`) derive de l'admission, du backlog rafraichi et de la bande passante delivery.

## Livrables

- Nouveau module `compat_runtime.commitment_pacing`.
- Nouveau schema `schemas/commitment-pacing-report.schema.json`.
- Nouveau script `scripts/build-commitment-pacing-report.sh`.
- Dashboard enrichi avec intake capacity, admission state et commitment mode.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose un mode de pacing d'engagement actionnable avant la planification du cycle suivant.

## Fichiers modifies

- `src/compat_runtime/commitment_pacing/cli.py`
- `schemas/commitment-pacing-report.schema.json`
- `scripts/build-commitment-pacing-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
