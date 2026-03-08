#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="${ROOT_DIR}/src:${PYTHONPATH:-}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

OUT_DIR="${1:-out}"
VALIDATION_DIR="${OUT_DIR}/validation"
mkdir -p "$OUT_DIR" "$VALIDATION_DIR"

"${PYTHON_BIN}" -m compat_runtime.execution_momentum.cli \
  --execution-confidence-report "${OUT_DIR}/execution-confidence-report.json" \
  --execution-burndown-report "${OUT_DIR}/execution-burndown-report.json" \
  --release-gate-history-report "${OUT_DIR}/release-gate-history-report.json" \
  --incident-feedback-report "${OUT_DIR}/incident-feedback-report.json" \
  --output "${OUT_DIR}/execution-momentum-report.json"

"${PYTHON_BIN}" -m compat_runtime.schema_validator.cli \
  --input "${OUT_DIR}/execution-momentum-report.json" \
  --schema schemas/execution-momentum-report.schema.json \
  --report "${VALIDATION_DIR}/execution-momentum-report-validation.json"

echo "execution momentum report: ok"
