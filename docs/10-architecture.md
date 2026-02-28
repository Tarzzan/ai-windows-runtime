# Architecture

## High-level modules
1. `PE Loader Layer`
- Binary loading, section mapping, import resolution, startup orchestration.

2. `NT/Win32 Core`
- Process/thread primitives, memory management adapters, handles, synchronization, file/registry adapters.

3. `COM Subsystem`
- COM activation path, class/object marshaling boundaries, registry-backed class resolution.

4. `WinRT Bridge (targeted)`
- Targeted support for high-impact WinRT APIs required by modern installers.

5. `Runtime Services`
- Registry service, IPC service, diagnostics service, policy engine.

6. `AI Compatibility Plane`
- Trace collection.
- Gap detection.
- Patch proposal generation.
- Validation orchestration.

## Text diagram
```text
Windows App/Installer
        |
        v
  PE Loader + Import Resolver
        |
        v
 NT/Win32 Core ---- COM Layer ---- WinRT Bridge
        |              |               |
        +------ Runtime Services ------+
                       |
                       v
             Evidence/Trace Store
                       |
                       v
      AI Gap Detector -> Patch Proposals -> CI Validation
```

## Engineering boundaries
- Runtime core remains deterministic and test-first.
- AI modules remain advisory and produce structured artifacts.
- Promotion of fixes requires tests + explicit reviewer sign-off.
