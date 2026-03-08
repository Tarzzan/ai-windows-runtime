# Phase 84 - Release Policy Propagation To Governance

## Objectif

Propager le diagnostic `release-policy-report` dans les artefacts de synthese jusqu'au checkpoint gouvernance.

## Livrables

- `release-packet-report`:
  - ajout de `summary.release_policy_status`
  - ajout de `summary.release_policy_failures`
- `evidence-catalog-report`:
  - ajout de `summary.release_policy_status`
  - ajout de `summary.release_policy_failures`
- `governance-checkpoint-report`:
  - ajout de `summary.release_policy_status`
  - ajout de `summary.release_policy_failures`
  - blocage explicite si `release_policy_status != pass`

## Fichiers modifies

- `src/compat_runtime/release_packet/cli.py`
- `src/compat_runtime/evidence_catalog/cli.py`
- `src/compat_runtime/governance_checkpoint/cli.py`
- `scripts/build-release-packet-report.sh`
- `schemas/release-packet-report.schema.json`
- `schemas/evidence-catalog-report.schema.json`
- `schemas/governance-checkpoint-report.schema.json`
- `tests/test_release_packet.py`
- `tests/test_evidence_catalog.py`
- `tests/test_governance_checkpoint.py`

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_release_packet.py tests/test_evidence_catalog.py tests/test_governance_checkpoint.py tests/test_release_policy_script.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
```

