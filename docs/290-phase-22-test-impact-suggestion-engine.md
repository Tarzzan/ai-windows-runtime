# Phase 22 - Test impact suggestion engine

## Scope livre
- Ajout d'un module `test_impact`:
  - generation `test-impact-report.json`
  - mapping des propositions patch vers suites de tests ciblees
  - priorisation des suites selon priorite patch (`P0/P1/P2`)
  - estimation d'effort (`estimated_minutes`) + commande suggeree
- Ajout du schema dedie:
  - `schemas/test-impact-report.schema.json`
- Ajout d'un script:
  - `scripts/build-test-impact-report.sh`
  - generation + validation schema de `out/test-impact-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Suggestion automatique de suites:
- selection des suites a partir des categories de gaps
- commande d'execution recommandee par suite

2. Priorisation de la validation:
- tri des suites en fonction de la criticite des proposals
- focus explicite sur les suites `P0`

3. Couverture et actions:
- verification de couverture des categories impactees
- alignement avec `root-cause-summary`
- hints d'action si provenance faible ou categorie non couverte

## Fichiers cles
- `src/compat_runtime/test_impact/cli.py`
- `src/compat_runtime/test_impact/__init__.py`
- `schemas/test-impact-report.schema.json`
- `scripts/build-test-impact-report.sh`
- `tests/test_test_impact.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-test-impact-report.sh out
scripts/build-proposal-provenance.sh out
scripts/build-patch-plan-diff.sh out
scripts/build-root-cause-summary.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

