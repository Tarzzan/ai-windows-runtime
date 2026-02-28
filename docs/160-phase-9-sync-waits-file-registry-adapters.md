# Phase 9 - Sync waits et adaptateurs fichier/registre

## Scope livré
- Extension de `ntcore` avec objets de synchronisation et waits déterministes:
  - événements (`manual` / `auto reset`)
  - mutex runtime
  - `WaitForSingleObject` et `WaitForMultipleObjects`
- Extension `ntcore` avec adaptateur fichier minimal en mémoire:
  - ouverture/création (`open_file`)
  - lecture/écriture (`read_file`, `write_file`)
  - déplacement du curseur (`set_file_pointer`)
  - fermeture de handle (`close_handle`)
- Extension `ntcore` avec adaptateur registre clé/valeur:
  - `registry_set_value`
  - `registry_get_value`
  - `registry_delete_value`
- Enrichissement du moteur Win32 simulé (`win32.rs` + `RuntimeCore::simulate_win32_call`) pour couvrir les appels sync/file/registry.

## Capacités ajoutées
1. Nouveaux types sync/wait:
- `WaitStatus`
- `WaitMultipleStatus`

2. Nouveaux appels Win32 simulés:
- `CreateEventW`, `SetEvent`, `ResetEvent`
- `CreateMutexW`, `ReleaseMutex`
- `WaitForSingleObject`, `WaitForMultipleObjects`
- `CreateFileW` (ouverture/création), `ReadFile`, `WriteFile`, `SetFilePointerEx`
- `RegSetValueExW`, `RegQueryValueExW`, `RegDeleteValueW`

3. Snapshot NT enrichi:
- `sync_object_count`
- `open_file_count`
- `registry_key_count`
- `registry_value_count`

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
