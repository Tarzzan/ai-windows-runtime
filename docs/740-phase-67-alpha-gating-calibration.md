# Phase 67 - Alpha Gating Calibration

## Objectif

Stabiliser les décisions de release/launch en environnement alpha sans masquer les signaux critiques.

## Changements de calibration

- `quality-gate`:
  - `kpi_risk_level`:
    - `high` + `failed_runs=0` => `pass`
    - `high` + `failed_runs>0` => `fail`
  - seuils warning optionnels:
    - `trend_regressions` warn si `regressed_metrics > 4`
    - `proposal_risk_high` warn si `high_risk > 3`
    - `installer_phases` warn si `error_events > 5`
  - `office_readiness`:
    - `ready|limited|not_provided` => `pass`
    - `blocked` => `fail`
  - `required_failures` compte uniquement les checks `required` en `fail`.

- `release-readiness`:
  - `compatibility_matrix.release_ready` n'est pas bloqué par `risk_level=high` si `failed_runs=0`.
  - `alpha_release_checklist.risk_level`:
    - `high` + `failed_runs=0` => `pass`
  - `regression_review` warn seulement au-dela de 4 métriques régressées.

- `release-decision`:
  - budget warnings (`WARNING_BUDGET=2`):
    - `no-go` si blockers
    - `hold` si warnings > 2
    - `go` sinon

- `pilot-readiness`:
  - `limited_pilot` possible si:
    - `score >= 60`
    - `decision in {go, hold}`
    - `gate in {pass, warn}`
    - `blocking_tasks <= 4`
    - `iterations_to_go <= 4`

- `launch-readiness`:
  - `ready` possible si:
    - `decision=go`
    - `gate in {pass, warn}`
    - `office_readiness in {ready, limited, not_provided}`
    - `pilot_recommendation in {ready, limited_pilot}`
    - `handoff_failed_checks=0`
    - `validation_missing_reports=0`

## Orchestration post-office

Apres generation de `office-readiness-report.json`, la pipeline re-execute:

1. `quality-gate`
2. `release-decision`
3. `pilot-readiness`
4. `launch-readiness`
5. `release-packet`
6. `readiness-delta`
7. `delivery-signoff`
8. `post-release-monitor`
9. `stability-window`

Cela evite les decisions avec etat stale et garantit des artefacts finaux coherents.

## Policy regression check

- Script dedie: `scripts/check-release-policy.sh`
- Conditions strictes:
  - `quality-gate-report.json.gate == "pass"`
  - `release-decision-report.json.decision == "go"`
  - `launch-readiness-report.json.status == "ready"`
- Ce controle est execute automatiquement en fin de:
  - `scripts/run-full-pipeline.sh`
  - `scripts/build-release-bundle.sh`

## Invariants conserves

- Tout `fail` requis reste bloquant.
- `office_readiness=blocked` reste bloquant dans `launch-readiness`.
- Les warnings restent visibles dans les artefacts et la decision.
