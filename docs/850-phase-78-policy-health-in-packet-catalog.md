# Phase 78 - Policy Health in Packet and Catalog

## Objectif

Propager les signaux policy (`config_valid`, `lockfile_sync`) jusque dans le packet de release et l'evidence catalog.

## Livrables

- `release-packet-report` enrichi:
  - `summary.policy_config_valid`
  - `summary.policy_lockfile_sync`
- `evidence-catalog-report` enrichi:
  - `summary.policy_config_valid`
  - `summary.policy_lockfile_sync`
- Regeneration du release packet apres `policy-health-report` dans:
  - `scripts/run-full-pipeline.sh`
  - `scripts/build-release-bundle.sh`

## Validation

- `tests/test_release_packet.py`
- `tests/test_evidence_catalog.py`

## Usage

```bash
scripts/run-full-pipeline.sh out
```
