# Phase 23 - Rollback hint generation

## Scope livre
- Ajout d'un module `rollback_hints`:
  - generation `rollback-hints.json`
  - classement des rollbacks (`full/partial/minimal`) selon priorite + risque
  - signaux de declenchement de rollback par proposition
  - etapes de rollback et commandes de validation
- Ajout du schema dedie:
  - `schemas/rollback-hints.schema.json`
- Ajout d'un script:
  - `scripts/build-rollback-hints.sh`
  - generation + validation schema de `out/rollback-hints.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Strategie de rollback proposal-level:
- niveau de rollback determine par `priority/risk`
- triggers explicites pour decider un rollback

2. Plan de retour arriere actionnable:
- prechecks, etapes, commandes de revalidation
- adaptation minimale par categorie de gap

3. Gouvernance livraison:
- artefact versionne et valide par schema
- inclus dans tous les livrables pipeline/release/repro

## Fichiers cles
- `src/compat_runtime/rollback_hints/cli.py`
- `src/compat_runtime/rollback_hints/__init__.py`
- `schemas/rollback-hints.schema.json`
- `scripts/build-rollback-hints.sh`
- `tests/test_rollback_hints.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
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

