# Phase 74 - Policy Lockfile Sync Fix Mode

## Objectif

Rendre le check de sync lockfile plus actionnable en local avec un mode de correction automatique.

## Livrables

- Script:
  - `scripts/check-policy-lockfile-sync.sh` supporte `--fix`
  - en mode strict: echec + message de remediaton
  - en mode `--fix`: regeneration du lockfile et succes

## Validation

- `tests/test_policy_lockfile_sync_script.py`

## Usage

```bash
scripts/check-policy-lockfile-sync.sh
scripts/check-policy-lockfile-sync.sh --fix
```
