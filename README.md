# AI Windows Runtime

AI Windows Runtime is a new Linux-native Windows compatibility runtime, designed from day one for AI-assisted compatibility iteration.

## Why this project
Current compatibility layers were not built around modern feedback loops (large-scale trace analysis, automated gap detection, patch generation, reproducible validation). This project targets a new architecture where runtime engineering and AI tooling are first-class citizens.

## Primary objective
Deliver a native Ubuntu-compatible runtime that can execute modern Windows installers/apps incrementally, starting with high-friction enterprise scenarios (Office Click-to-Run class installers).

## Repository map
- `docs/` product and engineering strategy
- `src/compat_runtime/` MVP tooling for trace -> gap -> patch proposal loop
- `runtime-core/` native Rust runtime core prototype (PE loader metadata + API dispatcher)
- `schemas/` JSON schemas for runtime evidence artifacts
- `scripts/` reproducible workflows
- `tests/` automated validation
- `.github/workflows/` CI

## Current scope (Phase 153)
This repository currently ships:
1. Planning baseline (vision, architecture, roadmap, risk model).
2. AI compatibility loop prototype (trace -> gaps -> patch plan).
3. Native runtime core prototype in Rust (PE loader + section mapping + import/export parser + relocations + API dispatcher + mini linker + NT process/thread primitives + memory + Win32 sync/file/registry simulation + telemetry hooks).
4. Python telemetry adapter prototype to convert runtime telemetry artifacts into normalized trace artifacts.

Core runtime capabilities in this phase:
1. Parse execution traces.
2. Detect likely compatibility gaps.
3. Produce ranked patch proposals for engineering review.
4. Parse core PE metadata from executable payloads.
5. Map PE headers/sections into an in-memory image model.
6. Parse import descriptors and thunk lists (named APIs + ordinal imports).
7. Parse export tables (DLL name, ordinals, RVAs, exported names).
8. Resolve imports against loaded export modules (mini linker report).
9. Produce per-DLL import/export details in runtime load reports.
10. Apply base relocations (DIR64/HIGHLOW) when image base differs.
11. Resolve imports across multiple provider modules with lookup cache.
12. Report ambiguous symbol matches and collision candidates.
13. Dispatch known APIs as implemented/stubbed/missing decisions.
14. Launch synthetic runtime processes with primary thread + handles.
15. Manage thread lifecycle transitions (running/waiting/resume/exit).
16. Cascade process termination to owned threads with state snapshots.
17. Manage virtual memory regions (alloc/protect/read/write/free) per synthetic process.
18. Simulate first kernel32 calls (CreateProcess/CreateThread/VirtualAlloc/VirtualProtect/ReadWriteProcessMemory/GetExitCodeProcess/TerminateProcess/CloseHandle).
19. Simulate synchronization waits (event/mutex + WaitForSingleObject/WaitForMultipleObjects).
20. Simulate minimal file adapter calls (CreateFile/Open, Read/Write, SetFilePointer, CloseHandle).
21. Simulate minimal registry adapter calls (RegSetValueEx/RegQueryValueEx/RegDeleteValue).
22. Emit structured runtime telemetry events (`start/success/error`) for each simulated Win32 call.
23. Expose telemetry capture API for extraction/drain in deterministic validation flows.
24. Adapt runtime telemetry artifacts into `trace.json` compatible events.
25. Merge telemetry-derived events with baseline traces for unified gap/patch planning.
26. Validate generated artifacts against repository schemas via native validator CLI.
27. Produce machine-readable validation reports for trace/gaps/patch-plan outputs.
28. Generate machine-readable end-to-end execution report artifacts.
29. Run complete pipeline gate (base + runtime + schema validation + execution report) in one script.
30. Generate trend reports from execution artifacts (current vs baseline).
31. Track metric deltas (gaps/proposals/events) and regression/improvement direction.
32. Generate KPI reports from execution/trend artifacts (run health, risk level, action hints).
33. Export dashboard timeseries artifacts for observability and milestone tracking.
34. Generate compatibility matrix and alpha release checklist artifacts.
35. Build release bundle manifest with checksum inventory for packaged deliverables.
36. Publish contributor runbook, corpus contribution protocol, and security review checklist.
37. Validate productization governance artifacts automatically in pipeline gates.
38. Generate deterministic reproduction packages for failing scenarios.
39. Capture environment fingerprint and artifact checksum inventory in repro packages.
40. Validate repro-package artifacts automatically in full pipeline and release bundle flows.
41. Generate root-cause clustering summary artifacts from base/runtime gaps.
42. Correlate gap clusters with patch priorities for actionable triage.
43. Validate root-cause summary artifacts automatically in pipeline gates.
44. Generate patch-plan diff artifacts against optional baseline plans.
45. Detect added/removed/changed proposals with reviewer-focused action hints.
46. Validate patch-plan diff artifacts automatically in pipeline and bundle gates.
47. Generate proposal provenance artifacts linking patch proposals back to gaps and traces.
48. Compute per-proposal provenance scores and evidence excerpts for reviewer traceability.
49. Validate proposal provenance artifacts automatically in pipeline and bundle gates.
50. Generate test impact report artifacts from patch proposals and gap categories.
51. Prioritize suggested test suites with estimated effort and execution commands.
52. Validate test impact report artifacts automatically in pipeline and release bundle gates.
53. Generate rollback hints artifacts aligned with proposal priority and risk levels.
54. Define rollback trigger signals, staged rollback steps, and validation commands per proposal.
55. Validate rollback hints artifacts automatically in pipeline and release bundle gates.
56. Generate proposal review checklist artifacts for engineering approval workflows.
57. Gate approval readiness using provenance, diff, rollback, and test-impact evidence.
58. Validate proposal review checklist artifacts automatically in pipeline and release bundle gates.
59. Generate patch template catalog artifacts with template metadata and usage analytics.
60. Map gap categories to reusable patch templates with priority distribution tracking.
61. Validate patch template catalog artifacts automatically in pipeline and release bundle gates.
62. Generate proposal risk report artifacts with per-proposal risk scores and risk levels.
63. Correlate risk scoring with provenance strength, diff churn, rollback level, and test impact.
64. Validate proposal risk report artifacts automatically in pipeline and release bundle gates.
65. Generate crash signature report artifacts from base/runtime traces.
66. Normalize anomaly signatures and classify priority for crash triage workflows.
67. Validate crash signature report artifacts automatically in pipeline and release bundle gates.
68. Generate installer phase report artifacts from base/runtime traces.
69. Track installer phase timelines with per-phase status rollups.
70. Validate installer phase report artifacts automatically in pipeline and release bundle gates.
71. Generate quality gate aggregation artifact (`quality-gate-report.json`) from execution/KPI/trend/risk/crash/installer/review/productization evidence.
72. Compute release gate status (`pass/warn/fail`) with required vs optional checks and remediation actions.
73. Validate quality gate artifacts automatically in pipeline, release bundle, and reproducible package flows.
74. Generate release decision artifact (`release-decision-report.json`) with `go/hold/no-go` outcome.
75. Consolidate blocking checks (gate/checklist/matrix/productization) and warning budget into one decision surface.
76. Validate release decision artifacts automatically in pipeline, release bundle, and reproducible package flows.
77. Generate runtime signal report artifact (`runtime-signal-report.json`) from base/runtime traces.
78. Enrich COM/WinRT/registry/network/installer/crash-like failures with hook coverage metrics.
79. Validate runtime signal artifacts automatically in pipeline, release bundle, and reproducible package flows.
80. Generate hook backlog report artifact (`hook-backlog-report.json`) from runtime signals + patch/risk evidence.
81. Prioritize missing runtime hooks with urgency (`P0/P1/P2`) and impact scoring per domain.
82. Validate hook backlog artifacts automatically in pipeline, release bundle, and reproducible package flows.
83. Generate iteration plan artifact (`iteration-plan-report.json`) from decision/backlog/risk/test-impact signals.
84. Build prioritized execution tasks (`P0/P1/P2`) with estimated effort and blocking flags.
85. Validate iteration plan artifacts automatically in pipeline, release bundle, and reproducible package flows.
86. Generate release forecast artifact (`release-forecast-report.json`) from iteration/decision/KPI/trend signals.
87. Estimate iterations and timeline to converge toward release readiness (`go`) with explicit assumptions.
88. Validate release forecast artifacts automatically in pipeline, release bundle, and reproducible package flows.
89. Generate readiness scorecard artifact (`readiness-scorecard-report.json`) with a normalized score (0-100).
90. Classify overall posture in `red/amber/green` band with release-candidate flag and factor breakdown.
91. Validate readiness scorecard artifacts automatically in pipeline, release bundle, and reproducible package flows.
92. Generate execution burndown artifact (`execution-burndown-report.json`) from plan/forecast/scorecard signals.
93. Project blocker reduction milestones and short-horizon readiness score movement.
94. Validate execution burndown artifacts automatically in pipeline, release bundle, and reproducible package flows.
95. Generate validation command pack artifact (`validation-command-pack.json`) with quick/blocking/full packs.
96. Deduplicate and prioritize executable validation commands from iteration and test-impact signals.
97. Validate validation command pack artifacts automatically in pipeline, release bundle, and reproducible package flows.
98. Generate risk watchlist artifact (`risk-watchlist-report.json`) from proposal risk, hook backlog, and runtime issues.
99. Consolidate P0/P1/P2 risk entries with evidence for triage governance workflows.
100. Validate risk watchlist artifacts automatically in pipeline, release bundle, and reproducible package flows.
101. Generate release gate history artifact (`release-gate-history-report.json`) from dashboard/trend/gate/decision/scorecard signals.
102. Classify release gate trajectory (`improving/stable/degrading`) for iteration-level steering.
103. Validate release gate history artifacts automatically in pipeline, release bundle, and reproducible package flows.
104. Generate pilot readiness artifact (`pilot-readiness-report.json`) with `ready/limited_pilot/not_ready` recommendation.
105. Correlate blockers, readiness posture, forecast horizon, and watchlist severity before pilot launch.
106. Validate pilot readiness artifacts automatically in pipeline, release bundle, and reproducible package flows.
107. Generate ownership assignment artifact (`ownership-assignment-report.json`) from iteration plan, watchlist, and validation command pack.
108. Map critical tasks and risk entries to explicit owner groups with command alignment for execution.
109. Validate ownership assignment artifacts automatically in pipeline, release bundle, and reproducible package flows.
110. Generate remediation sprint artifact (`remediation-sprint-report.json`) from ownership, burndown, and forecast signals.
111. Bucket remediation workload into `sprint_now/sprint_next/backlog` for short-horizon planning.
112. Validate remediation sprint artifacts automatically in pipeline, release bundle, and reproducible package flows.
113. Generate release brief artifact (`release-brief-report.json`) with executive headline from readiness, pilot, forecast, and risk signals.
114. Consolidate release posture and top risks into a concise stakeholder communication surface.
115. Validate release brief artifacts automatically in pipeline, release bundle, and reproducible package flows.
116. Generate rollout guardrails artifact (`rollout-guardrails-report.json`) from pilot readiness, rollback, risk, and crash signals.
117. Define rollout stop conditions and mandatory safeguards before expanding pilot scope.
118. Validate rollout guardrails artifacts automatically in pipeline, release bundle, and reproducible package flows.
119. Generate artifact health artifact (`artifact-health-report.json`) from validation report inventory coverage.
120. Measure required-report completeness with health ratio and remediation actions.
121. Validate artifact health artifacts automatically in pipeline, release bundle, and reproducible package flows.
122. Generate delivery cockpit artifact (`delivery-cockpit-report.json`) from release brief, remediation sprint, and artifact health signals.
123. Classify consolidated delivery posture as `on_track/watch/at_risk` for governance steering.
124. Validate delivery cockpit artifacts automatically in pipeline, release bundle, and reproducible package flows.
125. Generate stakeholder update artifact (`stakeholder-update-report.json`) from cockpit, brief, and watchlist signals.
126. Publish concise stakeholder highlights with readiness, trajectory, and P0 risk posture.
127. Validate stakeholder update artifacts automatically in pipeline, release bundle, and reproducible package flows.
128. Generate handoff checklist artifact (`handoff-checklist-report.json`) from stakeholder status, ownership, guardrails, and validation commands.
129. Score handoff checks as `pass/warn/fail` before launch sign-off.
130. Validate handoff checklist artifacts automatically in pipeline, release bundle, and reproducible package flows.
131. Generate validation coverage artifact (`validation-coverage-report.json`) from required validation report inventory.
132. Quantify validation completeness with coverage ratio and missing-report tracking.
133. Validate validation coverage artifacts automatically in pipeline, release bundle, and reproducible package flows.
134. Generate launch readiness artifact (`launch-readiness-report.json`) from handoff, coverage, gate, decision, and pilot signals.
135. Classify final launch posture as `ready/limited/blocked` with explicit decision context.
136. Validate launch readiness artifacts automatically in pipeline, release bundle, and reproducible package flows.
137. Generate release packet artifact (`release-packet-report.json`) from launch readiness, bundle manifest, and stakeholder update signals.
138. Confirm packet completeness before handoff by tracking missing bundle entries.
139. Validate release packet artifacts automatically in pipeline, release bundle, and reproducible package flows.
140. Generate ops runbook artifact (`ops-runbook-report.json`) from rollout guardrails, handoff checks, and validation commands.
141. Consolidate stop conditions, safeguards, and executable command set into one operational guide.
142. Validate ops runbook artifacts automatically in pipeline, release bundle, and reproducible package flows.
143. Generate dependency watch artifact (`dependency-watch-report.json`) from productization checks, risk watchlist, and execution status.
144. Track blocking dependency items explicitly before final signoff.
145. Validate dependency watch artifacts automatically in pipeline, release bundle, and reproducible package flows.
146. Generate readiness delta artifact (`readiness-delta-report.json`) from launch readiness, delivery cockpit, and release gate history.
147. Quantify readiness drift and trajectory for escalation decisions.
148. Validate readiness delta artifacts automatically in pipeline, release bundle, and reproducible package flows.
149. Generate delivery signoff artifact (`delivery-signoff-report.json`) from packet, runbook, dependency, and delta evidence.
150. Classify final delivery status as `approved/conditional/blocked` using explicit gating rules.
151. Validate delivery signoff artifacts automatically in pipeline, release bundle, and reproducible package flows.
152. Generate post-release monitor artifact (`post-release-monitor-report.json`) from delivery signoff, runtime signals, and crash signatures.
153. Classify post-release posture as `stable/watch/critical` for short-horizon operational supervision.
154. Validate post-release monitor artifacts automatically in pipeline, release bundle, and reproducible package flows.
155. Generate incident feedback artifact (`incident-feedback-report.json`) from post-release monitor, risk watchlist, and hook backlog signals.
156. Prioritize incident feedback into `P0/P1/P2` for triage and corrective routing.
157. Validate incident feedback artifacts automatically in pipeline, release bundle, and reproducible package flows.
158. Generate backlog refresh artifact (`backlog-refresh-report.json`) from incident feedback, iteration plan, and remediation sprint context.
159. Re-rank next-cycle backlog items based on blocking impact and feedback priority.
160. Validate backlog refresh artifacts automatically in pipeline, release bundle, and reproducible package flows.
161. Generate release retrospective artifact (`release-retrospective-report.json`) from signoff, readiness delta, and gate trajectory.
162. Capture actionable lessons and recurrent failure patterns for governance improvement.
163. Validate release retrospective artifacts automatically in pipeline, release bundle, and reproducible package flows.
164. Generate next-cycle bootstrap artifact (`next-cycle-bootstrap-report.json`) from retrospective, refreshed backlog, and validation commands.
165. Classify next-cycle startup posture as `ready/guarded/blocked` before iteration kickoff.
166. Validate next-cycle bootstrap artifacts automatically in pipeline, release bundle, and reproducible package flows.
167. Generate stability window artifact (`stability-window-report.json`) from post-release monitor, gate trajectory, and readiness delta.
168. Classify stabilization posture as `stable/watch/unstable` for hotfix governance.
169. Validate stability window artifacts automatically in pipeline, release bundle, and reproducible package flows.
170. Generate hotfix planner artifact (`hotfix-planner-report.json`) from stability window, incident feedback, and rollback hints.
171. Classify hotfix execution mode as `routine/accelerated/urgent` with rollback awareness.
172. Validate hotfix planner artifacts automatically in pipeline, release bundle, and reproducible package flows.
173. Generate verification snapshot artifact (`verification-snapshot-report.json`) from validation coverage, bootstrap, and signoff evidence.
174. Capture checkpoint-ready verification posture including missing reports and blockers.
175. Validate verification snapshot artifacts automatically in pipeline, release bundle, and reproducible package flows.
176. Generate evidence catalog artifact (`evidence-catalog-report.json`) from snapshot, release packet, and repro package inventory.
177. Maintain auditable artifact/checksum catalog for governance and compliance review.
178. Validate evidence catalog artifacts automatically in pipeline, release bundle, and reproducible package flows.
179. Generate governance checkpoint artifact (`governance-checkpoint-report.json`) from stability, hotfix, snapshot, and evidence signals.
180. Classify governance verdict as `pass/conditional/block` using explicit checkpoint rules.
181. Validate governance checkpoint artifacts automatically in pipeline, release bundle, and reproducible package flows.
182. Add Office readiness artifact and schema (`office-readiness-report.json`) to quantify Office-specific launch posture.
183. Add configurable policy system with profile support (`alpha/beta/prod`) via `COMPAT_POLICY_PATH` and `COMPAT_POLICY_PROFILE`.
184. Export effective merged policy into `active-policy.json` for runtime observability and governance evidence.
185. Add policy lockfile (`config/active-policy.lock.json`) and drift detection gate (`check-policy-drift.sh`).
186. Add policy lockfile sync check (`check-policy-lockfile-sync.sh`) with local auto-fix mode (`--fix`).
187. Add strict policy config validation gate (`check-policy-config.sh`) with schema + semantic checks.
188. Add policy health artifact (`policy-health-report.json`) with config validity, lockfile sync, and policy hash.
189. Enforce policy health in release gate (`check-release-policy.sh`) before `go`.
190. Propagate policy health signals into release packet summary.
191. Propagate policy health signals into evidence catalog summary.
192. Propagate policy health signals into governance checkpoint summary and verdicting.
193. Add CI gates for policy config check and policy lockfile sync before lint/tests/pipeline.
194. Add a local static dashboard template for project-wide control panel views (progress, timeline, quality, risks, actions).
195. Add automated dashboard data builder from README/docs/out artifacts (`build_dashboard_data.py`) with deterministic JSON output.
196. Add refresh/open scripts that publish the dashboard in the user desktop directory (`xdg-user-dir DESKTOP`) with offline-safe data preload.
197. Add execution confidence artifact (`execution-confidence-report.json`) from readiness, forecast, watchlist, and policy health signals.
198. Validate execution confidence artifacts automatically in pipeline and release bundle flows.
199. Surface execution confidence status and execution mode in the local dashboard control panel.
200. Add execution momentum artifact (`execution-momentum-report.json`) correlating confidence, burndown pressure, gate trajectory, and incident feedback.
201. Validate and package execution momentum artifacts in full pipeline and release bundle workflows.
202. Surface execution momentum posture and momentum index in the local dashboard control panel.
203. Add execution pressure artifact (`execution-pressure-report.json`) correlating momentum, dependency blockers, P0 risk pressure, and validation coverage gaps.
204. Validate and package execution pressure artifacts in full pipeline and release bundle workflows.
205. Surface execution pressure level and pressure index in the local dashboard control panel.
206. Add delivery temperature artifact (`delivery-temperature-report.json`) combining execution pressure with launch/decision context.
207. Validate and package delivery temperature artifacts in full pipeline and release bundle workflows.
208. Surface delivery temperature status and index in the local dashboard control panel.
209. Add control recommendation artifact (`control-recommendation-report.json`) deriving control mode from temperature, confidence, pressure, and release policy status.
210. Validate and package control recommendation artifacts in full pipeline and release bundle workflows.
211. Surface control recommendation mode in the local dashboard control panel.
212. Refresh delivery temperature and control recommendation signals in policy-aware regeneration flow after launch-readiness rebuild.
213. Add dedicated CLIs and build scripts for temperature/control artifacts for reusable automation entry points.
214. Add targeted unit tests for delivery temperature and control recommendation artifact logic.
215. Add control efficiency artifact (`control-efficiency-report.json`) combining confidence, momentum, and validation command pressure.
216. Validate and package control efficiency artifacts in full pipeline and release bundle workflows.
217. Add intervention plan artifact (`intervention-plan-report.json`) deriving execution intervention mode from efficiency, P0 risks, and dependency blockers.
218. Validate and package intervention plan artifacts in full pipeline and release bundle workflows.
219. Surface control efficiency and intervention mode in the local dashboard control panel.
220. Refresh control efficiency and intervention artifacts in the policy-aware regeneration flow after launch-readiness updates.
221. Add dedicated CLIs and build scripts for control efficiency and intervention planning artifacts.
222. Add targeted unit tests for control efficiency and intervention plan artifact logic.
223. Propagate control efficiency/intervention artifacts into repro package and release bundle inventories.
224. Add control efficiency artifact (`control-efficiency-report.json`) to score governance efficiency from confidence, momentum, and validation command pressure.
225. Validate and package control efficiency artifacts in full pipeline and release bundle workflows.
226. Add intervention plan artifact (`intervention-plan-report.json`) to classify execution intervention mode from efficiency, P0 risk load, and dependency blockers.
227. Validate and package intervention plan artifacts in full pipeline and release bundle workflows.
228. Surface control efficiency and intervention mode in the local dashboard control panel with visual indicators.
229. Refresh control efficiency and intervention plan in policy-aware regeneration flow before release packet rebuild.
230. Add dedicated CLIs and build scripts for control efficiency and intervention plan for reusable automation entry points.
231. Add targeted unit tests for control efficiency and intervention plan logic.
232. Propagate control efficiency and intervention artifacts into repro package and release bundle inventories.
233. Add governance friction artifact (`governance-friction-report.json`) combining control efficiency, intervention mode, and validation coverage pressure.
234. Validate and package governance friction artifacts in full pipeline and release bundle workflows.
235. Add cadence recommendation artifact (`cadence-recommendation-report.json`) from governance friction, delivery temperature, and control mode.
236. Validate and package cadence recommendation artifacts in full pipeline and release bundle workflows.
237. Add execution focus artifact (`execution-focus-report.json`) to capture P0 focus list aligned with cadence and ownership.
238. Validate and package execution focus artifacts in full pipeline and release bundle workflows.
239. Surface friction/cadence/focus signals in the local dashboard control panel.
240. Refresh friction/cadence/focus signals in policy-aware regeneration flow before release packet rebuild.
241. Add dedicated CLIs and build scripts for governance friction, cadence recommendation, and execution focus.
242. Add governance friction artifact (`governance-friction-report.json`) from control efficiency, intervention mode, and validation coverage pressure.
243. Validate and package governance friction artifacts in full pipeline and release bundle workflows.
244. Add cadence recommendation artifact (`cadence-recommendation-report.json`) to steer execution speed from friction, temperature, and control mode.
245. Validate and package cadence recommendation artifacts in full pipeline and release bundle workflows.
246. Add execution focus artifact (`execution-focus-report.json`) to track P0 focus list aligned with cadence and ownership scope.
247. Validate and package execution focus artifacts in full pipeline and release bundle workflows.
248. Surface governance friction, cadence, focus count, and owner scope in the local dashboard control panel.
249. Refresh governance friction/cadence/focus signals in policy-aware regeneration flow before release packet rebuild.
250. Add dedicated CLIs and build scripts for governance friction, cadence recommendation, and execution focus automation.
251. Add owner load artifact (`owner-load-report.json`) to map task distribution and overloaded owner groups.
252. Validate and package owner load artifacts in full pipeline and release bundle workflows.
253. Add execution throttle artifact (`execution-throttle-report.json`) from cadence, governance friction, and owner overload pressure.
254. Validate and package execution throttle artifacts in full pipeline and release bundle workflows.
255. Add priority corridor artifact (`priority-corridor-report.json`) from throttle mode, P0 focus depth, and P0 risk posture.
256. Validate and package priority corridor artifacts in full pipeline and release bundle workflows.
257. Surface owner overload, throttle mode, and priority corridor in the local dashboard control panel.
258. Refresh owner load/throttle/priority corridor signals in policy-aware regeneration flow before release packet rebuild.
259. Add dedicated CLIs and build scripts for owner load, execution throttle, and priority corridor automation.
260. Add queue pressure artifact (`queue-pressure-report.json`) combining owner overload, throttle mode, and active priority corridor.
261. Validate and package queue pressure artifacts in full pipeline and release bundle workflows.
262. Add delivery bandwidth artifact (`delivery-bandwidth-report.json`) from queue pressure, cadence recommendation, and owner load posture.
263. Validate and package delivery bandwidth artifacts in full pipeline and release bundle workflows.
264. Add intake guard artifact (`intake-guard-report.json`) from bandwidth mode, release policy status, and priority corridor.
265. Validate and package intake guard artifacts in full pipeline and release bundle workflows.
266. Surface queue pressure, delivery bandwidth, and intake guard in the local dashboard control panel.
267. Refresh queue pressure/bandwidth/intake guard signals in policy-aware regeneration flow before release packet rebuild.
268. Add dedicated CLIs and build scripts for queue pressure, delivery bandwidth, and intake guard automation.
269. Add intake capacity artifact (`intake-capacity-report.json`) from intake guard, bandwidth mode, and queue pressure.
270. Validate and package intake capacity artifacts in full pipeline and release bundle workflows.
271. Add admission control artifact (`admission-control-report.json`) from intake capacity, release policy status, and priority corridor.
272. Validate and package admission control artifacts in full pipeline and release bundle workflows.
273. Add commitment pacing artifact (`commitment-pacing-report.json`) from admission control, refreshed backlog, and bandwidth mode.
274. Validate and package commitment pacing artifacts in full pipeline and release bundle workflows.
275. Surface intake capacity, admission state, and commitment mode in the local dashboard control panel.
276. Refresh intake capacity/admission/commitment signals in policy-aware regeneration flow before release packet rebuild.
277. Add dedicated CLIs and build scripts for intake capacity, admission control, and commitment pacing automation.
278. Add scope budget artifact (`scope-budget-report.json`) from commitment pacing, readiness score, and forecast horizon.
279. Validate and package scope budget artifacts in full pipeline and release bundle workflows.
280. Add admission window artifact (`admission-window-report.json`) from scope budget, admission control, and execution focus saturation.
281. Validate and package admission window artifacts in full pipeline and release bundle workflows.
282. Add commitment guard artifact (`commitment-guard-report.json`) from admission window, P0 watchlist pressure, and release policy status.
283. Validate and package commitment guard artifacts in full pipeline and release bundle workflows.
284. Surface scope budget, admission window, and commitment guard in the local dashboard control panel.
285. Refresh scope budget/window/guard signals in policy-aware regeneration flow before release packet rebuild.
286. Add dedicated CLIs and build scripts for scope budget, admission window, and commitment guard automation.
287. Add portfolio risk budget artifact (`portfolio-risk-budget-report.json`) from commitment guard, P0 watchlist pressure, and readiness score.
288. Validate and package portfolio risk budget artifacts in full pipeline and release bundle workflows.
289. Add delivery-intake sync artifact (`delivery-intake-sync-report.json`) from risk budget mode, admission window, and cadence.
290. Validate and package delivery-intake sync artifacts in full pipeline and release bundle workflows.
291. Add execution reserve artifact (`execution-reserve-report.json`) from delivery-intake sync, scope budget mode, and owner overload pressure.
292. Validate and package execution reserve artifacts in full pipeline and release bundle workflows.
293. Surface portfolio risk budget, delivery-intake sync, and execution reserve in the local dashboard control panel.
294. Refresh risk-budget/sync/reserve signals in policy-aware regeneration flow before release packet rebuild.
295. Add dedicated CLIs and build scripts for portfolio risk budget, delivery-intake sync, and execution reserve automation.
296. Add capacity buffer artifact (`capacity-buffer-report.json`) from execution reserve, owner overload, and backlog refresh pressure.
297. Validate and package capacity buffer artifacts in full pipeline and release bundle workflows.
298. Add intake queue policy artifact (`intake-queue-policy-report.json`) from capacity buffer, delivery-intake sync, and commitment guard.
299. Validate and package intake queue policy artifacts in full pipeline and release bundle workflows.
300. Add scope rebalance artifact (`scope-rebalance-report.json`) from intake queue policy, portfolio risk budget, and scope budget mode.
301. Validate and package scope rebalance artifacts in full pipeline and release bundle workflows.
302. Surface capacity buffer, intake queue policy, and scope rebalance in the local dashboard control panel.
303. Refresh buffer/queue-policy/rebalance signals in policy-aware regeneration flow before release packet rebuild.
304. Add dedicated CLIs and build scripts for capacity buffer, intake queue policy, and scope rebalance automation.
305. Add flow control budget artifact (`flow-control-budget-report.json`) from scope rebalance, capacity buffer, and execution reserve.
306. Validate and package flow control budget artifacts in full pipeline and release bundle workflows.
307. Add intake release window artifact (`intake-release-window-report.json`) from flow control mode, queue policy, and admission window.
308. Validate and package intake release window artifacts in full pipeline and release bundle workflows.
309. Add execution stability guard artifact (`execution-stability-guard-report.json`) from intake release window, P0 risk pressure, and post-release monitor status.
310. Validate and package execution stability guard artifacts in full pipeline and release bundle workflows.
311. Surface flow control budget, intake release window, and execution stability guard in the local dashboard control panel.
312. Refresh flow/release-window/stability-guard signals in policy-aware regeneration flow before release packet rebuild.
313. Add dedicated CLIs and build scripts for flow control budget, intake release window, and execution stability guard automation.
314. Add delivery safety margin artifact (`delivery-safety-margin-report.json`) from execution stability guard, flow control budget, and capacity buffer.
315. Validate and package delivery safety margin artifacts in full pipeline and release bundle workflows.
316. Add intake commitment window artifact (`intake-commitment-window-report.json`) from safety margin, intake release window, and stability guard.
317. Validate and package intake commitment window artifacts in full pipeline and release bundle workflows.
318. Add scope lock state artifact (`scope-lock-state-report.json`) from intake commitment window, scope rebalance, and P0 risk pressure.
319. Validate and package scope lock state artifacts in full pipeline and release bundle workflows.
320. Surface delivery safety margin, intake commitment window, and scope lock state in the local dashboard control panel.
321. Refresh safety/commitment-window/scope-lock signals in policy-aware regeneration flow before release packet rebuild.
322. Add dedicated CLIs and build scripts for delivery safety margin, intake commitment window, and scope lock state automation.
323. Add throughput guard band artifact (`throughput-guard-band-report.json`) from scope lock state, safety margin, and execution reserve.
324. Validate and package throughput guard band artifacts in full pipeline and release bundle workflows.
325. Add intake slot policy artifact (`intake-slot-policy-report.json`) from throughput guard band, commitment window, and intake queue policy.
326. Validate and package intake slot policy artifacts in full pipeline and release bundle workflows.
327. Add scope freeze guard artifact (`scope-freeze-guard-report.json`) from intake slot policy, scope lock state, and P0 risk pressure.
328. Validate and package scope freeze guard artifacts in full pipeline and release bundle workflows.
329. Surface throughput guard band, intake slot policy, and scope freeze guard in the local dashboard control panel.
330. Refresh throughput/slot-policy/freeze-guard signals in policy-aware regeneration flow before release packet rebuild.
331. Add dedicated CLIs and build scripts for throughput guard band, intake slot policy, and scope freeze guard automation.
332. Add delivery stress index artifact (`delivery-stress-index-report.json`) from scope freeze guard, throughput guard band, and P0 risk pressure.
333. Validate and package delivery stress index artifacts in full pipeline and release bundle workflows.
334. Add intake pacing window artifact (`intake-pacing-window-report.json`) from delivery stress, intake slot policy, and intake release window.
335. Validate and package intake pacing window artifacts in full pipeline and release bundle workflows.
336. Add scope transition gate artifact (`scope-transition-gate-report.json`) from intake pacing window, scope freeze guard, and release policy status.
337. Validate and package scope transition gate artifacts in full pipeline and release bundle workflows.
338. Surface delivery stress index, intake pacing window, and scope transition gate in the local dashboard control panel.
339. Refresh stress/pacing/gate signals in policy-aware regeneration flow before release packet rebuild.
340. Add dedicated CLIs and build scripts for delivery stress index, intake pacing window, and scope transition gate automation.
341. Add transition readiness index artifact (`transition-readiness-index-report.json`) from scope transition gate, delivery stress index, and policy compliance.
342. Validate and package transition readiness index artifacts in full pipeline and release bundle workflows.
343. Add intake transition policy artifact (`intake-transition-policy-report.json`) from transition readiness, intake pacing window, and intake slot policy.
344. Validate and package intake transition policy artifacts in full pipeline and release bundle workflows.
345. Add scope admission gate artifact (`scope-admission-gate-report.json`) from intake transition policy, scope freeze guard, and release policy status.
346. Validate and package scope admission gate artifacts in full pipeline and release bundle workflows.
347. Surface transition readiness, intake transition policy, and scope admission gate in the local dashboard control panel.
348. Refresh readiness/transition/admission signals in policy-aware regeneration flow before release packet rebuild.
349. Add dedicated CLIs and build scripts for transition readiness index, intake transition policy, and scope admission gate automation.
350. Add scope reentry readiness artifact (`scope-reentry-readiness-report.json`) from scope admission gate, transition readiness, and P0 watchlist pressure.
351. Validate and package scope reentry readiness artifacts in full pipeline and release bundle workflows.
352. Add intake resumption policy artifact (`intake-resumption-policy-report.json`) from reentry readiness, intake transition policy, and delivery temperature.
353. Validate and package intake resumption policy artifacts in full pipeline and release bundle workflows.
354. Add scope unlock gate artifact (`scope-unlock-gate-report.json`) from intake resumption policy, scope admission gate, and release policy status.
355. Validate and package scope unlock gate artifacts in full pipeline and release bundle workflows.
356. Surface scope reentry readiness, intake resumption policy, and scope unlock gate in the local dashboard control panel.
357. Refresh reentry/resumption/unlock signals in policy-aware regeneration flow before release packet rebuild.
358. Add dedicated CLIs and build scripts for scope reentry readiness, intake resumption policy, and scope unlock gate automation.
194. Add explicit `policy_compliance_level` to `policy-health-report.json` and enforce it in release policy gate.
195. Keep backward-compatible gate behavior by deriving compliance level when older policy health artifacts omit it.
196. Harden pipeline determinism by cleaning stale policy artifacts before early schema validation stages.
197. Generate machine-readable release policy diagnostics (`release-policy-report.json`) from gate checks.
198. Validate release policy diagnostics against dedicated schema in pipeline and bundle flows.
199. Include release policy diagnostics in repro/bundle artifact inventories for audit continuity.
200. Propagate release policy diagnostics into release packet summary (`status` + failure count).
201. Propagate release policy diagnostics into evidence catalog and governance checkpoint summaries.
202. Enforce governance blocking when release policy diagnostics are not `pass`.
203. Propagate release policy diagnostics into delivery signoff summary for final release decision context.
204. Require `release_policy_status=pass` before delivery signoff can be `approved`.
205. Validate delivery signoff schema and tests with release policy status/failure counters.
206. Propagate release policy diagnostics from delivery signoff into post-release monitor summary.
207. Escalate post-release monitor status to `critical` when release policy status is `fail`.
208. Propagate release policy diagnostics into incident feedback summary for triage continuity.
209. Propagate release policy diagnostics into backlog refresh summary for next-cycle prioritization.
210. Propagate release policy diagnostics into next-cycle bootstrap summary and status evaluation.
211. Block next-cycle bootstrap when release policy status is `fail`.
212. Propagate release policy diagnostics into release retrospective summary and lessons.
213. Propagate release policy diagnostics into stability window summary and status classification.
214. Force `stability-window` to `unstable` when release policy status is `fail`.
215. Propagate release policy diagnostics into release brief summary.
216. Propagate release policy diagnostics into delivery cockpit and stakeholder update summaries.
217. Refresh communication chain after release-policy gate in pipeline/bundle for non-stale policy context.
218. Propagate release policy diagnostics into handoff checklist summary and checks.
219. Propagate release policy diagnostics into launch readiness summary.
220. Block launch readiness when release policy status is `fail`.
221. Propagate release policy diagnostics into ops runbook summary.
222. Downgrade ops runbook readiness when release policy status is `fail`.
223. Harden pipeline/bundle against stale ops-runbook artifacts after schema evolution.
224. Rebuild prelaunch artifacts (`handoff`, `launch`) after release-policy diagnostics refresh.
225. Ensure release packet regeneration consumes refreshed prelaunch + communication policy context.
226. Propagate release policy diagnostics into risk watchlist summary.
227. Propagate release policy diagnostics into ownership assignment summary.
228. Propagate release policy diagnostics into remediation sprint summary.
229. Refresh planning chain (`risk-watchlist`, `ownership`, `remediation`) after release-policy diagnostics.
230. Recompute communication and prelaunch artifacts from refreshed planning context before final packet.
231. Propagate release policy diagnostics into release forecast summary.
232. Propagate release policy diagnostics into readiness scorecard summary.
233. Propagate release policy diagnostics into execution burndown summary.
234. Refresh forecast/scorecard/burndown chain after release-policy diagnostics in pipeline and bundle.
194. Include policy artifacts in reproducible package and release bundle outputs.
195. Harden full pipeline against stale packet/catalog/governance artifacts to keep schema validation deterministic.

## Quick start
```bash
cd /home/tarzzan/Wine/ai-windows-runtime
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m compat_runtime.trace_collector.cli --input examples/sample-trace.log --output out/trace.json
python -m compat_runtime.gap_detector.cli --trace out/trace.json --output out/gaps.json
python -m compat_runtime.patch_orchestrator.cli --gaps out/gaps.json --output out/patch-plan.json
python -m compat_runtime.schema_validator.cli --input out/trace.json --schema schemas/trace.schema.json
python -m compat_runtime.schema_validator.cli --input out/gaps.json --schema schemas/gaps.schema.json
python -m compat_runtime.schema_validator.cli --input out/patch-plan.json --schema schemas/patch-plan.schema.json

# Adapt runtime telemetry into trace artifact (optional)
python -m compat_runtime.telemetry_adapter.cli --telemetry examples/sample-runtime-telemetry.json --output out/runtime-trace.json
python -m compat_runtime.gap_detector.cli --trace out/runtime-trace.json --output out/runtime-gaps.json
python -m compat_runtime.patch_orchestrator.cli --gaps out/runtime-gaps.json --output out/runtime-patch-plan.json
python -m compat_runtime.schema_validator.cli --input out/runtime-trace.json --schema schemas/trace.schema.json

# Validate full artifact batch with reports
scripts/validate-artifacts.sh out
scripts/run-full-pipeline.sh out
# out/execution-report.json is generated and schema-validated
scripts/build-trend-report.sh out/execution-report.json
# out/trend-report.json is generated and schema-validated
scripts/build-kpi-report.sh out/execution-report.json out/trend-report.json
# out/kpi-report.json and out/dashboard-timeseries.json are generated and schema-validated
scripts/build-release-bundle.sh out out/release-bundle
# out/compatibility-matrix.json, out/alpha-release-checklist.json and out/release-bundle-manifest.json are generated and schema-validated
scripts/check-productization-readiness.sh out
# out/productization-readiness.json is generated and schema-validated
scripts/build-quality-gate-report.sh out
# out/quality-gate-report.json is generated and schema-validated
scripts/build-release-decision-report.sh out
# out/release-decision-report.json is generated and schema-validated
scripts/build-runtime-signal-report.sh out
# out/runtime-signal-report.json is generated and schema-validated
scripts/build-hook-backlog-report.sh out
# out/hook-backlog-report.json is generated and schema-validated
scripts/build-iteration-plan-report.sh out
# out/iteration-plan-report.json is generated and schema-validated
scripts/build-release-forecast-report.sh out
# out/release-forecast-report.json is generated and schema-validated
scripts/build-readiness-scorecard-report.sh out
# out/readiness-scorecard-report.json is generated and schema-validated
scripts/build-execution-burndown-report.sh out
# out/execution-burndown-report.json is generated and schema-validated
scripts/build-validation-command-pack.sh out
# out/validation-command-pack.json is generated and schema-validated
scripts/build-risk-watchlist-report.sh out
# out/risk-watchlist-report.json is generated and schema-validated
scripts/build-release-gate-history-report.sh out
# out/release-gate-history-report.json is generated and schema-validated
scripts/build-pilot-readiness-report.sh out
# out/pilot-readiness-report.json is generated and schema-validated
scripts/build-ownership-assignment-report.sh out
# out/ownership-assignment-report.json is generated and schema-validated
scripts/build-remediation-sprint-report.sh out
# out/remediation-sprint-report.json is generated and schema-validated
scripts/build-release-brief-report.sh out
# out/release-brief-report.json is generated and schema-validated
scripts/build-rollout-guardrails-report.sh out
# out/rollout-guardrails-report.json is generated and schema-validated
scripts/build-artifact-health-report.sh out
# out/artifact-health-report.json is generated and schema-validated
scripts/build-delivery-cockpit-report.sh out
# out/delivery-cockpit-report.json is generated and schema-validated
scripts/build-stakeholder-update-report.sh out
# out/stakeholder-update-report.json is generated and schema-validated
scripts/build-handoff-checklist-report.sh out
# out/handoff-checklist-report.json is generated and schema-validated
scripts/build-validation-coverage-report.sh out
# out/validation-coverage-report.json is generated and schema-validated
scripts/build-launch-readiness-report.sh out
# out/launch-readiness-report.json is generated and schema-validated
scripts/build-release-packet-report.sh out
# out/release-packet-report.json is generated and schema-validated
scripts/build-ops-runbook-report.sh out
# out/ops-runbook-report.json is generated and schema-validated
scripts/build-dependency-watch-report.sh out
# out/dependency-watch-report.json is generated and schema-validated
scripts/build-readiness-delta-report.sh out
# out/readiness-delta-report.json is generated and schema-validated
scripts/build-delivery-signoff-report.sh out
# out/delivery-signoff-report.json is generated and schema-validated
scripts/build-post-release-monitor-report.sh out
# out/post-release-monitor-report.json is generated and schema-validated
scripts/build-incident-feedback-report.sh out
# out/incident-feedback-report.json is generated and schema-validated
scripts/build-backlog-refresh-report.sh out
# out/backlog-refresh-report.json is generated and schema-validated
scripts/build-release-retrospective-report.sh out
# out/release-retrospective-report.json is generated and schema-validated
scripts/build-next-cycle-bootstrap-report.sh out
# out/next-cycle-bootstrap-report.json is generated and schema-validated
scripts/build-stability-window-report.sh out
# out/stability-window-report.json is generated and schema-validated
scripts/build-hotfix-planner-report.sh out
# out/hotfix-planner-report.json is generated and schema-validated
scripts/build-verification-snapshot-report.sh out
# out/verification-snapshot-report.json is generated and schema-validated
scripts/build-evidence-catalog-report.sh out
# out/evidence-catalog-report.json is generated and schema-validated
scripts/build-governance-checkpoint-report.sh out
# out/governance-checkpoint-report.json is generated and schema-validated
scripts/build-root-cause-summary.sh out
# out/root-cause-summary.json is generated and schema-validated
scripts/build-patch-plan-diff.sh out
# out/patch-plan-diff.json is generated and schema-validated
scripts/build-proposal-provenance.sh out
# out/proposal-provenance.json is generated and schema-validated
scripts/build-crash-signature-report.sh out
# out/crash-signature-report.json is generated and schema-validated
scripts/build-installer-phase-report.sh out
# out/installer-phase-report.json is generated and schema-validated
scripts/build-test-impact-report.sh out
# out/test-impact-report.json is generated and schema-validated
scripts/build-rollback-hints.sh out
# out/rollback-hints.json is generated and schema-validated
scripts/build-proposal-risk-report.sh out
# out/proposal-risk-report.json is generated and schema-validated
scripts/build-proposal-review-checklist.sh out
# out/proposal-review-checklist.json is generated and schema-validated
scripts/build-patch-template-catalog.sh out
# out/patch-template-catalog.json is generated and schema-validated
scripts/build-repro-package.sh out
# out/repro-package.json is generated and schema-validated
pytest -q

# Native runtime core checks
cargo test --manifest-path runtime-core/Cargo.toml
bash scripts/runtime-core-smoke.sh
```

## Product deliverables included
- Vision and strategy
- Architecture blueprint
- 30/60/90 roadmap
- AI compatibility loop design
- Implementation operating model
- Prioritized backlog (50 tasks)
- Risks and mitigations
- Ubuntu proof-of-feasibility plan
- Executable Sprint 01 plan
