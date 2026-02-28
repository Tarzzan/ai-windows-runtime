# Phase 25 - Patch template library

## Scope livre
- Ajout d'un module `patch_template_library`:
  - generation `patch-template-catalog.json`
  - bibliotheque de templates de patch par domaine de compatibilite
  - mapping categories de gaps -> templates
  - analytics d'usage (volumetrie + priorites associees)
- Ajout du schema dedie:
  - `schemas/patch-template-catalog.schema.json`
- Ajout d'un script:
  - `scripts/build-patch-template-catalog.sh`
  - generation + validation schema de `out/patch-template-catalog.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Template catalog centralise:
- definition de templates par type de blocage (loader/com/network/etc.)
- metadata standardisees (strategie, risque, validation focus)

2. Mapping et coverage:
- liaison automatique des gaps detectes vers un template cible
- detection explicite des categories non mappees

3. Pilotage engineering:
- distribution des priorites par template
- exemples de `gap_id` par template pour triage rapide

## Fichiers cles
- `src/compat_runtime/patch_template_library/cli.py`
- `src/compat_runtime/patch_template_library/__init__.py`
- `schemas/patch-template-catalog.schema.json`
- `scripts/build-patch-template-catalog.sh`
- `tests/test_patch_template_library.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-patch-template-catalog.sh out
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

