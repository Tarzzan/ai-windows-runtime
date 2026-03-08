# Phase 75 - Policy Config Validation Gate

## Objectif

Bloquer rapidement les regressions de configuration policy (types invalides, profil par defaut incoherent) avant les checks lockfile/release.

## Livrables

- Schema config:
  - `schemas/alpha-gating-policy-config.schema.json`
- Script:
  - `scripts/check-policy-config.sh`
- Integrations:
  - `scripts/run-full-pipeline.sh`
  - `scripts/build-release-bundle.sh`
  - `scripts/check-policy-lockfile-sync.sh`
  - `.github/workflows/ci.yml`

## Validation

- `tests/test_policy_config_script.py`

## Usage

```bash
scripts/check-policy-config.sh out
```
