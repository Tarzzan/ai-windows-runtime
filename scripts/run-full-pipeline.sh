#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
BASELINE_EXECUTION_REPORT="${BASELINE_EXECUTION_REPORT:-}"
BASELINE_PATCH_PLAN="${BASELINE_PATCH_PLAN:-}"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.trace_collector.cli \
  --input examples/sample-trace.log \
  --output "${OUT_DIR}/trace.json"

"${PYTHON_BIN}" -m compat_runtime.gap_detector.cli \
  --trace "${OUT_DIR}/trace.json" \
  --output "${OUT_DIR}/gaps.json"

"${PYTHON_BIN}" -m compat_runtime.patch_orchestrator.cli \
  --gaps "${OUT_DIR}/gaps.json" \
  --output "${OUT_DIR}/patch-plan.json"

"${PYTHON_BIN}" -m compat_runtime.patch_template_library.cli \
  --gaps "${OUT_DIR}/gaps.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --output "${OUT_DIR}/patch-template-catalog.json"

"${PYTHON_BIN}" -m compat_runtime.proposal_provenance.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --trace "${OUT_DIR}/trace.json" \
  --output "${OUT_DIR}/proposal-provenance.json"

PATCH_PLAN_DIFF_ARGS=(
  --current "${OUT_DIR}/patch-plan.json"
  --current-label "current-base"
  --output "${OUT_DIR}/patch-plan-diff.json"
)
if [[ -n "${BASELINE_PATCH_PLAN}" && -f "${BASELINE_PATCH_PLAN}" ]]; then
  PATCH_PLAN_DIFF_ARGS+=(--baseline "${BASELINE_PATCH_PLAN}" --baseline-label "baseline-base")
fi
"${PYTHON_BIN}" -m compat_runtime.patch_plan_diff.cli "${PATCH_PLAN_DIFF_ARGS[@]}"

"${PYTHON_BIN}" -m compat_runtime.telemetry_adapter.cli \
  --telemetry examples/sample-runtime-telemetry.json \
  --output "${OUT_DIR}/runtime-trace.json"

"${PYTHON_BIN}" -m compat_runtime.gap_detector.cli \
  --trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/runtime-gaps.json"

"${PYTHON_BIN}" -m compat_runtime.crash_signatures.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/crash-signature-report.json"

"${PYTHON_BIN}" -m compat_runtime.installer_phases.cli \
  --trace "${OUT_DIR}/trace.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --output "${OUT_DIR}/installer-phase-report.json"

"${PYTHON_BIN}" -m compat_runtime.patch_orchestrator.cli \
  --gaps "${OUT_DIR}/runtime-gaps.json" \
  --output "${OUT_DIR}/runtime-patch-plan.json"

"${PYTHON_BIN}" -m compat_runtime.root_cause.cli \
  --gaps "${OUT_DIR}/gaps.json" "${OUT_DIR}/runtime-gaps.json" \
  --patch-plans "${OUT_DIR}/patch-plan.json" "${OUT_DIR}/runtime-patch-plan.json" \
  --labels "base" "runtime" \
  --output "${OUT_DIR}/root-cause-summary.json"

"${PYTHON_BIN}" -m compat_runtime.test_impact.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --root-cause "${OUT_DIR}/root-cause-summary.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --output "${OUT_DIR}/test-impact-report.json"

"${PYTHON_BIN}" -m compat_runtime.rollback_hints.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --output "${OUT_DIR}/rollback-hints.json"

"${PYTHON_BIN}" -m compat_runtime.proposal_risk.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --patch-plan-diff "${OUT_DIR}/patch-plan-diff.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --rollback-hints "${OUT_DIR}/rollback-hints.json" \
  --output "${OUT_DIR}/proposal-risk-report.json"

"${PYTHON_BIN}" -m compat_runtime.proposal_review_checklist.cli \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --proposal-provenance "${OUT_DIR}/proposal-provenance.json" \
  --patch-plan-diff "${OUT_DIR}/patch-plan-diff.json" \
  --test-impact "${OUT_DIR}/test-impact-report.json" \
  --rollback-hints "${OUT_DIR}/rollback-hints.json" \
  --proposal-risk "${OUT_DIR}/proposal-risk-report.json" \
  --output "${OUT_DIR}/proposal-review-checklist.json"

scripts/validate-artifacts.sh "$OUT_DIR"

"${PYTHON_BIN}" -m compat_runtime.reporting.cli \
  --trace "${OUT_DIR}/trace.json" \
  --gaps "${OUT_DIR}/gaps.json" \
  --patch-plan "${OUT_DIR}/patch-plan.json" \
  --trace-validation "${VALIDATION_DIR}/trace-validation.json" \
  --gaps-validation "${VALIDATION_DIR}/gaps-validation.json" \
  --patch-plan-validation "${VALIDATION_DIR}/patch-plan-validation.json" \
  --runtime-trace "${OUT_DIR}/runtime-trace.json" \
  --runtime-gaps "${OUT_DIR}/runtime-gaps.json" \
  --runtime-patch-plan "${OUT_DIR}/runtime-patch-plan.json" \
  --runtime-trace-validation "${VALIDATION_DIR}/runtime-trace-validation.json" \
  --output "${OUT_DIR}/execution-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-report.json" \
  --schema schemas/execution-report.schema.json \
  --report "${VALIDATION_DIR}/execution-report-validation.json"

if [[ -n "${BASELINE_EXECUTION_REPORT}" && -f "${BASELINE_EXECUTION_REPORT}" ]]; then
  "${PYTHON_BIN}" -m compat_runtime.trend_report.cli \
    --current "${OUT_DIR}/execution-report.json" \
    --baseline "${BASELINE_EXECUTION_REPORT}" \
    --history "${BASELINE_EXECUTION_REPORT}" "${OUT_DIR}/execution-report.json" \
    --output "${OUT_DIR}/trend-report.json"
else
  "${PYTHON_BIN}" -m compat_runtime.trend_report.cli \
    --current "${OUT_DIR}/execution-report.json" \
    --history "${OUT_DIR}/execution-report.json" \
    --output "${OUT_DIR}/trend-report.json"
fi

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/trend-report.json" \
  --schema schemas/trend-report.schema.json \
  --report "${VALIDATION_DIR}/trend-report-validation.json"

REPORT_LIST=("${OUT_DIR}/execution-report.json")
if [[ -n "${BASELINE_EXECUTION_REPORT}" && -f "${BASELINE_EXECUTION_REPORT}" ]]; then
  REPORT_LIST=("${BASELINE_EXECUTION_REPORT}" "${OUT_DIR}/execution-report.json")
fi

"${PYTHON_BIN}" -m compat_runtime.kpi_tracker.cli \
  --reports "${REPORT_LIST[@]}" \
  --trend "${OUT_DIR}/trend-report.json" \
  --output "${OUT_DIR}/kpi-report.json" \
  --dashboard-output "${OUT_DIR}/dashboard-timeseries.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/kpi-report.json" \
  --schema schemas/kpi-report.schema.json \
  --report "${VALIDATION_DIR}/kpi-report-validation.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/dashboard-timeseries.json" \
  --schema schemas/dashboard-timeseries.schema.json \
  --report "${VALIDATION_DIR}/dashboard-timeseries-validation.json"

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
    "${OUT_DIR}/runtime-gaps.json" \
    "${OUT_DIR}/runtime-patch-plan.json" \
    "${OUT_DIR}/root-cause-summary.json" \
    "${OUT_DIR}/test-impact-report.json" \
    "${OUT_DIR}/rollback-hints.json" \
    "${OUT_DIR}/proposal-risk-report.json" \
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
    "${OUT_DIR}/proposal-review-checklist.json" \
    "${OUT_DIR}/quality-gate-report.json" \
    "${OUT_DIR}/release-decision-report.json" \
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

echo "full pipeline: ok"
