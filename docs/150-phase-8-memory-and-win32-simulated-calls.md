# Phase 8 - Mémoire virtuelle et premiers appels Win32 simulés

## Scope livré
- Extension de `ntcore` avec une couche mémoire virtuelle par processus:
  - allocation (`alloc_memory`)
  - protection (`set_memory_protection`)
  - lecture/écriture (`read_memory`, `write_memory`)
  - libération (`free_memory`)
- Ajout d'une fermeture explicite de handle (`close_handle`).
- Ajout d'un module `win32` avec un contrat d'appels simulés:
  - `Win32Call`
  - `Win32CallResult`
  - constante `STILL_ACTIVE` (259)
- Exposition via `RuntimeCore` d'un moteur de simulation:
  - `register_phase8_kernel32_apis()`
  - `simulate_win32_call(...)`

## Capacités ajoutées
1. Nouvelles primitives NT:
- `MemoryProtection`
- `MemoryRegion`
- `VirtualAddress`

2. `NtSnapshot` enrichi:
- `memory_region_count`
- `allocated_bytes`

3. Nouvelles erreurs mémoire/handles:
- `UnknownMemoryRegion`
- `MemoryOutOfBounds`
- `MemoryProtectionViolation`
- `InvalidMemorySize`
- `InvalidHandle`

4. Premiers appels kernel32 simulés:
- `CreateProcessW`
- `CreateThread`
- `VirtualAlloc`
- `VirtualProtect`
- `VirtualFree`
- `WriteProcessMemory`
- `ReadProcessMemory`
- `GetExitCodeProcess`
- `TerminateProcess`
- `CloseHandle`

## Fichiers clés
- `runtime-core/src/ntcore.rs`
- `runtime-core/src/win32.rs`
- `runtime-core/src/runtime.rs`
- `runtime-core/src/lib.rs`
- `runtime-core/tests/runtime_flow.rs`

## Validation locale
```bash
cargo fmt --manifest-path runtime-core/Cargo.toml
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
. .venv/bin/activate && pytest -q && ruff check .
```
