# Phase 66: Office Compatibility Plan (Target: Click-to-Run bootstrap)

## Goal
Advance from synthetic Win32 simulation to an Office-focused compatibility slice that can execute and instrument early installer/bootstrap stages deterministically.

## Scope boundary (this phase)
- In scope:
  - Office bootstrap trace ingestion and normalization.
  - Gap prioritization profile specific to Office installer/runtime patterns.
  - Dispatcher/runtime coverage expansion for high-frequency Office dependencies.
  - Deterministic replay harness for repeatable regression checks.
- Out of scope:
  - Full Office feature parity.
  - UI correctness and rendering parity.
  - Production-grade security hardening.

## Office-first API domains to implement next
1. COM activation surface:
   - `CoInitializeEx`, `CoUninitialize`
   - `CoCreateInstance`
   - `CLSIDFromString`, `IIDFromString`
2. Registry depth for Office discovery/install:
   - Enumerate keys/values
   - Open/create nested keys with access flags
   - Basic HKCU/HKLM virtualization policy in synthetic model
3. File/system primitives:
   - Temp path/file APIs
   - Attribute/query metadata APIs
   - Move/replace/delete semantics
4. Process and module inspection:
   - Module handle/query (`GetModuleHandle*`, `GetProcAddress` telemetry parity)
   - Environment block access and command-line parsing hooks
5. Networking bootstrap telemetry (not full stack):
   - HTTP call intent capture stubs with structured outcomes for gap analysis

## Runtime-core changes
1. Add new `Win32Call` variants for COM bootstrap and registry enumeration.
2. Extend dispatcher registry presets with Office profile (`office-bootstrap`).
3. Add structured telemetry attributes:
   - `component=office`
   - `stage=bootstrap|install|first-run`
   - `api_domain=com|registry|filesystem|process|network`
4. Add deterministic failure injection points for top Office gap categories.

## Tooling changes (Python loop)
1. Add Office gap scoring policy:
   - Promote COM/registry/bootstrap failures to P0/P1.
2. Add Office patch template set:
   - COM activation skeleton
   - Registry fallback template
   - Bootstrap network intent handler template
3. Add Office readiness report artifact:
   - `office-readiness-report.json`
   - success criteria: bootstrap coverage, P0 unresolved count, replay stability.

## Validation strategy
1. Replay profile:
   - `office-bootstrap-smoke`
   - deterministic input traces + expected gap/plan delta bounds
2. New tests:
   - Runtime: COM lifecycle + registry enum state transitions
   - Tooling: Office score boosting and template selection assertions
3. Gate:
   - fail if Office P0 unresolved increases vs baseline
   - fail if replay stability classification regresses

## Exit criteria
1. Office bootstrap trace can complete through planned synthetic checkpoints.
2. Office readiness report produced and schema-validated.
3. No regression in existing pipeline artifacts/tests.
4. Clear next backlog for phase 67 (installer deepening + service interactions).

