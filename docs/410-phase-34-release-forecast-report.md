# Phase 34 - Release forecast report

## Scope livre
- Ajout d'un module `release_forecast`:
  - generation `release-forecast-report.json`
  - consolidation des signaux iteration/decision/kpi/trend
  - estimation du nombre d'iterations restantes vers `go`
  - projection d'horizon (`immediate/near_term/long_term`) avec hypothese explicite
- Ajout du schema dedie:
  - `schemas/release-forecast-report.schema.json`
- Ajout d'un script:
  - `scripts/build-release-forecast-report.sh`
  - generation + validation schema de `out/release-forecast-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans bundle + repro package
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Forecast de convergence:
- estimation du chemin restant vers release readiness
- pondération par risque courant et dynamique trend (amélioration/régression)

2. Pilotage horizon:
- projection en iterations/jours pour planification produit
- classement de l'horizon previsionnel pour decision management

3. Actionnabilite:
- extraction des premieres taches prioritaires du plan d'iteration
- actions automatiques coherentes avec un contexte `no-go`/`hold`/`go`

## Fichiers cles
- `src/compat_runtime/release_forecast/cli.py`
- `src/compat_runtime/release_forecast/__init__.py`
- `schemas/release-forecast-report.schema.json`
- `scripts/build-release-forecast-report.sh`
- `tests/test_release_forecast.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-release-forecast-report.sh out
scripts/build-iteration-plan-report.sh out
scripts/build-hook-backlog-report.sh out
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
