# Phase 35 - Readiness scorecard report

## Scope livre
- Ajout d'un module `readiness_scorecard`:
  - generation `readiness-scorecard-report.json`
  - calcul d'un score global de readiness (0-100)
  - classification `red/amber/green`
  - indicateur `release_candidate` et decomposition des facteurs de score
- Ajout du schema dedie:
  - `schemas/readiness-scorecard-report.schema.json`
- Ajout d'un script:
  - `scripts/build-readiness-scorecard-report.sh`
  - generation + validation schema de `out/readiness-scorecard-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans bundle + repro package
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Vue executive unique:
- un score quantifie pour suivre la progression release
- lecture rapide de la posture globale via bande couleur

2. Transparence du scoring:
- facteurs explicites (quality gate, decision, risque KPI, blocants, forecast)
- penalties tracables pour prioriser les efforts de correction

3. Cadence de pilotage:
- signal `release_candidate` utilisable en gate CI/review
- artefact simple a comparer entre iterations pour mesurer la convergence

## Fichiers cles
- `src/compat_runtime/readiness_scorecard/cli.py`
- `src/compat_runtime/readiness_scorecard/__init__.py`
- `schemas/readiness-scorecard-report.schema.json`
- `scripts/build-readiness-scorecard-report.sh`
- `tests/test_readiness_scorecard.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-readiness-scorecard-report.sh out
scripts/build-release-forecast-report.sh out
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
