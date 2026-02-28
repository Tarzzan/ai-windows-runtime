# Security Review Checklist

## Purpose
Provide a minimum security gate before publishing alpha artifacts.

## Threat Modeling
1. Identify trust boundaries for trace inputs and generated outputs.
2. Check for injection surfaces in CLI argument handling.
3. Review file write paths for traversal or overwrite risk.
4. Confirm no secrets are embedded in examples, tests, or docs.

## Artifact Hygiene
1. Validate all artifacts against schemas.
2. Confirm logs and traces are sanitized.
3. Verify release bundle manifest checksums are generated.

## Dependency & Tooling Review
1. Verify pinned Python tooling versions in `requirements.txt`.
2. Verify CI uses supported Python and Rust versions.
3. Check no new unsafe or escalated commands are introduced.

## Release Gate
1. `scripts/run-full-pipeline.sh out` passes.
2. `scripts/build-release-bundle.sh out out/release-bundle` passes.
3. Required checklist items in `alpha-release-checklist.json` are `pass`.
