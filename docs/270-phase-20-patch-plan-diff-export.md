# Phase 20 - Patch-plan diff export

## Scope livre
- Ajout d'un module `patch_plan_diff`:
  - generation `patch-plan-diff.json`
  - comparaison `baseline` vs `current` de patch-plan
  - detection `added/removed/changed/unchanged`
  - hints de revue pour les propositions a verifier
- Ajout du schema dedie:
  - `schemas/patch-plan-diff.schema.json`
- Ajout d'un script:
  - `scripts/build-patch-plan-diff.sh`
  - support baseline optionnel via `BASELINE_PATCH_PLAN`
  - generation + validation schema de `out/patch-plan-diff.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere le diff patch-plan
  - `scripts/validate-artifacts.sh` valide cet artefact quand present
  - `scripts/build-release-bundle.sh` inclut cet artefact dans le bundle
  - `scripts/build-repro-package.sh` reference cet artefact

## Capacites ajoutees
1. Diff de propositions patch:
- identification claire des propositions ajoutees/supprimees
- detection fine des changements de priorite/titre/risque/validation

2. Support baseline optionnel:
- comparaison CI entre plan precedent et plan courant
- fallback deterministe baseline vide si non fourni

3. Aide a la revue:
- section `reviewer_focus` orientee sur les elements a verifier en priorite

## Fichiers cles
- `src/compat_runtime/patch_plan_diff/cli.py`
- `src/compat_runtime/patch_plan_diff/__init__.py`
- `schemas/patch-plan-diff.schema.json`
- `scripts/build-patch-plan-diff.sh`
- `tests/test_patch_plan_diff.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-patch-plan-diff.sh out
scripts/build-root-cause-summary.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

