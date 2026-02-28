# Phase 21 - Proposal provenance metadata

## Scope livre
- Ajout d'un module `proposal_provenance`:
  - generation `proposal-provenance.json`
  - liaison de chaque proposition vers son gap source
  - enrichment par evidence trace (messages representatifs)
  - score de provenance pour la revue technique
- Ajout du schema dedie:
  - `schemas/proposal-provenance.schema.json`
- Ajout d'un script:
  - `scripts/build-proposal-provenance.sh`
  - generation + validation schema de `out/proposal-provenance.json`
- Integration pipeline:
  - `scripts/run-full-pipeline.sh` genere cet artefact
  - `scripts/validate-artifacts.sh` le valide quand present
  - `scripts/build-release-bundle.sh` l'inclut dans le bundle
  - `scripts/build-repro-package.sh` le reference dans les artefacts

## Capacites ajoutees
1. Provenance proposal-level:
- mapping explicite `gap_id -> gap metadata -> trace evidence`
- lineage standardise `trace->gaps->patch-plan`

2. Signal de confiance:
- `provenance_score` base sur confiance gap + volume evidence trace
- detection des propositions faibles/non reliees

3. Hints d'action:
- recommandations automatiques quand les liens gap/proposal sont incomplets
- recommandations pour renforcer l'evidence de revue

## Fichiers cles
- `src/compat_runtime/proposal_provenance/cli.py`
- `src/compat_runtime/proposal_provenance/__init__.py`
- `schemas/proposal-provenance.schema.json`
- `scripts/build-proposal-provenance.sh`
- `tests/test_proposal_provenance.py`

## Validation locale
```bash
. .venv/bin/activate
pytest -q
ruff check .

scripts/run-full-pipeline.sh out
scripts/build-proposal-provenance.sh out
scripts/build-patch-plan-diff.sh out
scripts/build-root-cause-summary.sh out
scripts/build-repro-package.sh out
scripts/build-release-bundle.sh out out/release-bundle

cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

