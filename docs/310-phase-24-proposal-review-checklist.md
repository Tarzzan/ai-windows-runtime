# Phase 24 - Proposal review checklist

## Scope livre
- Ajout d'un module `proposal_review_checklist`:
  - generation `proposal-review-checklist.json`
  - checklist de revue par proposition (`pass/warn/fail/todo`)
  - statut `ready_for_approval` derive des items requis
  - actions de revue derivees automatiquement
- Ajout du schema dedie:
  - `schemas/proposal-review-checklist.schema.json`
- Ajout d'un script:
  - `scripts/build-proposal-review-checklist.sh`
  - generation + validation schema de `out/proposal-review-checklist.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Gate de revue engineering:
- verification des preconditions requises (provenance/rollback/test-impact)
- comptage des items requis non conformes

2. Revue proposition-level:
- statut de liaison evidence gap/provenance
- verification du plan de rollback adapte a la criticite
- item explicite `todo` pour propositions ajoutees/modifiees

3. Gouvernance d'approbation:
- artefact structure pour decision `ready_for_approval`
- trace de revue exploitable en CI et release packaging

## Fichiers cles
- `src/compat_runtime/proposal_review_checklist/cli.py`
- `src/compat_runtime/proposal_review_checklist/__init__.py`
- `schemas/proposal-review-checklist.schema.json`
- `scripts/build-proposal-review-checklist.sh`
- `tests/test_proposal_review_checklist.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-proposal-review-checklist.sh out
scripts/build-rollback-hints.sh out
scripts/build-test-impact-report.sh out
scripts/build-proposal-provenance.sh out
scripts/build-patch-plan-diff.sh out
scripts/build-root-cause-summary.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

