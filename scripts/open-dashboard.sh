#!/usr/bin/env bash
set -euo pipefail

DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
TARGET_DIR="${1:-$DESKTOP_DIR/project-dashboard}"
PORT="${2:-8765}"

if [[ ! -f "$TARGET_DIR/index.html" ]]; then
  echo "dashboard missing in $TARGET_DIR; run ./scripts/refresh-dashboard.sh first" >&2
  exit 1
fi

cd "$TARGET_DIR"
URL="http://127.0.0.1:${PORT}/index.html"

if command -v xdg-open >/dev/null 2>&1; then
  (xdg-open "$URL" >/dev/null 2>&1 || true)
fi

echo "dashboard url: $URL"
echo "press Ctrl+C to stop server"
python3 -m http.server "$PORT" --bind 127.0.0.1
