# Phase 69 - Policy Profiles (alpha/beta/prod)

## Objectif

Permettre de basculer la politique de gating sans modifier le code, selon un profil d'environnement.

## Livrables

- Support des profils dans la config:
  - `config/alpha-gating-policy.json`
  - structure:
    - `default_profile`
    - `profiles.<name>.<domain>.<setting>`
- Selection de profil:
  - `COMPAT_POLICY_PROFILE`
  - fallback sur `default_profile`, puis `alpha`
- Compatibilite retroactive:
  - le format plat (sans `profiles`) reste supporte

## Impact

- Mecanisme de tuning progressif:
  - `alpha`: permissif pour iteration rapide
  - `beta`: plus strict
  - `prod`: strict et conservateur
- Meme point d'integration pour tous les modules de decision.

## Validation

- tests:
  - `tests/test_alpha_gating_policy.py`
- pipeline:
  - `scripts/run-full-pipeline.sh out`
