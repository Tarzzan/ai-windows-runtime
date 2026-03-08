# Phase 79 - Policy Health in Governance Checkpoint

## Objectif

Faire remonter la conformite policy jusque dans le checkpoint de gouvernance final.

## Livrables

- `governance-checkpoint-report` enrichi:
  - `summary.policy_config_valid`
  - `summary.policy_lockfile_sync`
- Nouvelle regle:
  - checkpoint `block` si `policy_config_valid` ou `policy_lockfile_sync` est faux.

## Validation

- `tests/test_governance_checkpoint.py`

## Usage

```bash
scripts/run-full-pipeline.sh out
```
