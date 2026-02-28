# Phase 26 - Proposal risk scoring

## Scope livre
- Ajout d'un module `proposal_risk`:
  - generation `proposal-risk-report.json`
  - scoring de risque par proposition
  - classification `low/medium/high`
  - drivers explicites de scoring pour audit reviewer
- Ajout du schema dedie:
  - `schemas/proposal-risk-report.schema.json`
- Ajout d'un script:
  - `scripts/build-proposal-risk-report.sh`
  - generation + validation schema de `out/proposal-risk-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts
  - `scripts/build-proposal-review-checklist.sh` l'utilise pour la gate de revue

## Capacites ajoutees
1. Scoring de risque proposition-level:
- prise en compte de `priority` + `risk` declaré
- ajustement par confiance de provenance
- ajustement par churn (`added/changed`) et niveau de rollback
- ajustement par criticite des suites de test impactees

2. Classification et actions:
- niveau de risque derive (`high/medium/low`)
- actions de revue/gating proposees automatiquement

3. Traçabilite de revue:
- liste des drivers de score par proposition
- integration directe avec la checklist d'approbation

## Fichiers cles
- `src/compat_runtime/proposal_risk/cli.py`
- `src/compat_runtime/proposal_risk/__init__.py`
- `schemas/proposal-risk-report.schema.json`
- `scripts/build-proposal-risk-report.sh`
- `tests/test_proposal_risk.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
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

