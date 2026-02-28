# Phase 3 - Loader exécutable et imports minimaux

## Scope livré
- Extension du module PE pour aller au-delà des métadonnées.
- Mapping mémoire des headers + sections dans une image virtuelle (`mapped_image`).
- Parseur minimal de table d'import (`IMAGE_IMPORT_DESCRIPTOR`) avec extraction des DLL.
- Enrichissement du `LoadReport` côté runtime.
- Mise à jour du smoke test pour vérifier un import réel (`KERNEL32.dll`).

## Capacités nouvelles
1. `load_pe_image(bytes)` retourne:
- `metadata`
- `sections`
- `imports`
- `mapped_image`

2. Le runtime expose:
- `sections_loaded`
- `imports_checked`
- `imported_dlls`

## Fichiers clés
- `runtime-core/src/pe.rs`
- `runtime-core/src/runtime.rs`
- `runtime-core/tests/runtime_flow.rs`
- `scripts/runtime-core-smoke.sh`

## Validation locale
```bash
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
