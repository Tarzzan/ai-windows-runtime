# Phase 6 - Relocations et linking multi-modules

## Scope livré
- Parse du répertoire de relocations PE (`.reloc`).
- Modèle de relocation runtime (type + offset + RVA cible).
- Application des relocations au chargement pour changement d'image base:
  - `DIR64` (x64)
  - `HIGHLOW` (x86)
- Enrichissement du reporting de chargement:
  - image base
  - nombre de relocations
- Extension du mini linker runtime:
  - résolution sur plusieurs modules providers
  - cache de résolution des imports répétés
  - détection d'ambiguïtés/collisions (plusieurs candidates pour un symbole)

## Capacités ajoutées
1. `LoadedPeImage` contient maintenant:
- `relocations`
- `metadata.image_base`

2. Nouvelle API relocation:
- `parse_relocations(...)`
- `apply_relocations(&mut LoadedPeImage, new_image_base)`

3. `LinkReport` enrichi:
- `cache_hits`
- `ambiguous_symbols`
- `collisions`

4. `ImportResolution` enrichi:
- `ambiguous`

5. `LoadReport` enrichi:
- `image_base`
- `relocations_count`

## Fichiers clés
- `runtime-core/src/pe.rs`
- `runtime-core/src/runtime.rs`
- `runtime-core/src/lib.rs`
- `runtime-core/src/bin/runtime_probe.rs`
- `runtime-core/tests/runtime_flow.rs`

## Validation locale
```bash
cargo fmt --manifest-path runtime-core/Cargo.toml
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
. .venv/bin/activate && pytest -q && ruff check .
```
