# Risques et mitigation

1. Proprietary protocol incompatibilities
- Risk: incomplete behavior despite API coverage.
- Mitigation: evidence-driven targeted implementation + graceful diagnostics.

2. AI false positives in patch proposals
- Risk: engineering time wasted.
- Mitigation: confidence threshold + reviewer checklist + mandatory tests.

3. Runtime complexity explosion
- Risk: broad scope without stable core.
- Mitigation: strict phase gates and scenario-priority matrix.

4. Regression churn
- Risk: one app fix breaks another.
- Mitigation: scenario corpus expansion + regression CI + rollback-ready patches.

5. Contributor onboarding friction
- Risk: low velocity.
- Mitigation: scripted bootstrap + explicit sprint playbooks + artifact contracts.
