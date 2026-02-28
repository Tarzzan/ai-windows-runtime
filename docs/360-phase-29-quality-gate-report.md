# Phase 29 - Quality gate aggregation report

## Scope livre
- Ajout d'un module `quality_gate`:
  - generation `quality-gate-report.json`
  - aggregation des artefacts execution/kpi/trend/proposal-risk/crash/installer/review/productization
  - calcul d'un gate global `pass/warn/fail` avec checks requis vs optionnels
  - recommandations d'actions selon le niveau de gate
- Ajout du schema dedie:
  - `schemas/quality-gate-report.schema.json`
- Ajout d'un script:
  - `scripts/build-quality-gate-report.sh`
  - generation + validation schema de `out/quality-gate-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Gate unifie:
- un point d'entree unique pour trancher readiness release
- lecture consolidee des signaux critiques et non critiques

2. Politique de checks:
- checks requis (pipeline/kpi/crash/review/productization) bloquants
- checks optionnels (trend/proposal-risk/installer) remontes en warning

3. Actionnabilite immediate:
- actions de remediation explicites selon `fail` ou `warn`
- artefact exploitable directement en CI, revue et triage

## Fichiers cles
- `src/compat_runtime/quality_gate/cli.py`
- `src/compat_runtime/quality_gate/__init__.py`
- `schemas/quality-gate-report.schema.json`
- `scripts/build-quality-gate-report.sh`
- `tests/test_quality_gate.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-quality-gate-report.sh out
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
