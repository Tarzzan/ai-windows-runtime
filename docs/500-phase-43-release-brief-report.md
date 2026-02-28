# Phase 43 - Release brief report

## Scope livre
- Ajout d'un module `release_brief`:
  - generation `release-brief-report.json`
  - synthese executive des signaux readiness/pilot/forecast/risks
  - headline unique exploitable en communication release
- Ajout du schema dedie:
  - `schemas/release-brief-report.schema.json`
- Ajout d'un script:
  - `scripts/build-release-brief-report.sh`

## Capacites ajoutees
1. Communication:
- resume lisible pour stakeholders non techniques

2. Decision support:
- consolidation du contexte critique dans un artefact court

3. Risques majeurs:
- extraction automatique des top risques de watchlist
