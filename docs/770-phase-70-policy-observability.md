# Phase 70 - Policy Observability

## Objectif

Rendre la policy effective visible en execution (debug local + CI) apres merge defaults + profil + override fichier.

## Livrables

- Script:
  - `scripts/show-active-policy.sh`
- Sortie JSON:
  - `policy_path`
  - `policy_profile`
  - `policy` (configuration effective)

## Variables supportees

- `COMPAT_POLICY_PATH`: chemin du fichier policy
- `COMPAT_POLICY_PROFILE`: profil actif (`alpha`, `beta`, `prod`, ...)

## Validation

- `tests/test_show_active_policy_script.py`

## Usage

```bash
scripts/show-active-policy.sh
COMPAT_POLICY_PROFILE=prod scripts/show-active-policy.sh
```
