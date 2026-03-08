# Phase 77 - Policy Health Release Gate

## Objectif

Renforcer la gate de release pour exiger explicitement un etat policy sain avant `go`.

## Livrables

- `scripts/check-release-policy.sh` valide maintenant:
  - `policy-health-report.json` present
  - `config_valid == true`
  - `lockfile_sync == true`

## Validation

- `tests/test_release_policy_script.py`

## Usage

```bash
scripts/check-release-policy.sh out
```
