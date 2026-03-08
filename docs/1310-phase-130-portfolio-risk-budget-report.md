# Phase 130 - Portfolio Risk Budget Report

## Objectif

Ajouter un signal de budget risque portefeuille (`conservative/balanced/aggressive`) derive du commitment guard, de la pression P0 watchlist et du readiness score.

## Livrables

- Nouveau module `compat_runtime.portfolio_risk_budget`.
- Nouveau schema `schemas/portfolio-risk-budget-report.schema.json`.
- Nouveau script `scripts/build-portfolio-risk-budget-report.sh`.
- Integration generation/validation dans pipeline et release bundle.

## Impact

Le pilotage dispose d'une enveloppe de risque explicite pour cadrer les arbitrages de portefeuille.

## Fichiers modifies

- `src/compat_runtime/portfolio_risk_budget/cli.py`
- `schemas/portfolio-risk-budget-report.schema.json`
- `scripts/build-portfolio-risk-budget-report.sh`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
