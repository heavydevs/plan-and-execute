# 050 - Resource Map: research revision 2

Date: 2026-10-28. Feature: `F023`. Implementation TODO `050`; independent review TODO `051`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Maintain a content-fingerprinted, least-privilege resource map with explicit readiness, health and progress roles; reconcile only relevant inventory inputs and fail unknown observations conservatively.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The map is no longer treated as just a list of services. The revision separates discovery, readiness, ongoing health and actual work progress, and adds probe-cost and unsafe-command tests.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Trace change-only discovery, toolchain preflights, service dependencies and freshness fingerprints.
- Test false unhealthy signals, deadlocks and environment versus semantic classification.

**Baseline observations:**
- service_map supplies discovery/freshness and validation binding; resource_watch uses toolchain/resource checks and evidence packets.
- The preserved map contains historical validations unrelated to active tasks. A map entry existing does not prove its command still targets a present file or supported version.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/service_map.py` | `44477da68a3e9fa3f6afb13e77c753385b879d85ec02f16507fff6066923bf29` | scan_inputs:149; validate_data:237 |
| `skill/plan-and-execute/scripts/resource_watch.py` | `22ac707b846a428c832671c6cfc96d9e45b367f5b3a61963ac0258791a5c2184` | run_toolchain_check:271; evaluate_check:322; run_validation:460 |
| `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md` | `a1d0627faf24c2c97cfe4e3b12cbada151d5c849cb2eeb6006cfff5ffa7de79f` | # Test resource inventory and monitoring:1; ## 1. Reuse the project router:5; ## 2. Build a test-to-resource map:84; ## 3. Run mapped validations under the watcher:122 |

## Deeper analysis and competing approaches

### 1. Design analysis

A running process or open port does not prove the dependency is ready for validation. Map the toolchain and resource checks needed by each validation id, and establish readiness before running the command. Keep an explicit empty resource list for tests that require no external service; never infer a dependency from a generic project file alone.

### 2. Design analysis

Fingerprint relevant build, dependency, test and environment declarations by content. A same-size edit or timestamp-preserving replacement must invalidate the inventory. Avoid scanning the entire repository or rereading all service logs for every focused check. Use per-validation selection and cache only within a verified input generation.

### 3. Design analysis

Probes must be bounded, read-only and independent of the model being tested. A health check should not repair or restart a service as a side effect. Sanitize output before recording; unknown, permission-denied or timed-out checks must not be interpreted as healthy. Host/process ownership matters when the same service name exists elsewhere.

### 4. Design analysis

Monitoring cost is itself a budget. Polling too often can load a dependency and create the incident being diagnosed. Configure cadence per resource and stop observers when the owned validation terminates. Keep readiness failures separate from productive task stalls and capability failures.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| No resource map | No setup | Environment failures misclassified as code failures | Small direct tests only when dependencies are truly absent |
| Full discovery before every test | Broad visibility | Repeated I/O and unnecessary probes | Reject |
| Scoped generation-pinned map | Reusable and explainable | Needs freshness and ownership rules | Recommended |
| Always-on external observability stack | Rich operations | New dependency and maintenance cost | Optional project integration, not skill requirement |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Audit every active validation reference against actual files/commands and the discovery snapshot. Replace stale version literals and removed-path checks with contract-based assertions.
2. Fingerprint only relevant discovery inputs and update the map when those inputs change. Do not repeatedly scan all historical logs or unrelated source trees.
3. Distinguish starting, healthy, unhealthy and unknown states; use startup grace and bounded repeated samples before declaring environment failure.
4. Correlate each validation with only its assigned resources, toolchains and logs. Missing privileges or metrics must be reported as unknown, not success or an automatic semantic escalation.
5. Keep the reusable map outside plan cleanup; avoid injecting all resource inventory into every implementation prompt.
6. Separate startup readiness, runtime health and task progress in resource observations.
7. Reject stale content fingerprints and unsafe or unbounded probes; unknown observations never mean healthy.
8. Measure probe count and duration per validation and reuse only generation-valid scoped inventory.

## Acceptance and counterexamples

- Removing a referenced test file or changing toolchain input makes the map stale/actionable.
- A service inside startup grace is not misclassified as unhealthy.
- An unresponsive health probe ends at its bounded timeout and does not stall the watcher.
- A semantic failing test with healthy dependencies differs from a dependency outage.
- Unrelated resources are not probed or read for a focused validation.
- An open port with an unready service blocks dependent validation without escalating the model.
- A same-size build configuration change invalidates the map.
- Probe timeout or permission denial is explicit unknown/environment evidence.
- A map probe cannot silently run a service repair command.

## Cost, latency and quality decision

Measure inventory and probe CPU/I/O separately from test runtime. Reuse validated metadata, not stale health results; no model call is needed for ordinary map reconciliation.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-COMPOSE] Docker, [Control startup and shutdown order](https://docs.docker.com/compose/how-tos/startup-order/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SRE] Google SRE Workbook, [Monitoring](https://sre.google/workbook/monitoring/). Accessed 2026-10-28. Reading scope: Public book chapter monitoring sections inspected; not a claim of reading the whole book. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E043], [E045], [E040]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Docker compose startup order service healthy ready; Google SRE monitoring synthetic signals; bounded health checks command execution.

## Unverified limits and refresh triggers

- Container-local probes do not certify the user's actual databases, JVM deadlocks, networks or Windows services.
- No real project services were started in this research round. Fixture readiness results do not establish production dependency health.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
