# Phase 31 - Runtime signal report

## Scope livre
- Ajout d'un module `runtime_signals`:
  - generation `runtime-signal-report.json`
  - enrichment des signaux de panne COM/WinRT/registry/network/installer/crash-like
  - mesure de couverture des hooks runtime par domaine
  - extraction d'issues priorisables pour triage rapide
- Ajout du schema dedie:
  - `schemas/runtime-signal-report.schema.json`
- Ajout d'un script:
  - `scripts/build-runtime-signal-report.sh`
  - generation + validation schema de `out/runtime-signal-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Enrichment multi-domaines:
- lecture consolidee des traces base + runtime
- mapping des echec vers domaines operables (com/winrt/registry/network/installer/crash)

2. Visibilite hook coverage:
- suivi explicite des domaines couverts par instrumentation runtime
- ratio de couverture pour prioriser les hooks manquants

3. Triage actionnable:
- extraction d'issues severes avec contexte source/message/timestamp
- actions automatiques liees aux manques de couverture et aux erreurs critiques

## Fichiers cles
- `src/compat_runtime/runtime_signals/cli.py`
- `src/compat_runtime/runtime_signals/__init__.py`
- `schemas/runtime-signal-report.schema.json`
- `scripts/build-runtime-signal-report.sh`
- `tests/test_runtime_signals.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-runtime-signal-report.sh out
scripts/build-release-decision-report.sh out
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
