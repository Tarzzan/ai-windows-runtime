# Corpus Contribution Protocol

## Purpose
Define a reproducible process to add new scenario logs/traces to the compatibility corpus.

## Submission Requirements
1. Provide a sanitized raw log input (no credentials, no personal data).
2. Provide scenario metadata: workload type, target app/version, observed blocker.
3. Provide generated artifacts:
- `trace.json`
- `gaps.json`
- `patch-plan.json`
4. Include reproduction command lines used to generate artifacts.

## Validation Steps
1. Run `scripts/run-full-pipeline.sh out`.
2. Validate schemas with `scripts/validate-artifacts.sh out`.
3. Ensure `execution-report.json` is present and `status` is `ok`.

## Acceptance Criteria
1. Contribution includes deterministic inputs and outputs.
2. Artifacts pass schema validation.
3. New scenario improves corpus coverage (new blocker class or workload).

## Rejection Criteria
1. Sensitive data is present in logs or artifacts.
2. Reproduction steps are missing or non-deterministic.
3. Artifacts fail schema validation.
