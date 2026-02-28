# Phase 30 - Release decision report

## Scope livre
- Ajout d'un module `release_decision`:
  - generation `release-decision-report.json`
  - consolidation des signaux `quality gate` + checklist + matrix + productization
  - decision explicite `go/hold/no-go`
  - synthese de checks bloquants et budget warnings
- Ajout du schema dedie:
  - `schemas/release-decision-report.schema.json`
- Ajout d'un script:
  - `scripts/build-release-decision-report.sh`
  - generation + validation schema de `out/release-decision-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Decision unifiee:
- traduction des artefacts de qualite en verdict release operationnel
- statut final `go/hold/no-go` directement consommable en CI

2. Blocants vs warnings:
- separation claire entre echecs bloquants et alertes non bloquantes
- comptage centralise du warning budget cross-artefacts

3. Guidance actionnable:
- actions de suite coherentes avec la decision
- reduction de l'ambiguite entre preparation technique et decision de promotion

## Fichiers cles
- `src/compat_runtime/release_decision/cli.py`
- `src/compat_runtime/release_decision/__init__.py`
- `schemas/release-decision-report.schema.json`
- `scripts/build-release-decision-report.sh`
- `tests/test_release_decision.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
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
