# Phase 42 - Remediation sprint report

## Scope livre
- Ajout d'un module `remediation_sprint`:
  - generation `remediation-sprint-report.json`
  - distribution des taches en buckets `sprint_now/sprint_next/backlog`
  - correlation avec burndown et forecast
- Ajout du schema dedie:
  - `schemas/remediation-sprint-report.schema.json`
- Ajout d'un script:
  - `scripts/build-remediation-sprint-report.sh`

## Capacites ajoutees
1. Planification sprint:
- priorisation claire des efforts de remediation par vague

2. Pilotage execution:
- lecture immediate des charges critiques du sprint en cours

3. Projection:
- alignement direct avec horizon de convergence release
