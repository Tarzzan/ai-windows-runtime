# Phase 89 - Policy Communication Propagation

## Objectif

Propager `release_policy_status` et `release_policy_failures` dans la chaine de communication (`release-brief`, `delivery-cockpit`, `stakeholder-update`).

## Livrables

- `release-brief-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
- `delivery-cockpit-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`
- `stakeholder-update-report`:
  - `summary.release_policy_status`
  - `summary.release_policy_failures`

## Pipeline/Bundles

- Regeneration de la chaine communication juste apres `check-release-policy`:
  - `build-release-brief-report.sh`
  - `build-delivery-cockpit-report.sh`
  - `build-stakeholder-update-report.sh`
  - `build-release-packet-report.sh`
- Nettoyage des artefacts stale associes pour eviter les echecs schema en pre-validation.

## Fichiers modifies

- `src/compat_runtime/release_brief/cli.py`
- `src/compat_runtime/delivery_cockpit/cli.py`
- `src/compat_runtime/stakeholder_update/cli.py`
- `scripts/build-release-brief-report.sh`
- `schemas/delivery-cockpit-report.schema.json`
- `schemas/stakeholder-update-report.schema.json`
- `scripts/run-full-pipeline.sh`
- `scripts/build-release-bundle.sh`
- `tests/test_release_brief.py`
- `tests/test_delivery_cockpit.py`
- `tests/test_stakeholder_update.py`

