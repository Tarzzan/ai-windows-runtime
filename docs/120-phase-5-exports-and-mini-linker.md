# Phase 5 - Exports et mini linker runtime

## Scope livré
- Parse des exports PE (`IMAGE_EXPORT_DIRECTORY`).
- Extraction du nom DLL exporté + symboles exportés (nom/ordinal/RVA).
- Ajout d'un mini linker runtime:
  - résolution des imports contre les modules exportés fournis.
  - support des imports nommés et imports par ordinal.
- Rapport de linking structuré (résolus / non résolus).

## Capacités ajoutées
1. `LoadedPeImage` contient maintenant:
- `export_dll_name`
- `exports`

2. Nouveau rapport de link:
- `LinkReport`
- `ImportResolution`

3. Le runtime expose:
- `resolve_imports(&consumer, &providers)`

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
