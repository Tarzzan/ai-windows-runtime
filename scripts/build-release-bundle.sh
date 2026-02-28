#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
BUNDLE_DIR="${2:-out/release-bundle}"
VALIDATION_DIR="${OUT_DIR}/validation"
BASELINE_PATCH_PLAN="${BASELINE_PATCH_PLAN:-}"

mkdir -p "${BUNDLE_DIR}" "${VALIDATION_DIR}"

PATCH_PLAN_DIFF_ARGS=(
  --current "${OUT_DIR}/patch-plan.json"
  --current-label "current-base"
  --output "${OUT_DIR}/patch-plan-diff.json"
)
if [[ -n "${BASELINE_PATCH_PLAN}" && -f "${BASELINE_PATCH_PLAN}" ]]; then
  PATCH_PLAN_DIFF_ARGS+=(--baseline "${BASELINE_PATCH_PLAN}" --baseline-label "baseline-base")
fi
"${PYTHON_BIN}" -m compat_runtime.patch_plan_diff.cli "${PATCH_PLAN_DIFF_ARGS[@]}"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-plan-diff.json" \
  --schema schemas/patch-plan-diff.schema.json \
  --report "${VALIDATION_DIR}/patch-plan-diff-validation.json"

"${PYTHON_BIN}" -m compat_runtime.patch_template_library.cli \
  --gaps "${OUT_DIR}/gaps.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --output "${OUT_DIR}/patch-template-catalog.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/patch-template-catalog.json" \
  --schema schemas/patch-template-catalog.schema.json \
  --report "${VALIDATION_DIR}/patch-template-catalog-validation.json"

"${PYTHON_BIN}" -m compat_runtime.proposal_provenance.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --trace "${OUT_DIR}/trace.json" \
  --output "${OUT_DIR}/proposal-provenance.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/proposal-provenance.json" \
  --schema schemas/proposal-provenance.schema.json \
  --report "${VALIDATION_DIR}/proposal-provenance-validation.json"

"${PYTHON_BIN}" -m compat_runtime.crash_signatures.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/crash-signature-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/crash-signature-report.json" \
  --schema schemas/crash-signature-report.schema.json \
  --report "${VALIDATION_DIR}/crash-signature-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.installer_phases.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/installer-phase-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/installer-phase-report.json" \
  --schema schemas/installer-phase-report.schema.json \
  --report "${VALIDATION_DIR}/installer-phase-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.runtime_signals.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/runtime-signal-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/runtime-signal-report.json" \
  --schema schemas/runtime-signal-report.schema.json \
  --report "${VALIDATION_DIR}/runtime-signal-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.root_cause.cli \
  --gaps "${OUT_DIR}/gaps.json" "${OUT_DIR}/runtime-gaps.json" \
  --patch-plans "${OUT_DIR}/patch-plan.json" "${OUT_DIR}/runtime-patch-plan.json" \
  --labels "base" "runtime" \
  --output "${OUT_DIR}/root-cause-summary.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/root-cause-summary.json" \
  --schema schemas/root-cause-summary.schema.json \
  --report "${VALIDATION_DIR}/root-cause-summary-validation.json"

"${PYTHON_BIN}" -m compat_runtime.test_impact.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --root-cause "${OUT_DIR}/root-cause-summary.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --output "${OUT_DIR}/test-impact-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/test-impact-report.json" \
  --schema schemas/test-impact-report.schema.json \
  --report "${VALIDATION_DIR}/test-impact-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.rollback_hints.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/rollback-hints.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/rollback-hints.json" \
  --schema schemas/rollback-hints.schema.json \
  --report "${VALIDATION_DIR}/rollback-hints-validation.json"

"${PYTHON_BIN}" -m compat_runtime.proposal_risk.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --patch-plan-diff "${OUT_DIR}/patch-plan-diff.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --rollback-hints "${OUT_DIR}/rollback-hints.json" \
  --output "${OUT_DIR}/proposal-risk-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/proposal-risk-report.json" \
  --schema schemas/proposal-risk-report.schema.json \
  --report "${VALIDATION_DIR}/proposal-risk-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.hook_backlog.cli \
  --runtime-signal-report "${OUT_DIR}/runtime-signal-report.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --output "${OUT_DIR}/hook-backlog-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/hook-backlog-report.json" \
  --schema schemas/hook-backlog-report.schema.json \
  --report "${VALIDATION_DIR}/hook-backlog-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.proposal_review_checklist.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --patch-plan-diff "${OUT_DIR}/patch-plan-diff.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --rollback-hints "${OUT_DIR}/rollback-hints.json" \
  --proposal-risk "${OUT_DIR}/proposal-risk-report.json" \
  --output "${OUT_DIR}/proposal-review-checklist.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/proposal-review-checklist.json" \
  --schema schemas/proposal-review-checklist.schema.json \
  --report "${VALIDATION_DIR}/proposal-review-checklist-validation.json"

"${PYTHON_BIN}" -m compat_runtime.release_readiness.cli \
  --execution-report "${OUT_DIR}/execution-report.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --matrix-output "${OUT_DIR}/compatibility-matrix.json" \
  --checklist-output "${OUT_DIR}/alpha-release-checklist.json" \
  --manifest-output "${OUT_DIR}/release-bundle-manifest.json" \
  --artifacts \
    "${OUT_DIR}/trace.json" \
    "${OUT_DIR}/gaps.json" \
    "${OUT_DIR}/patch-plan.json" \
    "${OUT_DIR}/patch-template-catalog.json" \
    "${OUT_DIR}/proposal-provenance.json" \
    "${OUT_DIR}/patch-plan-diff.json" \
    "${OUT_DIR}/runtime-trace.json" \
    "${OUT_DIR}/crash-signature-report.json" \
    "${OUT_DIR}/installer-phase-report.json" \
    "${OUT_DIR}/runtime-signal-report.json" \
    "${OUT_DIR}/runtime-gaps.json" \
    "${OUT_DIR}/runtime-patch-plan.json" \
    "${OUT_DIR}/root-cause-summary.json" \
    "${OUT_DIR}/test-impact-report.json" \
    "${OUT_DIR}/rollback-hints.json" \
    "${OUT_DIR}/proposal-risk-report.json" \
    "${OUT_DIR}/hook-backlog-report.json" \
    "${OUT_DIR}/proposal-review-checklist.json" \
    "${OUT_DIR}/execution-report.json" \
    "${OUT_DIR}/trend-report.json" \
    "${OUT_DIR}/kpi-report.json" \
    "${OUT_DIR}/dashboard-timeseries.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/compatibility-matrix.json" \
  --schema schemas/compatibility-matrix.schema.json \
  --report "${VALIDATION_DIR}/compatibility-matrix-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/alpha-release-checklist.json" \
  --schema schemas/alpha-release-checklist.schema.json \
  --report "${VALIDATION_DIR}/alpha-release-checklist-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-bundle-manifest.json" \
  --schema schemas/release-bundle-manifest.schema.json \
  --report "${VALIDATION_DIR}/release-bundle-manifest-validation.json"

"${PYTHON_BIN}" -m compat_runtime.productization.cli \
  --root "${ROOT_DIR}" \
  --output "${OUT_DIR}/productization-readiness.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/productization-readiness.json" \
  --schema schemas/productization-readiness.schema.json \
  --report "${VALIDATION_DIR}/productization-readiness-validation.json"

"${PYTHON_BIN}" -m compat_runtime.quality_gate.cli \
  --execution-report "${OUT_DIR}/execution-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --crash-signature-report "${OUT_DIR}/crash-signature-report.json" \
  --installer-phase-report "${OUT_DIR}/installer-phase-report.json" \
  --proposal-review-checklist "${OUT_DIR}/proposal-review-checklist.json" \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --output "${OUT_DIR}/quality-gate-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/quality-gate-report.json" \
  --schema schemas/quality-gate-report.schema.json \
  --report "${VALIDATION_DIR}/quality-gate-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.release_decision.cli \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --alpha-release-checklist "${OUT_DIR}/alpha-release-checklist.json" \
  --compatibility-matrix "${OUT_DIR}/compatibility-matrix.json" \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --output "${OUT_DIR}/release-decision-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-decision-report.json" \
  --schema schemas/release-decision-report.schema.json \
  --report "${VALIDATION_DIR}/release-decision-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.iteration_plan.cli \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --hook-backlog-report "${OUT_DIR}/hook-backlog-report.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --test-impact-report "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/iteration-plan-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/iteration-plan-report.json" \
  --schema schemas/iteration-plan-report.schema.json \
  --report "${VALIDATION_DIR}/iteration-plan-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.release_forecast.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --output "${OUT_DIR}/release-forecast-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-forecast-report.json" \
  --schema schemas/release-forecast-report.schema.json \
  --report "${VALIDATION_DIR}/release-forecast-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.readiness_scorecard.cli \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --kpi-report "${OUT_DIR}/kpi-report.json" \
  --output "${OUT_DIR}/readiness-scorecard-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/readiness-scorecard-report.json" \
  --schema schemas/readiness-scorecard-report.schema.json \
  --report "${VALIDATION_DIR}/readiness-scorecard-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.execution_burndown.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --output "${OUT_DIR}/execution-burndown-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-burndown-report.json" \
  --schema schemas/execution-burndown-report.schema.json \
  --report "${VALIDATION_DIR}/execution-burndown-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.validation_command_pack.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --test-impact-report "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/validation-command-pack.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/validation-command-pack.json" \
  --schema schemas/validation-command-pack.schema.json \
  --report "${VALIDATION_DIR}/validation-command-pack-validation.json"

"${PYTHON_BIN}" -m compat_runtime.risk_watchlist.cli \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --hook-backlog-report "${OUT_DIR}/hook-backlog-report.json" \
  --runtime-signal-report "${OUT_DIR}/runtime-signal-report.json" \
  --output "${OUT_DIR}/risk-watchlist-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/risk-watchlist-report.json" \
  --schema schemas/risk-watchlist-report.schema.json \
  --report "${VALIDATION_DIR}/risk-watchlist-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.release_gate_history.cli \
  --dashboard-timeseries "${OUT_DIR}/dashboard-timeseries.json" \
  --trend-report "${OUT_DIR}/trend-report.json" \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --output "${OUT_DIR}/release-gate-history-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-gate-history-report.json" \
  --schema schemas/release-gate-history-report.schema.json \
  --report "${VALIDATION_DIR}/release-gate-history-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.pilot_readiness.cli \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/pilot-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/pilot-readiness-report.json" \
  --schema schemas/pilot-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/pilot-readiness-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.ownership_assignment.cli \
  --iteration-plan-report "${OUT_DIR}/iteration-plan-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --output "${OUT_DIR}/ownership-assignment-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/ownership-assignment-report.json" \
  --schema schemas/ownership-assignment-report.schema.json \
  --report "${VALIDATION_DIR}/ownership-assignment-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.remediation_sprint.cli \
  --ownership-assignment-report "${OUT_DIR}/ownership-assignment-report.json" \
  --execution-burndown-report "${OUT_DIR}/execution-burndown-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --output "${OUT_DIR}/remediation-sprint-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/remediation-sprint-report.json" \
  --schema schemas/remediation-sprint-report.schema.json \
  --report "${VALIDATION_DIR}/remediation-sprint-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.release_brief.cli \
  --pilot-readiness-report "${OUT_DIR}/pilot-readiness-report.json" \
  --readiness-scorecard-report "${OUT_DIR}/readiness-scorecard-report.json" \
  --release-forecast-report "${OUT_DIR}/release-forecast-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/release-brief-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-brief-report.json" \
  --schema schemas/release-brief-report.schema.json \
  --report "${VALIDATION_DIR}/release-brief-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.rollout_guardrails.cli \
  --pilot-readiness-report "${OUT_DIR}/pilot-readiness-report.json" \
  --rollback-hints-report "${OUT_DIR}/rollback-hints.json" \
  --proposal-risk-report "${OUT_DIR}/proposal-risk-report.json" \
  --crash-signature-report "${OUT_DIR}/crash-signature-report.json" \
  --output "${OUT_DIR}/rollout-guardrails-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/rollout-guardrails-report.json" \
  --schema schemas/rollout-guardrails-report.schema.json \
  --report "${VALIDATION_DIR}/rollout-guardrails-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.artifact_health.cli \
  --validation-dir "${VALIDATION_DIR}" \
  --output "${OUT_DIR}/artifact-health-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/artifact-health-report.json" \
  --schema schemas/artifact-health-report.schema.json \
  --report "${VALIDATION_DIR}/artifact-health-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.delivery_cockpit.cli \
  --release-brief-report "${OUT_DIR}/release-brief-report.json" \
  --remediation-sprint-report "${OUT_DIR}/remediation-sprint-report.json" \
  --artifact-health-report "${OUT_DIR}/artifact-health-report.json" \
  --output "${OUT_DIR}/delivery-cockpit-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-cockpit-report.json" \
  --schema schemas/delivery-cockpit-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-cockpit-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.stakeholder_update.cli \
  --delivery-cockpit-report "${OUT_DIR}/delivery-cockpit-report.json" \
  --release-brief-report "${OUT_DIR}/release-brief-report.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --output "${OUT_DIR}/stakeholder-update-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/stakeholder-update-report.json" \
  --schema schemas/stakeholder-update-report.schema.json \
  --report "${VALIDATION_DIR}/stakeholder-update-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.handoff_checklist.cli \
  --stakeholder-update-report "${OUT_DIR}/stakeholder-update-report.json" \
  --ownership-assignment-report "${OUT_DIR}/ownership-assignment-report.json" \
  --rollout-guardrails-report "${OUT_DIR}/rollout-guardrails-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --output "${OUT_DIR}/handoff-checklist-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/handoff-checklist-report.json" \
  --schema schemas/handoff-checklist-report.schema.json \
  --report "${VALIDATION_DIR}/handoff-checklist-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.validation_coverage.cli \
  --validation-dir "${VALIDATION_DIR}" \
  --output "${OUT_DIR}/validation-coverage-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/validation-coverage-report.json" \
  --schema schemas/validation-coverage-report.schema.json \
  --report "${VALIDATION_DIR}/validation-coverage-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.launch_readiness.cli \
  --handoff-checklist-report "${OUT_DIR}/handoff-checklist-report.json" \
  --validation-coverage-report "${OUT_DIR}/validation-coverage-report.json" \
  --quality-gate-report "${OUT_DIR}/quality-gate-report.json" \
  --release-decision-report "${OUT_DIR}/release-decision-report.json" \
  --pilot-readiness-report "${OUT_DIR}/pilot-readiness-report.json" \
  --output "${OUT_DIR}/launch-readiness-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/launch-readiness-report.json" \
  --schema schemas/launch-readiness-report.schema.json \
  --report "${VALIDATION_DIR}/launch-readiness-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.release_packet.cli \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --release-bundle-manifest "${OUT_DIR}/release-bundle-manifest.json" \
  --stakeholder-update-report "${OUT_DIR}/stakeholder-update-report.json" \
  --output "${OUT_DIR}/release-packet-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/release-packet-report.json" \
  --schema schemas/release-packet-report.schema.json \
  --report "${VALIDATION_DIR}/release-packet-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.ops_runbook.cli \
  --rollout-guardrails-report "${OUT_DIR}/rollout-guardrails-report.json" \
  --validation-command-pack "${OUT_DIR}/validation-command-pack.json" \
  --handoff-checklist-report "${OUT_DIR}/handoff-checklist-report.json" \
  --output "${OUT_DIR}/ops-runbook-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/ops-runbook-report.json" \
  --schema schemas/ops-runbook-report.schema.json \
  --report "${VALIDATION_DIR}/ops-runbook-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.dependency_watch.cli \
  --productization-readiness "${OUT_DIR}/productization-readiness.json" \
  --risk-watchlist-report "${OUT_DIR}/risk-watchlist-report.json" \
  --execution-report "${OUT_DIR}/execution-report.json" \
  --output "${OUT_DIR}/dependency-watch-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/dependency-watch-report.json" \
  --schema schemas/dependency-watch-report.schema.json \
  --report "${VALIDATION_DIR}/dependency-watch-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.readiness_delta.cli \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --delivery-cockpit-report "${OUT_DIR}/delivery-cockpit-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --output "${OUT_DIR}/readiness-delta-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/readiness-delta-report.json" \
  --schema schemas/readiness-delta-report.schema.json \
  --report "${VALIDATION_DIR}/readiness-delta-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.delivery_signoff.cli \
  --release-packet-report "${OUT_DIR}/release-packet-report.json" \
  --ops-runbook-report "${OUT_DIR}/ops-runbook-report.json" \
  --dependency-watch-report "${OUT_DIR}/dependency-watch-report.json" \
  --readiness-delta-report "${OUT_DIR}/readiness-delta-report.json" \
  --launch-readiness-report "${OUT_DIR}/launch-readiness-report.json" \
  --output "${OUT_DIR}/delivery-signoff-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/delivery-signoff-report.json" \
  --schema schemas/delivery-signoff-report.schema.json \
  --report "${VALIDATION_DIR}/delivery-signoff-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.repro_package.cli \
  --execution-report "${OUT_DIR}/execution-report.json" \
  --compatibility-matrix "${OUT_DIR}/compatibility-matrix.json" \
  --alpha-checklist "${OUT_DIR}/alpha-release-checklist.json" \
  --output "${OUT_DIR}/repro-package.json" \
  --artifacts \
    "${OUT_DIR}/trace.json" \
    "${OUT_DIR}/gaps.json" \
    "${OUT_DIR}/patch-plan.json" \
    "${OUT_DIR}/patch-template-catalog.json" \
    "${OUT_DIR}/proposal-provenance.json" \
    "${OUT_DIR}/patch-plan-diff.json" \
    "${OUT_DIR}/runtime-trace.json" \
    "${OUT_DIR}/crash-signature-report.json" \
    "${OUT_DIR}/installer-phase-report.json" \
    "${OUT_DIR}/runtime-gaps.json" \
    "${OUT_DIR}/runtime-patch-plan.json" \
    "${OUT_DIR}/root-cause-summary.json" \
    "${OUT_DIR}/test-impact-report.json" \
    "${OUT_DIR}/rollback-hints.json" \
    "${OUT_DIR}/proposal-risk-report.json" \
    "${OUT_DIR}/hook-backlog-report.json" \
    "${OUT_DIR}/proposal-review-checklist.json" \
    "${OUT_DIR}/quality-gate-report.json" \
    "${OUT_DIR}/release-decision-report.json" \
    "${OUT_DIR}/iteration-plan-report.json" \
    "${OUT_DIR}/release-forecast-report.json" \
    "${OUT_DIR}/readiness-scorecard-report.json" \
    "${OUT_DIR}/execution-burndown-report.json" \
    "${OUT_DIR}/validation-command-pack.json" \
    "${OUT_DIR}/risk-watchlist-report.json" \
    "${OUT_DIR}/release-gate-history-report.json" \
    "${OUT_DIR}/pilot-readiness-report.json" \
    "${OUT_DIR}/ownership-assignment-report.json" \
    "${OUT_DIR}/remediation-sprint-report.json" \
    "${OUT_DIR}/release-brief-report.json" \
    "${OUT_DIR}/rollout-guardrails-report.json" \
    "${OUT_DIR}/artifact-health-report.json" \
    "${OUT_DIR}/delivery-cockpit-report.json" \
    "${OUT_DIR}/stakeholder-update-report.json" \
    "${OUT_DIR}/handoff-checklist-report.json" \
    "${OUT_DIR}/validation-coverage-report.json" \
    "${OUT_DIR}/launch-readiness-report.json" \
    "${OUT_DIR}/release-packet-report.json" \
    "${OUT_DIR}/ops-runbook-report.json" \
    "${OUT_DIR}/dependency-watch-report.json" \
    "${OUT_DIR}/readiness-delta-report.json" \
    "${OUT_DIR}/delivery-signoff-report.json" \
    "${OUT_DIR}/execution-report.json" \
    "${OUT_DIR}/trend-report.json" \
    "${OUT_DIR}/kpi-report.json" \
    "${OUT_DIR}/dashboard-timeseries.json" \
    "${OUT_DIR}/compatibility-matrix.json" \
    "${OUT_DIR}/alpha-release-checklist.json" \
    "${OUT_DIR}/release-bundle-manifest.json" \
    "${OUT_DIR}/productization-readiness.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/repro-package.json" \
  --schema schemas/repro-package.schema.json \
  --report "${VALIDATION_DIR}/repro-package-validation.json"

cp "${OUT_DIR}/execution-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/trend-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/kpi-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/dashboard-timeseries.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/compatibility-matrix.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/alpha-release-checklist.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/release-bundle-manifest.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/productization-readiness.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/quality-gate-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/release-decision-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/iteration-plan-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/release-forecast-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/readiness-scorecard-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/execution-burndown-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/validation-command-pack.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/risk-watchlist-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/release-gate-history-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/pilot-readiness-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/ownership-assignment-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/remediation-sprint-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/release-brief-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/rollout-guardrails-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/artifact-health-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/delivery-cockpit-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/stakeholder-update-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/handoff-checklist-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/validation-coverage-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/launch-readiness-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/release-packet-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/ops-runbook-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/dependency-watch-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/readiness-delta-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/delivery-signoff-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/repro-package.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/root-cause-summary.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/patch-plan-diff.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/proposal-provenance.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/crash-signature-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/installer-phase-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/runtime-signal-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/test-impact-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/rollback-hints.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/proposal-risk-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/hook-backlog-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/proposal-review-checklist.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/patch-template-catalog.json" "${BUNDLE_DIR}/"

echo "release bundle: ok"
