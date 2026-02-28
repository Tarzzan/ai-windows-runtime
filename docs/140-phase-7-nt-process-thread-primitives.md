# Phase 7 - Primitives NT process/thread

## Scope livré
- Ajout d'un module `NT/Win32 Core` minimal (`ntcore`) dans `runtime-core`.
- Gestion d'un modèle de processus et threads synthétiques:
  - création de process + thread principal.
  - création de threads secondaires.
  - transitions d'état thread (running/waiting/resume/terminated).
  - terminaison de process avec cascade sur threads.
- Ajout d'une table de handles runtime (process/thread) avec résolution handle -> id.
- Exposition de ces primitives via `RuntimeCore`.

## Capacités ajoutées
1. Nouvelles structures runtime:
- `ProcessRecord`, `ThreadRecord`
- `ProcessState`, `ThreadState`
- `ProcessLaunch`, `ThreadLaunch`
- `NtSnapshot`

2. Nouvelles erreurs NT:
- `NtError::UnknownProcess`
- `NtError::UnknownThread`
- `NtError::ProcessTerminated`
- `NtError::ThreadTerminated`
- `NtError::InvalidProcessHandle`
- `NtError::InvalidThreadHandle`

3. Nouvelles API `RuntimeCore`:
- `launch_process(...)`
- `spawn_thread(...)`
- `set_thread_waiting(...)`
- `resume_thread(...)`
- `exit_thread(...)`
- `terminate_process(...)`
- `process(...)`, `thread(...)`
- `process_id_from_handle(...)`, `thread_id_from_handle(...)`
- `nt_snapshot()`

## Fichiers clés
- `runtime-core/src/ntcore.rs`
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
