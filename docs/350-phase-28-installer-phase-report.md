# Phase 28 - Installer phase report

## Scope livre
- Ajout d'un module `installer_phases`:
  - generation `installer-phase-report.json`
  - detection de phases d'installation (bootstrap/network/registry/file/finalize)
  - timeline normalisee des evenements base + runtime
  - rollup par phase avec statut `progress/success/error`
- Ajout du schema dedie:
  - `schemas/installer-phase-report.schema.json`
- Ajout d'un script:
  - `scripts/build-installer-phase-report.sh`
  - generation + validation schema de `out/installer-phase-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Installer timeline:
- sequence consolidée des marqueurs d'installation depuis traces base/runtime
- conservation des messages, categories et statuts interpretes

2. Phase rollup:
- volumetrie par phase (`events/errors/success/progress`)
- `phase_status` derive pour identifier les points de blocage

3. Triage d'installation:
- actions automatiques pour prioriser les phases en erreur
- artefact directement exploitable en debug/repro

## Fichiers cles
- `src/compat_runtime/installer_phases/cli.py`
- `src/compat_runtime/installer_phases/__init__.py`
- `schemas/installer-phase-report.schema.json`
- `scripts/build-installer-phase-report.sh`
- `tests/test_installer_phases.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-installer-phase-report.sh out
scripts/build-crash-signature-report.sh out
scripts/build-proposal-risk-report.sh out
scripts/build-proposal-review-checklist.sh out
scripts/build-rollback-hints.sh out
scripts/build-test-impact-report.sh out
scripts/build-proposal-provenance.sh out
scripts/build-patch-plan-diff.sh out
scripts/build-root-cause-summary.sh out
scripts/build-patch-template-catalog.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

