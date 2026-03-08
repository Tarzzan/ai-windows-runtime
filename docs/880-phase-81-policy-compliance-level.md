# Phase 81 - Policy Compliance Level Propagation

## Objectif

Ajouter un niveau synthese `policy_compliance_level` pour simplifier la lecture de conformite policy dans les artefacts de decision.

## Livrables

- `release-packet-report`:
  - `summary.policy_compliance_level` (`compliant|degraded|non_compliant`)
- `evidence-catalog-report`:
  - `summary.policy_compliance_level`
- `governance-checkpoint-report`:
  - `summary.policy_compliance_level`

## Regle de calcul

- `compliant`: `policy_config_valid=true` et `policy_lockfile_sync=true`
- `degraded`: un seul des deux signaux est `true`
- `non_compliant`: les deux signaux sont `false`

## Validation

- `tests/test_release_packet.py`
- `tests/test_evidence_catalog.py`
- `tests/test_governance_checkpoint.py`

## Usage

```bash
scripts/run-full-pipeline.sh out
```
