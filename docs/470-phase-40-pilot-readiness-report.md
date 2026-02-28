# Phase 40 - Pilot readiness report

## Scope livre
- Ajout d'un module `pilot_readiness`:
  - generation `pilot-readiness-report.json`
  - recommandation finale `ready/limited_pilot/not_ready`
  - synthese des blocants restants avant ouverture pilote
- Ajout du schema dedie:
  - `schemas/pilot-readiness-report.schema.json`
- Ajout d'un script:
  - `scripts/build-pilot-readiness-report.sh`
  - generation + validation schema de `out/pilot-readiness-report.json`

## Capacites ajoutees
1. Decision orientee pilote:
- traduction des signaux techniques en recommandation operationnelle
- prise en compte conjointe quality gate, scorecard, forecast et risque

2. Blocants explicites:
- extraction des blockers requis encore ouverts
- base claire pour plan de remediation pre-pilote

3. Cadre de lancement:
- recommande un mode de lancement proportionne au niveau de maturite
- facilite l'alignement entre engineering et produit avant ouverture terrain
