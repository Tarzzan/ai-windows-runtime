# Phase 37 - Validation command pack

## Scope livre
- Ajout d'un module `validation_command_pack`:
  - generation `validation-command-pack.json`
  - dedup/ordonnancement des commandes de validation
  - constitution de packs `quick`, `blocking`, `full`
- Ajout du schema dedie:
  - `schemas/validation-command-pack.schema.json`
- Ajout d'un script:
  - `scripts/build-validation-command-pack.sh`
  - generation + validation schema de `out/validation-command-pack.json`

## Capacites ajoutees
1. Runbook de validation:
- traduction des taches d'iteration en commandes executables
- priorisation par criticite (`P0/P1/P2`, bloquant/non bloquant)

2. Packs operationnels:
- pack rapide pour feedback court
- pack bloquant pour gates release
- pack complet pour revue finale

3. Standardisation:
- reduction des variations d'execution manuelle
- base commune entre triage, dev et release review
