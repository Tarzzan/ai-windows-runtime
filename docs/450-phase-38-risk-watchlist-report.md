# Phase 38 - Risk watchlist report

## Scope livre
- Ajout d'un module `risk_watchlist`:
  - generation `risk-watchlist-report.json`
  - consolidation des signaux proposal risk, hooks manquants et incidents runtime
  - tri des entrees de risque par priorite `P0/P1/P2`
- Ajout du schema dedie:
  - `schemas/risk-watchlist-report.schema.json`
- Ajout d'un script:
  - `scripts/build-risk-watchlist-report.sh`
  - generation + validation schema de `out/risk-watchlist-report.json`

## Capacites ajoutees
1. Watchlist unifiee:
- une vue unique des risques critiques a traiter
- correlation entre risque projet et risques instrumentation runtime

2. Priorisation:
- entree P0/P1/P2 avec evidence explicite
- support direct au rituel de triage

3. Gouvernance:
- meilleure tracabilite des risques avant decision de promotion
- artefact simple a partager en revue technique
