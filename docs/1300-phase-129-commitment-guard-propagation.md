# Phase 129 - Commitment Guard Propagation

## Objectif

Propager un guard d'engagement (`strict/moderate/adaptive`) derive de la fenetre d'admission, de la pression P0 watchlist et du statut policy.

## Livrables

- Nouveau module `compat_runtime.commitment_guard`.
- Nouveau schema `schemas/commitment-guard-report.schema.json`.
- Nouveau script `scripts/build-commitment-guard-report.sh`.
- Dashboard enrichi avec scope budget, admission window et commitment guard.
- Integration policy-aware refresh + repro package + release bundle.

## Impact

Le panneau de controle expose un niveau de guard d'engagement exploitable avant arbitrage de cycle.

## Fichiers modifies

- `src/compat_runtime/commitment_guard/cli.py`
- `schemas/commitment-guard-report.schema.json`
- `scripts/build-commitment-guard-report.sh`
- `scripts/build_dashboard_data.py`
- `dashboard-template/assets/app.js`
- `scripts/build-repro-package.sh`
- `scripts/validate-artifacts.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
