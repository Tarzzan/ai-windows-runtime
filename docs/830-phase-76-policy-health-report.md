# Phase 76 - Policy Health Report

## Objectif

Rendre l'etat policy observable dans les artefacts de release (config valide, sync lockfile, empreinte policy active).

## Livrables

- Schema:
  - `schemas/policy-health-report.schema.json`
- Script:
  - `scripts/build-policy-health-report.sh`
- Integrations:
  - `scripts/run-full-pipeline.sh`
  - `scripts/build-release-bundle.sh`
  - `scripts/build-repro-package.sh`
  - `scripts/validate-artifacts.sh`

## Validation

- `tests/test_policy_health_report_script.py`

## Usage

```bash
scripts/build-policy-health-report.sh out
```
