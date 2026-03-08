# Phase 85 - Delivery Signoff Policy Gate

## Objectif

Assurer que le signoff livraison final reste coherent avec le diagnostic `release-policy-report`.

## Livrables

- `delivery-signoff-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
- Regle de signoff:
  - `approved` seulement si `release_policy_status == pass`
  - sinon `conditional` ou `blocked` selon les autres signaux existants

## Fichiers modifies

- `src/compat_runtime/delivery_signoff/cli.py`
- `schemas/delivery-signoff-report.schema.json`
- `tests/test_delivery_signoff.py`

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_delivery_signoff.py tests/test_release_packet.py tests/test_evidence_catalog.py tests/test_governance_checkpoint.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
```

