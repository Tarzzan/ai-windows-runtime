# Phase 36 - Execution burndown report

## Scope livre
- Ajout d'un module `execution_burndown`:
  - generation `execution-burndown-report.json`
  - projection de reduction des blocants par iteration
  - estimation de score readiness a horizon 1-2 iterations
- Ajout du schema dedie:
  - `schemas/execution-burndown-report.schema.json`
- Ajout d'un script:
  - `scripts/build-execution-burndown-report.sh`
  - generation + validation schema de `out/execution-burndown-report.json`

## Capacites ajoutees
1. Trajectoire d'execution:
- suivi de la pente de reduction des blocants
- estimation du nombre d'iterations pour les absorber

2. Milestones:
- cibles explicites par iteration (blocants restants + score cible)
- priorisation des efforts en cadence courte

3. Actionnabilite:
- recommandations automatiques selon le niveau de blocage
- artefact directement exploitable pour pilotage sprint runtime
