# Phase 82 - Policy Compliance Gate Hardening

## Objectif

Finaliser l'introduction de `policy_compliance_level` et eliminer les faux echecs lies aux artefacts policy obsoletes.

## Livrables

- `policy-health-report`:
  - schema enrichi avec `policy_compliance_level` obligatoire.
  - generation explicite de `policy_compliance_level` dans `build-policy-health-report.sh`.
- `check-release-policy.sh`:
  - gate principal sur `policy_compliance_level == compliant`.
  - fallback de compatibilite sur `config_valid` + `lockfile_sync` si le champ est absent.
- `run-full-pipeline.sh` / `build-release-bundle.sh`:
  - purge preventive des anciens artefacts policy avant validation initiale.

## Motivation

Le pipeline validait parfois un ancien `out/policy-health-report.json` avant sa regeneration, provoquant un echec schema non deterministe.

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_release_policy_script.py tests/test_policy_health_report_script.py tests/test_policy_config_script.py tests/test_policy_lockfile_sync_script.py tests/test_release_packet.py tests/test_evidence_catalog.py tests/test_governance_checkpoint.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
./scripts/check-policy-lockfile-sync.sh
```

