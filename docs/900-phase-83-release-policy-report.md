# Phase 83 - Release Policy Report Artifact

## Objectif

Rendre le gate release-policy plus observable avec un artefact machine-readable reutilisable par les workflows de validation et d'audit.

## Livrables

- Nouveau schema:
  - `schemas/release-policy-report.schema.json`
- Script gate enrichi:
  - `scripts/check-release-policy.sh`
  - produit `out/release-policy-report.json`
  - produit `out/validation/release-policy-report-validation.json`
  - conserve un comportement strict (`exit 1`) si un check est non conforme.
- Integration pipeline/bundle:
  - `scripts/run-full-pipeline.sh`
  - `scripts/build-release-bundle.sh`
  - `scripts/build-repro-package.sh`
  - `scripts/validate-artifacts.sh`

## Contenu du report

- `status`: `pass|fail`
- `summary`: valeurs observees (`gate`, `decision`, `launch`, policy flags)
- `checks`: booleens par condition
- `failures`: liste explicite des ecarts

## Validation

```bash
. .venv/bin/activate
pytest -q tests/test_release_policy_script.py tests/test_repro_package.py
./scripts/run-full-pipeline.sh out
./scripts/build-release-bundle.sh out out/release-bundle
```

