# Phase 17 - Productization governance gates

## Scope livré
- Publication des artefacts de gouvernance manquants:
  - `docs/contributor-runbook.md`
  - `docs/compatibility-matrix-template.md`
  - `docs/corpus-contribution-protocol.md`
  - `docs/security-review-checklist.md`
- Ajout d'un module de contrôle productisation:
  - `compat_runtime.productization.cli`
  - génère `productization-readiness.json`
- Ajout d'un schéma dédié:
  - `schemas/productization-readiness.schema.json`
- Ajout d'un script dédié:
  - `scripts/check-productization-readiness.sh`
- Intégration dans le pipeline complet:
  - `scripts/run-full-pipeline.sh` valide désormais la readiness productisation.

## Capacités ajoutées
1. Vérification automatique de présence + headings minimum pour les documents gouvernance.
2. Statut `ready` machine-readable pour gate de productisation.
3. Validation de schéma du rapport `productization-readiness.json`.

## Fichiers clés
- `src/compat_runtime/productization/cli.py`
- `src/compat_runtime/productization/__init__.py`
- `schemas/productization-readiness.schema.json`
- `scripts/check-productization-readiness.sh`
- `tests/test_productization.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/check-productization-readiness.sh out

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
