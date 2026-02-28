# Phase 12 - Schema validation pipeline

## Scope livré
- Ajout d'un validateur JSON natif (sans dépendance externe) pour les artefacts du projet:
  - `compat_runtime.schema_validator.engine`
  - `compat_runtime.schema_validator.cli`
- Validation prise en charge:
  - `type` (incluant unions simples, ex: `["string", "null"]`)
  - `required`
  - `properties`
  - `items` (tableaux)
- Ajout d'une commande scriptable:
  - `compat-validate`
- Ajout d'un script batch de validation:
  - `scripts/validate-artifacts.sh`
- Ajout de tests unitaires dédiés au validateur.

## Capacités ajoutées
1. Vérification automatique de conformité des artefacts:
- `trace.json`
- `gaps.json`
- `patch-plan.json`
- `runtime-telemetry.json` (schéma dédié)

2. Rapports machine-readable:
- statut `valid`
- liste d'erreurs annotées par chemin

## Fichiers clés
- `src/compat_runtime/schema_validator/engine.py`
- `src/compat_runtime/schema_validator/cli.py`
- `scripts/validate-artifacts.sh`
- `tests/test_schema_validator.py`
- `pyproject.toml`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

python -m compat_runtime.trace_collector.cli --input examples/sample-trace.log --output out/trace.json
python -m compat_runtime.gap_detector.cli --trace out/trace.json --output out/gaps.json
python -m compat_runtime.patch_orchestrator.cli --gaps out/gaps.json --output out/patch-plan.json
scripts/validate-artifacts.sh out

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
