# Ubuntu PoC Plan

## Goal
Prove the project can run a full evidence loop on Ubuntu from raw logs to patch proposal artifacts.

## Steps
1. Bootstrap environment with `scripts/bootstrap.sh`.
2. Run trace collection on sample logs.
3. Run gap detector and patch planner.
4. Validate artifact schemas.
5. Run tests and generate summary report.

## PoC outputs
- `out/trace.json`
- `out/gaps.json`
- `out/patch-plan.json`
- test report and lint report

## Acceptance
- All commands run on clean Ubuntu without manual edits.
- Artifacts conform to schemas.
- At least 1 critical blocker detected and mapped to proposal.
