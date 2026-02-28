# Plan d'implémentation

## Tech stack (initial)
- Language: Python (MVP tooling), C/Rust reserved for runtime core milestones.
- Packaging: `pyproject.toml` + editable install.
- Tests: `pytest`.
- CI: GitHub Actions (lint + tests + artifact checks).

## Repo structure rules
- `src/compat_runtime/` only production code.
- `tests/` only automated tests.
- `docs/` strategy and decisions.
- `schemas/` versioned contracts.

## Quality gates
- Type + style checks (ruff).
- Unit tests mandatory.
- Schema validation for generated artifacts.
- Changelog update for user-visible behavior.

## Release discipline
- Semantic versioning.
- Release notes with compatibility matrix updates.
- Reproducible scripts for bootstrap and smoke runs.
