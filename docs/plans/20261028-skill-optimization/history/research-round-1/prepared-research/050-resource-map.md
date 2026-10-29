# F023 / task 050 - Resource discovery, freshness and runtime health

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Retain the reusable project resource map with change-scoped freshness and bounded preflights; make missing or stale evidence visible.

## Questions addressed

- Trace change-only discovery, toolchain preflights, service dependencies and freshness fingerprints.
- Test false unhealthy signals, deadlocks and environment versus semantic classification.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- service_map supplies discovery/freshness and validation binding; resource_watch uses toolchain/resource checks and evidence packets.
- The preserved map contains historical validations unrelated to active tasks. A map entry existing does not prove its command still targets a present file or supported version.

### Read targets and integrity

- `skill/plan-and-execute/scripts/service_map.py` (SHA-256 `44477da68a3e9fa3f6afb13e77c753385b879d85ec02f16507fff6066923bf29`): `scan_inputs` L149-183; `validate_data` L237-382
- `skill/plan-and-execute/scripts/resource_watch.py` (SHA-256 `22ac707b846a428c832671c6cfc96d9e45b367f5b3a61963ac0258791a5c2184`): `run_toolchain_check` L271-319; `evaluate_check` L322-395; `run_validation` L460-783
- `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md` (SHA-256 `a1d0627faf24c2c97cfe4e3b12cbada151d5c849cb2eeb6006cfff5ffa7de79f`): `# Test resource inventory and monitoring` L1; `## 1. Reuse the project router` L5; `## 2. Build a test-to-resource map` L84; `## 3. Run mapped validations under the watcher` L122

## External basis

- [E043] [Monitoring Distributed Systems, Site Reliability Engineering chapter 6](https://sre.google/sre-book/monitoring-distributed-systems/) - Google SRE; accessed 2026-10-28.
- [E045] [Logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) - OpenTelemetry; accessed 2026-10-28.
- [E040] [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - Amazon Builders Library; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | One large inventory and full polling everywhere | Useful visibility but unnecessary I/O and misleading stale bindings. |
| recommended | Validation-scoped map with freshness and unknown states | Reuses a valuable mechanism while bounding monitoring work. |
| rejected | Replace the map with an LLM reading every log continuously | Consumes tokens and makes operational detection less deterministic. |

## Implementation instructions

1. Audit every active validation reference against actual files/commands and the discovery snapshot. Replace stale version literals and removed-path checks with contract-based assertions.
2. Fingerprint only relevant discovery inputs and update the map when those inputs change. Do not repeatedly scan all historical logs or unrelated source trees.
3. Distinguish starting, healthy, unhealthy and unknown states; use startup grace and bounded repeated samples before declaring environment failure.
4. Correlate each validation with only its assigned resources, toolchains and logs. Missing privileges or metrics must be reported as unknown, not success or an automatic semantic escalation.
5. Keep the reusable map outside plan cleanup; avoid injecting all resource inventory into every implementation prompt.

## Acceptance tests to implement and run

- [ ] Removing a referenced test file or changing toolchain input makes the map stale/actionable.
- [ ] A service inside startup grace is not misclassified as unhealthy.
- [ ] An unresponsive health probe ends at its bounded timeout and does not stall the watcher.
- [ ] A semantic failing test with healthy dependencies differs from a dependency outage.
- [ ] Unrelated resources are not probed or read for a focused validation.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure discovery files scanned, probe count/duration and time-to-detect, plus false unhealthy reports. These deterministic costs are often more relevant than model price for the monitor.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Container-local probes do not certify the user's actual databases, JVM deadlocks, networks or Windows services.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **050** now implements this recommendation; task **051** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
