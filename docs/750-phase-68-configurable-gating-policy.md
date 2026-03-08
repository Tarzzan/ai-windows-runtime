# Phase 68 - Configurable Gating Policy

## Objectif

Sortir les seuils de calibration alpha du code pour permettre un ajustement versionne sans modifier les modules de decision.

## Livrables

- Fichier de configuration versionne:
  - `config/alpha-gating-policy.json`
- Loader central:
  - `src/compat_runtime/common/policy.py`
  - source prioritaire: variable d'environnement `COMPAT_POLICY_PATH`
  - profil selectionnable via `COMPAT_POLICY_PROFILE` (`alpha` par defaut)
  - fallback: `config/alpha-gating-policy.json`
  - fallback final: policy par defaut integree

## Modules branches

- `quality_gate`
- `release_decision`
- `release_readiness`
- `pilot_readiness`
- `launch_readiness`

## Parametres exposes (exemples)

- `release_decision.warning_budget`
- `quality_gate.trend_regression_warn_threshold`
- `quality_gate.proposal_high_risk_warn_threshold`
- `quality_gate.installer_error_warn_threshold`
- `quality_gate.office_limited_as_pass`
- `pilot_readiness.limited_pilot_*`
- `launch_readiness.ready_allowed_*`

## Validation

- Tests policy:
  - `tests/test_alpha_gating_policy.py`
- Pipeline complet:
  - `scripts/run-full-pipeline.sh out`

## Resultat attendu

- Meme comportement par defaut qu'avant la phase.
- Possibilite de reconfigurer la politique sans patcher le code des modules.
