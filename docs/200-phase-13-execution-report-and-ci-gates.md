# Phase 13 - Execution report et CI gates

## Scope livré
- Ajout d'un générateur de rapport exécutable:
  - `compat_runtime.reporting.cli`
  - sortie `execution-report.json` (counts + statut + validations)
- Ajout d'un schéma dédié:
  - `schemas/execution-report.schema.json`
- Ajout d'un script de pipeline complet:
  - `scripts/run-full-pipeline.sh`
  - exécute trace/gaps/plan (base + runtime), validations de schéma, puis rapport final
- Renforcement de la CI:
  - exécution smoke runtime-core
  - exécution du pipeline complet

## Capacités ajoutées
1. Artefact de synthèse machine-readable pour chaque run.
2. Gate unique reproductible local/CI pour vérifier le flux de bout en bout.
3. Couverture tests pour la génération de rapport.

## Fichiers clés
- `src/compat_runtime/reporting/cli.py`
- `src/compat_runtime/reporting/__init__.py`
- `schemas/execution-report.schema.json`
- `scripts/run-full-pipeline.sh`
- `tests/test_reporting.py`
- `.github/workflows/ci.yml`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
