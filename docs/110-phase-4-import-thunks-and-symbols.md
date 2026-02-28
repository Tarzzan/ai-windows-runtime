# Phase 4 - Import thunks et symboles API

## Scope livré
- Parse des thunks d'import (`OriginalFirstThunk` / fallback `FirstThunk`).
- Support des imports nommés (`IMAGE_IMPORT_BY_NAME`) et imports par ordinal.
- Détails des symboles importés dans le rapport runtime.
- Mise à jour du probe CLI pour afficher DLL + liste API.

## Capacités ajoutées
1. `PeImport` inclut maintenant `functions`.
2. `PeImportFunction` expose `thunk_rva` + `symbol`.
3. `PeImportSymbol` supporte:
- `Name { hint, name }`
- `Ordinal(u16)`
4. `LoadReport` expose:
- `import_symbol_count`
- `import_details` (par DLL)

## Fichiers clés
- `runtime-core/src/pe.rs`
- `runtime-core/src/runtime.rs`
- `runtime-core/src/bin/runtime_probe.rs`
- `runtime-core/tests/runtime_flow.rs`
- `scripts/runtime-core-smoke.sh`

## Validation locale
```bash
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```
