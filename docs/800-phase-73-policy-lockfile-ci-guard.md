# Phase 73 - Policy Lockfile CI Guard

## Objectif

Ajouter un garde-fou CI dedie pour verifier que le lockfile policy versionne reste synchronise avec la policy active.

## Livrables

- Script:
  - `scripts/check-policy-lockfile-sync.sh`
- Workflow CI:
  - `.github/workflows/ci.yml` execute le check lockfile avant lint/tests/pipeline.

## Validation

- `tests/test_policy_lockfile_sync_script.py`

## Usage

```bash
scripts/check-policy-lockfile-sync.sh
scripts/check-policy-lockfile-sync.sh --fix
```
