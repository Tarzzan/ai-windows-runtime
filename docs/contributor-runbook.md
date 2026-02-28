# Contributor Runbook

## Purpose
This runbook defines the minimum workflow to contribute safely and reproducibly to AI Windows Runtime.

## Environment Setup
1. Clone the repository and enter the project directory.
2. Run `scripts/bootstrap.sh`.
3. Ensure `pytest -q` and `ruff check .` are green.
4. Ensure `cargo test --manifest-path runtime-core/Cargo.toml` is green.

## End-to-End Validation
1. Run `scripts/run-full-pipeline.sh out`.
2. Run `scripts/runtime-core-smoke.sh`.
3. Verify generated artifacts in `out/` and `out/validation/`.

## Contribution Flow
1. Create focused commits (one phase / one concern).
2. Update docs and schemas with code changes.
3. Add or update tests for each behavior change.
4. Push and verify CI passes.

## Review Expectations
1. No failing tests or lint warnings.
2. No undocumented schema/artifact changes.
3. No destructive commands in automation scripts.
