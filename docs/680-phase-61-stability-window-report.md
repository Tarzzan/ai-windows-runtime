# Phase 61 - Stability window report

## Scope livre
- Ajout d'un module `stability_window`:
  - generation `stability-window-report.json`
  - consolidation monitor post-release, trajectory et readiness delta
  - statut `stable/watch/unstable`
- Ajout du schema dedie:
  - `schemas/stability-window-report.schema.json`
- Ajout d'un script:
  - `scripts/build-stability-window-report.sh`

## Capacites ajoutees
1. Fenetre de stabilite:
- signal unique pour qualifier la posture de stabilisation

2. Alerte:
- detection rapide des derivees de trajectoire

3. Pilotage:
- base de decision pour prioriser correctifs
