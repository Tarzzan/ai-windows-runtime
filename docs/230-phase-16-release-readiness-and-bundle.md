# Phase 16 - Release readiness et bundle packaging

## Scope livré
- Ajout d'un module `release_readiness`:
  - génération `compatibility-matrix.json`
  - génération `alpha-release-checklist.json`
  - génération `release-bundle-manifest.json` (checksum inventory)
- Ajout des schémas dédiés:
  - `schemas/compatibility-matrix.schema.json`
  - `schemas/alpha-release-checklist.schema.json`
  - `schemas/release-bundle-manifest.schema.json`
- Ajout d'un script de packaging:
  - `scripts/build-release-bundle.sh`
  - produit un dossier bundle avec artefacts consolidés
- Intégration dans le pipeline:
  - `scripts/run-full-pipeline.sh` génère et valide les artefacts release readiness
  - `scripts/validate-artifacts.sh` valide ces artefacts quand présents

## Capacités ajoutées
1. Décision de readiness structurée (`release_ready`) basée sur:
- statut pipeline
- validations base/runtime
- niveau de risque KPI

2. Checklist alpha actionnable:
- items requis / optionnels
- statut `pass/fail/warn/todo`

3. Manifeste de bundle:
- empreintes `sha256`
- tailles des artefacts
- liste des artefacts manquants

## Fichiers clés
- `src/compat_runtime/release_readiness/cli.py`
- `src/compat_runtime/release_readiness/__init__.py`
- `schemas/compatibility-matrix.schema.json`
- `schemas/alpha-release-checklist.schema.json`
- `schemas/release-bundle-manifest.schema.json`
- `scripts/build-release-bundle.sh`
- `tests/test_release_readiness.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
