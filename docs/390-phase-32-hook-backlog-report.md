# Phase 32 - Hook backlog report

## Scope livre
- Ajout d'un module `hook_backlog`:
  - generation `hook-backlog-report.json`
  - consolidation des signaux runtime + patch plan + risk scoring
  - priorisation des hooks runtime manquants (com/winrt/registry/network/installer)
  - niveau d'urgence `P0/P1/P2` et `impact_score` pour ordonnancer l'implementation
- Ajout du schema dedie:
  - `schemas/hook-backlog-report.schema.json`
- Ajout d'un script:
  - `scripts/build-hook-backlog-report.sh`
  - generation + validation schema de `out/hook-backlog-report.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere et valide cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans manifeste + bundle
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Backlog instrumentation:
- une vue unique des domaines de hook restants
- corrélation directe avec volume d'evenements, erreurs et proposals associees

2. Priorisation basee risque:
- majoration automatique de priorite quand des proposals high-risk sont liees
- score d'impact borné pour planifier les iterations runtime

3. Operabilite release:
- artefact exploitable pour grooming technique et planning sprint runtime
- actions par defaut pour attaquer les domaines `P0` en premier

## Fichiers cles
- `src/compat_runtime/hook_backlog/cli.py`
- `src/compat_runtime/hook_backlog/__init__.py`
- `schemas/hook-backlog-report.schema.json`
- `scripts/build-hook-backlog-report.sh`
- `tests/test_hook_backlog.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
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
