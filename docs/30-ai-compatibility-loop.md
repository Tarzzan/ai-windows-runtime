# AI Compatibility Loop

## Loop stages
1. Trace ingest
- Normalize runtime logs and execution signals.

2. Gap extraction
- Detect missing APIs, COM activation failures, unimplemented stubs, protocol failures.

3. Prioritization
- Rank by execution impact (startup blocker, install blocker, runtime degradation).

4. Patch proposal
- Produce candidate patch plans with risk and validation scope.

5. Validation
- Run focused regression + scenario replay.

6. Decision
- Accept, reject, or request refinement.

## Artifact contracts
- `trace.json`: normalized events.
- `gaps.json`: structured blockers and confidence.
- `patch-plan.json`: actionable implementation proposals.

## Governance model
- AI outputs are never merged directly.
- Each accepted proposal must map to tests.
- Proposal confidence is tracked and calibrated over time.
