# Phase 33 - Iteration plan report

## Scope livre
- Ajout d'un module `iteration_plan`:
  - generation `iteration-plan-report.json`
  - synthese operationnelle depuis `release-decision`, `hook-backlog`, `proposal-risk`, `test-impact`
  - construction d'une liste de taches ordonnees `P0/P1/P2`
  - estimation d'effort et marquage des taches bloquantes
- Ajout du schema dedie:
  - `schemas/iteration-plan-report.schema.json`
- Ajout d'un script:
  - `scripts/build-iteration-plan-report.sh`
  - generation + validation schema de `out/iteration-plan-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans bundle + repro package
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Planification automatique:
- passage automatique du diagnostic a un plan d'execution concret
- priorisation explicite des blocants release et hooks manquants

2. Orchestration des validations:
- rattachement des commandes de test suggerees aux taches
- alignement direct avec le test-impact existant

3. Pilotage sprint runtime:
- effort total estime pour dimensionner l'iteration suivante
- sortie directement exploitable en grooming/triage quotidien

## Fichiers cles
- `src/compat_runtime/iteration_plan/cli.py`
- `src/compat_runtime/iteration_plan/__init__.py`
- `schemas/iteration-plan-report.schema.json`
- `scripts/build-iteration-plan-report.sh`
- `tests/test_iteration_plan.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-iteration-plan-report.sh out
scripts/build-hook-backlog-report.sh out
scripts/build-runtime-signal-report.sh out
scripts/build-release-decision-report.sh out
scripts/build-quality-gate-report.sh out
scripts/build-installer-phase-report.sh out
scripts/build-crash-signature-report.sh out
scripts/build-proposal-risk-report.sh out
scripts/build-proposal-review-checklist.sh out
scripts/build-rollback-hints.sh out
scripts/build-test-impact-report.sh out
scripts/build-proposal-provenance.sh out
scripts/build-patch-plan-diff.sh out
scripts/build-root-cause-summary.sh out
scripts/build-patch-template-catalog.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
