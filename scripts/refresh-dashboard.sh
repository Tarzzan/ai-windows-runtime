#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
TARGET_DIR="${1:-$DESKTOP_DIR/project-dashboard}"

mkdir -p "$TARGET_DIR/assets" "$TARGET_DIR/data"

"$ROOT_DIR/scripts/build_dashboard_data.py" \
  --repo "$ROOT_DIR" \
  --output "$TARGET_DIR/data/dashboard-data.json"

python3 - <<'PY' "$TARGET_DIR/data/dashboard-data.json" "$TARGET_DIR/data/dashboard-data.js"
import json
import sys
from pathlib import Path
src = Path(sys.argv[1])
dst = Path(sys.argv[2])
payload = json.loads(src.read_text(encoding="utf-8"))
dst.write_text("window.__DASHBOARD_DATA__ = " + json.dumps(payload, ensure_ascii=True) + ";\n", encoding="utf-8")
PY

cp "$ROOT_DIR/dashboard-template/index.html" "$TARGET_DIR/index.html"
cp "$ROOT_DIR/dashboard-template/assets/styles.css" "$TARGET_DIR/assets/styles.css"
cp "$ROOT_DIR/dashboard-template/assets/app.js" "$TARGET_DIR/assets/app.js"

cat > "$TARGET_DIR/README-dashboard.md" <<'MD'
# Dashboard Projet (Local)

## Refresh des donnees

```bash
cd /home/tarzzan/codex/mw2/ai-windows-runtime
./scripts/refresh-dashboard.sh
```

## Ouvrir le dashboard

```bash
cd /home/tarzzan/codex/mw2/ai-windows-runtime
./scripts/open-dashboard.sh
```

Le dashboard lit `data/dashboard-data.json` et affiche:
- avancement global
- timeline des phases
- etat qualite/pipeline
- risques
- prochaines actions
MD

echo "dashboard refreshed: $TARGET_DIR"
