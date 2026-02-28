# Compatibility Matrix Template

## Scope
Template for publishing alpha compatibility status across scenarios.

## Fields
- `scenario_id`: stable scenario identifier.
- `workload`: installer/app category.
- `status`: `pass`, `partial`, `fail`.
- `blocking_gaps`: number of unresolved high/medium blockers.
- `last_validated_at`: UTC timestamp.
- `evidence_artifacts`: paths to trace/gaps/patch plan/report files.
- `notes`: concise actionable context.

## Example Row
| scenario_id | workload | status | blocking_gaps | last_validated_at | evidence_artifacts | notes |
| --- | --- | --- | --- | --- | --- | --- |
| office-clicktorun-bootstrap | installer | partial | 2 | 2026-02-28T00:00:00Z | out/runtime-trace.json; out/runtime-gaps.json | Registry key bootstrap still unstable |

## Publication Guidelines
1. Update matrix only from reproducible pipeline outputs.
2. Keep notes factual and bounded to latest evidence.
3. Include at least one artifact path per row.
