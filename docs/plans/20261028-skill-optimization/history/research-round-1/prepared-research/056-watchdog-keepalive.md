# F026 / task 056 - Read-only watchdog and guarded runner recovery

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep watchdog observation read-only and keepalive restart narrowly authorized, with bounded probes, leases and loop protection.

## Questions addressed

- Separate passive observation from active restart permissions and live-lease checks.
- Check restart-loop protection, scheduler portability and deduplicated alerts.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- watchdogctl distinguishes status observation from a watch loop that writes a deduplication cache. keepalivectl is the separate active restart component.
- The existing mechanisms inspect lease, runnable work and restart history; absence of a console message is not sufficient reason to start another runner.

### Read targets and integrity

- `skill/plan-and-execute/scripts/watchdogctl.py` (SHA-256 `3fa923781fb9e87f0a2197cbb996fa92b6571edb41308ff004d278cd616dbb86`): `collect_plan` L139-211; `classify` L222-256; `watch` L323-342
- `skill/plan-and-execute/scripts/keepalivectl.py` (SHA-256 `8c19a0cf77c5a05947d89fa73409db0d5004ccae36bccd0cbb401a4637e802fe`): `launch` L99-111; `check` L182-193
- `skill/plan-and-execute/references/WATCHDOG.md` (SHA-256 `5f23918061bb3c7f72fddac6627210f648f69a132b9cc84b848ff32dc44fe1ac`): `# Execution watchdog` L1; `## Commands and output` L5; `## Activity and deduplication` L30; `## Host scheduling` L40

## External basis

- [E043] [Monitoring Distributed Systems, Site Reliability Engineering chapter 6](https://sre.google/sre-book/monitoring-distributed-systems/) - Google SRE; accessed 2026-10-28.
- [E040] [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - Amazon Builders Library; accessed 2026-10-28.
- [E056] [os.replace and operating-system interfaces](https://docs.python.org/3/library/os.html#os.replace) - Python Software Foundation; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | One monitor both observes and repairs implicitly | Convenient but blurs authority and can create duplicate runners. |
| recommended | Separate observer and guarded restarter | Preserves the current separation and allows deterministic safety tests. |
| rejected | A permanent model watches and decides when to restart | Costs tokens continuously and creates a less auditable control loop. |

## Implementation instructions

1. Specify an observation record with anomaly class, evidence timestamp and suggested action; never mutate task status or restart from passive status.
2. Require an owned stale/dead local runner, runnable work and restart allowance before keepalive launches. Respect quota pauses, explicit pause and missing credentials.
3. Deduplicate repeated anomalies and bound observation-cache growth. Keep operational scheduling outside the semantic task prompt.
4. Add scheduler examples with explicit user opt-in and platform-specific quoting. Do not install cron/Task Scheduler entries during ordinary implementation.
5. Record restart reasons and outcomes without retaining provider transcripts or secrets. Failed environment probes do not trigger capability escalation.

## Acceptance tests to implement and run

- [ ] Repeated status calls leave plan/job/process state unchanged.
- [ ] A live lease prevents duplicate restart even if the job appears quiet.
- [ ] Restart-loop limits and manual pause suppress repeated launches.
- [ ] Quota-resume timing is observed without a busy loop or premature paid dispatch.
- [ ] Windows/POSIX scheduler command generation is tested independently from actual registration.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Most observation requires no model at all. Measure polling cost, duplicate-alert suppression and prevented restart loops; an LLM should be event-triggered only for bounded ambiguous diagnosis.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No host scheduler was installed and no real provider was restarted in this research.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **056** now implements this recommendation; task **057** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
