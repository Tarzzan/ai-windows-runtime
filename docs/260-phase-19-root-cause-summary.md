# Phase 19 - Root cause summary and clustering

## Scope livre
- Ajout d'un module `root_cause`:
  - generation `root-cause-summary.json`
  - clustering des gaps par categorie
  - correlation gaps <-> priorites patch-plan (P0/P1/P2)
  - suggestions d'action pour triage
- Ajout du schema dedie:
  - `schemas/root-cause-summary.schema.json`
- Ajout d'un script:
  - `scripts/build-root-cause-summary.sh`
  - genere et valide `out/root-cause-summary.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere le root-cause summary
  - `scripts/validate-artifacts.sh` valide ce nouvel artefact quand present
  - `scripts/build-release-bundle.sh` inclut l'artefact dans le bundle

## Capacites ajoutees
1. Vue root-cause agrégée:
- causes principales triees par frequence
- distribution des severites et des priorites liees

2. Analyse par scenario:
- synthese base/runtime
- top categories et top gaps avec priorite associee

3. Triage actionnable:
- actions recommandees derivees des categories dominantes
- orientation prioritaire sur les gaps P0

## Fichiers cles
- `src/compat_runtime/root_cause/cli.py`
- `src/compat_runtime/root_cause/__init__.py`
- `schemas/root-cause-summary.schema.json`
- `scripts/build-root-cause-summary.sh`
- `tests/test_root_cause_summary.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-root-cause-summary.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

