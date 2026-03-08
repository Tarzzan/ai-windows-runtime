#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
TARGET_DIR="${1:-$DESKTOP_DIR/project-dashboard}"

"$ROOT_DIR/scripts/refresh-dashboard.sh" "$TARGET_DIR"
"$ROOT_DIR/scripts/open-dashboard.sh" "$TARGET_DIR" "${2:-8765}"
