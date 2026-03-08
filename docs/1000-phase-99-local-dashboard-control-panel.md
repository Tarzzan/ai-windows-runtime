# Phase 99 - Local Dashboard Control Panel

## Objectif

Fournir un panneau de pilotage local, lisible sans dependance externe, pour suivre l'avancement global du projet et l'etat des risques/qualite.

## Livrables

- Nouveau template statique dashboard:
  - `dashboard-template/index.html`
  - `dashboard-template/assets/styles.css`
  - `dashboard-template/assets/app.js`
- Nouveau generateur de donnees dashboard:
  - `scripts/build_dashboard_data.py`
- Nouveaux scripts d'orchestration:
  - `scripts/refresh-dashboard.sh`
  - `scripts/open-dashboard.sh`
  - `scripts/refresh-and-open-dashboard.sh`
- Support explicite du repertoire bureau utilisateur via `xdg-user-dir DESKTOP`.
- Fallback hors-ligne via `data/dashboard-data.js` precharge dans `index.html`.

## Impact

Le suivi de projet est consultable localement dans un navigateur via une page statique, avec donnees regenerees automatiquement depuis `README`, `docs` et `out/*.json`.

## Fichiers modifies

- `README.md`
- `dashboard-template/index.html`
- `dashboard-template/assets/styles.css`
- `dashboard-template/assets/app.js`
- `scripts/build_dashboard_data.py`
- `scripts/refresh-dashboard.sh`
- `scripts/open-dashboard.sh`
- `scripts/refresh-and-open-dashboard.sh`
