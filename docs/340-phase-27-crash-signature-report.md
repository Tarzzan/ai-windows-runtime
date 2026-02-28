# Phase 27 - Crash signature report

## Scope livre
- Ajout d'un module `crash_signatures`:
  - generation `crash-signature-report.json`
  - extraction de signatures d'anomalies depuis traces base + runtime
  - clustering des messages normalises en signatures stables
  - classification de priorite `P0/P1/P2` pour triage
- Ajout du schema dedie:
  - `schemas/crash-signature-report.schema.json`
- Ajout d'un script:
  - `scripts/build-crash-signature-report.sh`
  - generation + validation schema de `out/crash-signature-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle/manifeste
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Signature extraction:
- detection d'evenements anormaux (severity high + mots-clefs crash/timeout/error)
- normalisation des messages pour deduplication fiable

2. Crash triage:
- signatures avec `kind`, `category`, `count`, `sources`, `first_seen/last_seen`
- priorisation automatique pour focaliser les investigations

3. Gouvernance artefacts:
- schema de validation dedie et rapports de conformite
- inclusion dans tous les flux de livraison (pipeline/release/repro)

## Fichiers cles
- `src/compat_runtime/crash_signatures/cli.py`
- `src/compat_runtime/crash_signatures/__init__.py`
- `schemas/crash-signature-report.schema.json`
- `scripts/build-crash-signature-report.sh`
- `tests/test_crash_signatures.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
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

