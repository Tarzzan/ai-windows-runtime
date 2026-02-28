# Phase 18 - Deterministic repro package

## Scope livre
- Ajout d'un module `repro_package`:
  - generation `repro-package.json`
  - consolidation des cibles en echec depuis:
    - `execution-report.json`
    - `compatibility-matrix.json`
    - `alpha-release-checklist.json`
  - inventaire des artefacts avec checksum `sha256`
  - empreinte d'environnement (OS, release, machine, version Python)
- Ajout du schema dedie:
  - `schemas/repro-package.schema.json`
- Ajout d'un script:
  - `scripts/build-repro-package.sh`
  - genere et valide `out/repro-package.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide `repro-package.json`
  - `scripts/validate-artifacts.sh` valide ce nouvel artefact quand present
  - `scripts/build-release-bundle.sh` inclut `repro-package.json` dans le bundle

## Capacites ajoutees
1. Package de reproduction deterministe:
- agrege les echecs scenario/checklist/pipeline
- fournit un identifiant stable `deterministic_id`

2. Evidence packaging pour debug collaboratif:
- inventaire des artefacts disponibles/manquants
- hash des fichiers presents pour traçabilite

3. Steps de reproduction standardises:
- commandes recommandees pour regenerer un contexte complet
- notes d'usage pour contribution issue/triage

## Fichiers cles
- `src/compat_runtime/repro_package/cli.py`
- `src/compat_runtime/repro_package/__init__.py`
- `schemas/repro-package.schema.json`
- `scripts/build-repro-package.sh`
- `tests/test_repro_package.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

