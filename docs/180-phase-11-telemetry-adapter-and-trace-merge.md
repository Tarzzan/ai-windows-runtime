# Phase 11 - Telemetry adapter et fusion de traces

## Scope livré
- Ajout d'un adaptateur Python `compat_runtime.telemetry_adapter`:
  - convertit un artefact `runtime telemetry` en artefact `trace` normalisé.
  - option de filtrage `--errors-only`.
  - option de fusion avec trace existante `--base-trace`.
- Extension du pipeline d'analyse:
  - `gap_detector` enrichi pour les catégories `sync`, `file`, `registry`.
  - `patch_orchestrator` enrichi avec playbook dédié pour ces catégories.
- Ajout d'un schéma d'entrée telemetry:
  - `schemas/runtime-telemetry.schema.json`.
- Ajout d'un exemple d'artefact telemetry:
  - `examples/sample-runtime-telemetry.json`.

## Capacités ajoutées
1. Import des événements runtime simulés dans le pipeline `trace -> gaps -> patch-plan`.
2. Unification des traces log textuelles et télémétrie runtime en un flux d'analyse unique.
3. Priorisation des erreurs registry/file/sync dans la planification de correctifs.

## Fichiers clés
- `src/compat_runtime/telemetry_adapter/cli.py`
- `src/compat_runtime/gap_detector/cli.py`
- `src/compat_runtime/patch_orchestrator/cli.py`
- `schemas/runtime-telemetry.schema.json`
- `schemas/trace.schema.json`
- `tests/test_runtime_telemetry_adapter.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
