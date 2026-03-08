# Phase 72 - Policy Tooling Hardening

## Objectif

Durcir les scripts policy pour des echec explicites en environnement incomplet et faciliter la maintenance du lockfile.

## Livrables

- Controle de dependance `jq`:
  - `scripts/check-release-policy.sh`
  - `scripts/check-policy-drift.sh`
- Script de refresh lockfile:
  - `scripts/refresh-policy-lockfile.sh`

## Validation

- `tests/test_release_policy_script.py`
- `tests/test_policy_lockfile_scripts.py`
- `tests/test_refresh_policy_lockfile_script.py`

## Usage

```bash
scripts/refresh-policy-lockfile.sh
scripts/check-policy-drift.sh out
scripts/check-release-policy.sh out
```
