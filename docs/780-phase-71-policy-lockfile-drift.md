# Phase 71 - Policy Lockfile Drift

## Objectif

Verrouiller la policy active attendue et detecter toute derive involontaire dans la pipeline.

## Livrables

- Lockfile versionne:
  - `config/active-policy.lock.json`
- Scripts:
  - `scripts/export-active-policy.sh`
  - `scripts/check-policy-drift.sh`
- Integrations:
  - `scripts/run-full-pipeline.sh`
  - `scripts/build-release-bundle.sh`
  - `scripts/build-repro-package.sh`
  - `scripts/validate-artifacts.sh`

## Variables supportees

- `COMPAT_POLICY_LOCKFILE`: override du chemin lockfile (defaut: `config/active-policy.lock.json`)
- `COMPAT_POLICY_PATH`: override du fichier policy source
- `COMPAT_POLICY_PROFILE`: profil actif (`alpha`, `beta`, `prod`, ...)

## Validation

- `tests/test_policy_lockfile_scripts.py`

## Usage

```bash
scripts/export-active-policy.sh out
scripts/check-policy-drift.sh out
scripts/run-full-pipeline.sh out
```
