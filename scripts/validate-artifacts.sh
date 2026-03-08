#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
REPORT_DIR="${OUT_DIR}/validation"
mkdir -p "$REPORT_DIR"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/trace.json" \
  --schema schemas/trace.schema.json \
  --report "${REPORT_DIR}/trace-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/gaps.json" \
  --schema schemas/gaps.schema.json \
  --report "${REPORT_DIR}/gaps-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-plan.json" \
  --schema schemas/patch-plan.schema.json \
  --report "${REPORT_DIR}/patch-plan-validation.json"

if [[ -f "${OUT_DIR}/patch-template-catalog.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/patch-template-catalog.json" \
    --schema schemas/patch-template-catalog.schema.json \
    --report "${REPORT_DIR}/patch-template-catalog-validation.json"
fi

if [[ -f "${OUT_DIR}/patch-plan-diff.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/patch-plan-diff.json" \
    --schema schemas/patch-plan-diff.schema.json \
    --report "${REPORT_DIR}/patch-plan-diff-validation.json"
fi

if [[ -f "${OUT_DIR}/proposal-provenance.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/proposal-provenance.json" \
    --schema schemas/proposal-provenance.schema.json \
    --report "${REPORT_DIR}/proposal-provenance-validation.json"
fi

if [[ -f "${OUT_DIR}/runtime-trace.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/runtime-trace.json" \
    --schema schemas/trace.schema.json \
    --report "${REPORT_DIR}/runtime-trace-validation.json"
fi

if [[ -f "${OUT_DIR}/crash-signature-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/crash-signature-report.json" \
    --schema schemas/crash-signature-report.schema.json \
    --report "${REPORT_DIR}/crash-signature-report-validation.json"
fi

if [[ -f "${OUT_DIR}/installer-phase-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/installer-phase-report.json" \
    --schema schemas/installer-phase-report.schema.json \
    --report "${REPORT_DIR}/installer-phase-report-validation.json"
fi

if [[ -f "${OUT_DIR}/runtime-signal-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/runtime-signal-report.json" \
    --schema schemas/runtime-signal-report.schema.json \
    --report "${REPORT_DIR}/runtime-signal-report-validation.json"
fi

if [[ -f "${OUT_DIR}/root-cause-summary.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/root-cause-summary.json" \
    --schema schemas/root-cause-summary.schema.json \
    --report "${REPORT_DIR}/root-cause-summary-validation.json"
fi

if [[ -f "${OUT_DIR}/test-impact-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/test-impact-report.json" \
    --schema schemas/test-impact-report.schema.json \
    --report "${REPORT_DIR}/test-impact-report-validation.json"
fi

if [[ -f "${OUT_DIR}/rollback-hints.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/rollback-hints.json" \
    --schema schemas/rollback-hints.schema.json \
    --report "${REPORT_DIR}/rollback-hints-validation.json"
fi

if [[ -f "${OUT_DIR}/proposal-risk-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/proposal-risk-report.json" \
    --schema schemas/proposal-risk-report.schema.json \
    --report "${REPORT_DIR}/proposal-risk-report-validation.json"
fi

if [[ -f "${OUT_DIR}/hook-backlog-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/hook-backlog-report.json" \
    --schema schemas/hook-backlog-report.schema.json \
    --report "${REPORT_DIR}/hook-backlog-report-validation.json"
fi

if [[ -f "${OUT_DIR}/proposal-review-checklist.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/proposal-review-checklist.json" \
    --schema schemas/proposal-review-checklist.schema.json \
    --report "${REPORT_DIR}/proposal-review-checklist-validation.json"
fi

if [[ -f "${OUT_DIR}/execution-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/execution-report.json" \
    --schema schemas/execution-report.schema.json \
    --report "${REPORT_DIR}/execution-report-validation.json"
fi

if [[ -f "${OUT_DIR}/trend-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/trend-report.json" \
    --schema schemas/trend-report.schema.json \
    --report "${REPORT_DIR}/trend-report-validation.json"
fi

if [[ -f "${OUT_DIR}/kpi-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/kpi-report.json" \
    --schema schemas/kpi-report.schema.json \
    --report "${REPORT_DIR}/kpi-report-validation.json"
fi

if [[ -f "${OUT_DIR}/dashboard-timeseries.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/dashboard-timeseries.json" \
    --schema schemas/dashboard-timeseries.schema.json \
    --report "${REPORT_DIR}/dashboard-timeseries-validation.json"
fi

if [[ -f "${OUT_DIR}/compatibility-matrix.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/compatibility-matrix.json" \
    --schema schemas/compatibility-matrix.schema.json \
    --report "${REPORT_DIR}/compatibility-matrix-validation.json"
fi

if [[ -f "${OUT_DIR}/alpha-release-checklist.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/alpha-release-checklist.json" \
    --schema schemas/alpha-release-checklist.schema.json \
    --report "${REPORT_DIR}/alpha-release-checklist-validation.json"
fi

if [[ -f "${OUT_DIR}/release-bundle-manifest.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-bundle-manifest.json" \
    --schema schemas/release-bundle-manifest.schema.json \
    --report "${REPORT_DIR}/release-bundle-manifest-validation.json"
fi

if [[ -f "${OUT_DIR}/productization-readiness.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/productization-readiness.json" \
    --schema schemas/productization-readiness.schema.json \
    --report "${REPORT_DIR}/productization-readiness-validation.json"
fi

if [[ -f "${OUT_DIR}/quality-gate-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/quality-gate-report.json" \
    --schema schemas/quality-gate-report.schema.json \
    --report "${REPORT_DIR}/quality-gate-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-decision-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-decision-report.json" \
    --schema schemas/release-decision-report.schema.json \
    --report "${REPORT_DIR}/release-decision-report-validation.json"
fi

if [[ -f "${OUT_DIR}/iteration-plan-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/iteration-plan-report.json" \
    --schema schemas/iteration-plan-report.schema.json \
    --report "${REPORT_DIR}/iteration-plan-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-forecast-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-forecast-report.json" \
    --schema schemas/release-forecast-report.schema.json \
    --report "${REPORT_DIR}/release-forecast-report-validation.json"
fi

if [[ -f "${OUT_DIR}/readiness-scorecard-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/readiness-scorecard-report.json" \
    --schema schemas/readiness-scorecard-report.schema.json \
    --report "${REPORT_DIR}/readiness-scorecard-report-validation.json"
fi

if [[ -f "${OUT_DIR}/execution-burndown-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/execution-burndown-report.json" \
    --schema schemas/execution-burndown-report.schema.json \
    --report "${REPORT_DIR}/execution-burndown-report-validation.json"
fi

if [[ -f "${OUT_DIR}/validation-command-pack.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/validation-command-pack.json" \
    --schema schemas/validation-command-pack.schema.json \
    --report "${REPORT_DIR}/validation-command-pack-validation.json"
fi

if [[ -f "${OUT_DIR}/risk-watchlist-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/risk-watchlist-report.json" \
    --schema schemas/risk-watchlist-report.schema.json \
    --report "${REPORT_DIR}/risk-watchlist-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-gate-history-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-gate-history-report.json" \
    --schema schemas/release-gate-history-report.schema.json \
    --report "${REPORT_DIR}/release-gate-history-report-validation.json"
fi

if [[ -f "${OUT_DIR}/pilot-readiness-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/pilot-readiness-report.json" \
    --schema schemas/pilot-readiness-report.schema.json \
    --report "${REPORT_DIR}/pilot-readiness-report-validation.json"
fi

if [[ -f "${OUT_DIR}/ownership-assignment-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/ownership-assignment-report.json" \
    --schema schemas/ownership-assignment-report.schema.json \
    --report "${REPORT_DIR}/ownership-assignment-report-validation.json"
fi

if [[ -f "${OUT_DIR}/remediation-sprint-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/remediation-sprint-report.json" \
    --schema schemas/remediation-sprint-report.schema.json \
    --report "${REPORT_DIR}/remediation-sprint-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-brief-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-brief-report.json" \
    --schema schemas/release-brief-report.schema.json \
    --report "${REPORT_DIR}/release-brief-report-validation.json"
fi

if [[ -f "${OUT_DIR}/rollout-guardrails-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/rollout-guardrails-report.json" \
    --schema schemas/rollout-guardrails-report.schema.json \
    --report "${REPORT_DIR}/rollout-guardrails-report-validation.json"
fi

if [[ -f "${OUT_DIR}/artifact-health-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/artifact-health-report.json" \
    --schema schemas/artifact-health-report.schema.json \
    --report "${REPORT_DIR}/artifact-health-report-validation.json"
fi

if [[ -f "${OUT_DIR}/delivery-cockpit-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/delivery-cockpit-report.json" \
    --schema schemas/delivery-cockpit-report.schema.json \
    --report "${REPORT_DIR}/delivery-cockpit-report-validation.json"
fi

if [[ -f "${OUT_DIR}/stakeholder-update-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/stakeholder-update-report.json" \
    --schema schemas/stakeholder-update-report.schema.json \
    --report "${REPORT_DIR}/stakeholder-update-report-validation.json"
fi

if [[ -f "${OUT_DIR}/handoff-checklist-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/handoff-checklist-report.json" \
    --schema schemas/handoff-checklist-report.schema.json \
    --report "${REPORT_DIR}/handoff-checklist-report-validation.json"
fi

if [[ -f "${OUT_DIR}/validation-coverage-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/validation-coverage-report.json" \
    --schema schemas/validation-coverage-report.schema.json \
    --report "${REPORT_DIR}/validation-coverage-report-validation.json"
fi

if [[ -f "${OUT_DIR}/launch-readiness-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/launch-readiness-report.json" \
    --schema schemas/launch-readiness-report.schema.json \
    --report "${REPORT_DIR}/launch-readiness-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-packet-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-packet-report.json" \
    --schema schemas/release-packet-report.schema.json \
    --report "${REPORT_DIR}/release-packet-report-validation.json"
fi

if [[ -f "${OUT_DIR}/ops-runbook-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/ops-runbook-report.json" \
    --schema schemas/ops-runbook-report.schema.json \
    --report "${REPORT_DIR}/ops-runbook-report-validation.json"
fi

if [[ -f "${OUT_DIR}/dependency-watch-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/dependency-watch-report.json" \
    --schema schemas/dependency-watch-report.schema.json \
    --report "${REPORT_DIR}/dependency-watch-report-validation.json"
fi

if [[ -f "${OUT_DIR}/readiness-delta-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/readiness-delta-report.json" \
    --schema schemas/readiness-delta-report.schema.json \
    --report "${REPORT_DIR}/readiness-delta-report-validation.json"
fi

if [[ -f "${OUT_DIR}/delivery-signoff-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/delivery-signoff-report.json" \
    --schema schemas/delivery-signoff-report.schema.json \
    --report "${REPORT_DIR}/delivery-signoff-report-validation.json"
fi

if [[ -f "${OUT_DIR}/post-release-monitor-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/post-release-monitor-report.json" \
    --schema schemas/post-release-monitor-report.schema.json \
    --report "${REPORT_DIR}/post-release-monitor-report-validation.json"
fi

if [[ -f "${OUT_DIR}/incident-feedback-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/incident-feedback-report.json" \
    --schema schemas/incident-feedback-report.schema.json \
    --report "${REPORT_DIR}/incident-feedback-report-validation.json"
fi

if [[ -f "${OUT_DIR}/backlog-refresh-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/backlog-refresh-report.json" \
    --schema schemas/backlog-refresh-report.schema.json \
    --report "${REPORT_DIR}/backlog-refresh-report-validation.json"
fi

if [[ -f "${OUT_DIR}/intake-capacity-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/intake-capacity-report.json" \
    --schema schemas/intake-capacity-report.schema.json \
    --report "${REPORT_DIR}/intake-capacity-report-validation.json"
fi

if [[ -f "${OUT_DIR}/admission-control-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/admission-control-report.json" \
    --schema schemas/admission-control-report.schema.json \
    --report "${REPORT_DIR}/admission-control-report-validation.json"
fi

if [[ -f "${OUT_DIR}/commitment-pacing-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/commitment-pacing-report.json" \
    --schema schemas/commitment-pacing-report.schema.json \
    --report "${REPORT_DIR}/commitment-pacing-report-validation.json"
fi

if [[ -f "${OUT_DIR}/scope-budget-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/scope-budget-report.json" \
    --schema schemas/scope-budget-report.schema.json \
    --report "${REPORT_DIR}/scope-budget-report-validation.json"
fi

if [[ -f "${OUT_DIR}/admission-window-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/admission-window-report.json" \
    --schema schemas/admission-window-report.schema.json \
    --report "${REPORT_DIR}/admission-window-report-validation.json"
fi

if [[ -f "${OUT_DIR}/commitment-guard-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/commitment-guard-report.json" \
    --schema schemas/commitment-guard-report.schema.json \
    --report "${REPORT_DIR}/commitment-guard-report-validation.json"
fi

if [[ -f "${OUT_DIR}/portfolio-risk-budget-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/portfolio-risk-budget-report.json" \
    --schema schemas/portfolio-risk-budget-report.schema.json \
    --report "${REPORT_DIR}/portfolio-risk-budget-report-validation.json"
fi

if [[ -f "${OUT_DIR}/delivery-intake-sync-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/delivery-intake-sync-report.json" \
    --schema schemas/delivery-intake-sync-report.schema.json \
    --report "${REPORT_DIR}/delivery-intake-sync-report-validation.json"
fi

if [[ -f "${OUT_DIR}/execution-reserve-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/execution-reserve-report.json" \
    --schema schemas/execution-reserve-report.schema.json \
    --report "${REPORT_DIR}/execution-reserve-report-validation.json"
fi

if [[ -f "${OUT_DIR}/capacity-buffer-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/capacity-buffer-report.json" \
    --schema schemas/capacity-buffer-report.schema.json \
    --report "${REPORT_DIR}/capacity-buffer-report-validation.json"
fi

if [[ -f "${OUT_DIR}/intake-queue-policy-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/intake-queue-policy-report.json" \
    --schema schemas/intake-queue-policy-report.schema.json \
    --report "${REPORT_DIR}/intake-queue-policy-report-validation.json"
fi

if [[ -f "${OUT_DIR}/scope-rebalance-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/scope-rebalance-report.json" \
    --schema schemas/scope-rebalance-report.schema.json \
    --report "${REPORT_DIR}/scope-rebalance-report-validation.json"
fi

if [[ -f "${OUT_DIR}/flow-control-budget-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/flow-control-budget-report.json" \
    --schema schemas/flow-control-budget-report.schema.json \
    --report "${REPORT_DIR}/flow-control-budget-report-validation.json"
fi

if [[ -f "${OUT_DIR}/intake-release-window-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/intake-release-window-report.json" \
    --schema schemas/intake-release-window-report.schema.json \
    --report "${REPORT_DIR}/intake-release-window-report-validation.json"
fi

if [[ -f "${OUT_DIR}/execution-stability-guard-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/execution-stability-guard-report.json" \
    --schema schemas/execution-stability-guard-report.schema.json \
    --report "${REPORT_DIR}/execution-stability-guard-report-validation.json"
fi

if [[ -f "${OUT_DIR}/delivery-safety-margin-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/delivery-safety-margin-report.json" \
    --schema schemas/delivery-safety-margin-report.schema.json \
    --report "${REPORT_DIR}/delivery-safety-margin-report-validation.json"
fi

if [[ -f "${OUT_DIR}/intake-commitment-window-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/intake-commitment-window-report.json" \
    --schema schemas/intake-commitment-window-report.schema.json \
    --report "${REPORT_DIR}/intake-commitment-window-report-validation.json"
fi

if [[ -f "${OUT_DIR}/scope-lock-state-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/scope-lock-state-report.json" \
    --schema schemas/scope-lock-state-report.schema.json \
    --report "${REPORT_DIR}/scope-lock-state-report-validation.json"
fi

if [[ -f "${OUT_DIR}/throughput-guard-band-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/throughput-guard-band-report.json" \
    --schema schemas/throughput-guard-band-report.schema.json \
    --report "${REPORT_DIR}/throughput-guard-band-report-validation.json"
fi

if [[ -f "${OUT_DIR}/intake-slot-policy-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/intake-slot-policy-report.json" \
    --schema schemas/intake-slot-policy-report.schema.json \
    --report "${REPORT_DIR}/intake-slot-policy-report-validation.json"
fi

if [[ -f "${OUT_DIR}/scope-freeze-guard-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/scope-freeze-guard-report.json" \
    --schema schemas/scope-freeze-guard-report.schema.json \
    --report "${REPORT_DIR}/scope-freeze-guard-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-retrospective-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-retrospective-report.json" \
    --schema schemas/release-retrospective-report.schema.json \
    --report "${REPORT_DIR}/release-retrospective-report-validation.json"
fi

if [[ -f "${OUT_DIR}/next-cycle-bootstrap-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/next-cycle-bootstrap-report.json" \
    --schema schemas/next-cycle-bootstrap-report.schema.json \
    --report "${REPORT_DIR}/next-cycle-bootstrap-report-validation.json"
fi

if [[ -f "${OUT_DIR}/stability-window-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/stability-window-report.json" \
    --schema schemas/stability-window-report.schema.json \
    --report "${REPORT_DIR}/stability-window-report-validation.json"
fi

if [[ -f "${OUT_DIR}/office-readiness-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/office-readiness-report.json" \
    --schema schemas/office-readiness-report.schema.json \
    --report "${REPORT_DIR}/office-readiness-report-validation.json"
fi

if [[ -f "${OUT_DIR}/hotfix-planner-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/hotfix-planner-report.json" \
    --schema schemas/hotfix-planner-report.schema.json \
    --report "${REPORT_DIR}/hotfix-planner-report-validation.json"
fi

if [[ -f "${OUT_DIR}/verification-snapshot-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/verification-snapshot-report.json" \
    --schema schemas/verification-snapshot-report.schema.json \
    --report "${REPORT_DIR}/verification-snapshot-report-validation.json"
fi

if [[ -f "${OUT_DIR}/evidence-catalog-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/evidence-catalog-report.json" \
    --schema schemas/evidence-catalog-report.schema.json \
    --report "${REPORT_DIR}/evidence-catalog-report-validation.json"
fi

if [[ -f "${OUT_DIR}/governance-checkpoint-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/governance-checkpoint-report.json" \
    --schema schemas/governance-checkpoint-report.schema.json \
    --report "${REPORT_DIR}/governance-checkpoint-report-validation.json"
fi

if [[ -f "${OUT_DIR}/repro-package.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/repro-package.json" \
    --schema schemas/repro-package.schema.json \
    --report "${REPORT_DIR}/repro-package-validation.json"
fi

if [[ -f "${OUT_DIR}/active-policy.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/active-policy.json" \
    --schema schemas/active-policy.schema.json \
    --report "${REPORT_DIR}/active-policy-validation.json"
fi

if [[ -f "${OUT_DIR}/policy-health-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/policy-health-report.json" \
    --schema schemas/policy-health-report.schema.json \
    --report "${REPORT_DIR}/policy-health-report-validation.json"
fi

if [[ -f "${OUT_DIR}/release-policy-report.json" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
    --input "${OUT_DIR}/release-policy-report.json" \
    --schema schemas/release-policy-report.schema.json \
    --report "${REPORT_DIR}/release-policy-report-validation.json"
fi

echo "artifact validation: ok"
