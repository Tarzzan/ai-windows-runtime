#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.evidence_catalog.cli \
  --verification-snapshot-report "${OUT_DIR}/verification-snapshot-report.json" \
  --release-packet-report "${OUT_DIR}/release-packet-report.json" \
  --repro-package "${OUT_DIR}/repro-package.json" \
  --output "${OUT_DIR}/evidence-catalog-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/evidence-catalog-report.json" \
  --schema schemas/evidence-catalog-report.schema.json \
  --report "${VALIDATION_DIR}/evidence-catalog-report-validation.json"

echo "evidence catalog report: ok"
