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
cp "${OUT_DIR}/repro-package.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/root-cause-summary.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/patch-plan-diff.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/proposal-provenance.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/crash-signature-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/test-impact-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/rollback-hints.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/proposal-risk-report.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/proposal-review-checklist.json" "${BUNDLE_DIR}/"
cp "${OUT_DIR}/patch-template-catalog.json" "${BUNDLE_DIR}/"

echo "release bundle: ok"
