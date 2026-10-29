# 056 - Watchdog Keepalive: research revision 2

Date: 2026-10-28. Feature: `F026`. Implementation TODO `056`; independent review TODO `057`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep watchdog observation separate from guarded restart actions, with generation-fenced leases, bounded restart budgets and deduplicated anomaly notifications.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision treats observed inactivity, confirmed death and safe-to-restart as different states and adds restart-storm, PID-reuse and cooperative-cancellation cases.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Separate passive observation from active restart permissions and live-lease checks.
- Check restart-loop protection, scheduler portability and deduplicated alerts.

**Baseline observations:**
- watchdogctl distinguishes status observation from a watch loop that writes a deduplication cache. keepalivectl is the separate active restart component.
- The existing mechanisms inspect lease, runnable work and restart history; absence of a console message is not sufficient reason to start another runner.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/watchdogctl.py` | `3fa923781fb9e87f0a2197cbb996fa92b6571edb41308ff004d278cd616dbb86` | collect_plan:139; classify:222; watch:323 |
| `skill/plan-and-execute/scripts/keepalivectl.py` | `8c19a0cf77c5a05947d89fa73409db0d5004ccae36bccd0cbb401a4637e802fe` | launch:99; check:182 |
| `skill/plan-and-execute/references/WATCHDOG.md` | `5f23918061bb3c7f72fddac6627210f648f69a132b9cc84b848ff32dc44fe1ac` | # Execution watchdog:1; ## Commands and output:5; ## Activity and deduplication:30; ## Host scheduling:40 |

## Deeper analysis and competing approaches

### 1. Design analysis

The watchdog should report a compact anomaly and evidence references without changing plan state. A cached observation cursor can support deduplication, but a status query must not resume work or rewrite completion state. Healthy checks should emit little or no data and never call a model.

### 2. Design analysis

A runner can be silent while blocked on I/O or waiting for a provider. Process death, stale lease, missing session output and no semantic progress are different evidence. Only an owned dead runner with runnable work and no live job conflict is a restart candidate. Unknown remote liveness is not safe-to-restart.

### 3. Design analysis

The keepalive action needs an exclusive generation-fenced lock, a sliding restart budget and backoff. Persist the reason for every refusal and restart attempt. Operator pause/cancel must survive recovery; otherwise a helpful watchdog can repeatedly resurrect work the user deliberately stopped.

### 4. Design analysis

An observer model may suggest a diagnostic after deterministic anomaly detection, but it must not become a second autonomous process controller. A stale recommendation must expire with the observed generation. Cancellation-acknowledgement rules of native agents also apply before replacing their workers.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Watchdog auto-repairs everything | Convenient appearance | Unbounded side effects and restart loops | Reject |
| Read-only watchdog only | Safe diagnosis | Needs operator restart | Keep as default observation |
| Separate guarded keepalive | Controlled recovery | Needs ownership and budgets | Recommended opt-in action |
| LLM decides liveness/restart | Flexible | Cannot reliably prove process ownership | Reject as authority |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Specify an observation record with anomaly class, evidence timestamp and suggested action; never mutate task status or restart from passive status.
2. Require an owned stale/dead local runner, runnable work and restart allowance before keepalive launches. Respect quota pauses, explicit pause and missing credentials.
3. Deduplicate repeated anomalies and bound observation-cache growth. Keep operational scheduling outside the semantic task prompt.
4. Add scheduler examples with explicit user opt-in and platform-specific quoting. Do not install cron/Task Scheduler entries during ordinary implementation.
5. Record restart reasons and outcomes without retaining provider transcripts or secrets. Failed environment probes do not trigger capability escalation.
6. Distinguish silence, death, stale lease and restart eligibility; unknown liveness cannot authorize recovery.
7. Fence keepalive actions by runner generation and preserve explicit user pause/cancel state.
8. Bound restart frequency and deduplicate anomalies without feeding healthy status loops to an LLM.

## Acceptance and counterexamples

- Repeated status calls leave plan/job/process state unchanged.
- A live lease prevents duplicate restart even if the job appears quiet.
- Restart-loop limits and manual pause suppress repeated launches.
- Quota-resume timing is observed without a busy loop or premature paid dispatch.
- Windows/POSIX scheduler command generation is tested independently from actual registration.
- A recycled PID cannot be killed or treated as the old runner.
- Repeated failure reaches a restart-loop guard rather than consuming unlimited attempts.
- User pause remains effective after watchdog and host restart.
- A stale observer suggestion cannot restart a new runner generation.

## Cost, latency and quality decision

Measure recovery delay and false restarts against polling/probe overhead. Healthy watchkeeping has zero model cost; optional diagnosis is bounded per novel anomaly.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-SRE] Google SRE Workbook, [Monitoring](https://sre.google/workbook/monitoring/). Accessed 2026-10-28. Reading scope: Public book chapter monitoring sections inspected; not a claim of reading the whole book. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRY] Amazon Builders Library, [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CAS] Kubernetes, [Kubernetes API Concepts: updates](https://kubernetes.io/docs/reference/using-api/api-concepts/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-MUSE] Meta, [Extending and automating Muse Code](https://dev.meta.ai/docs/muse-code/extending). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E043], [E040], [E056]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Google SRE monitoring alert tests; retry backoff jitter restart storms; conditional lease generation stale writer.

## Unverified limits and refresh triggers

- No host scheduler was installed and no real provider was restarted in this research.
- No operating-system scheduler was installed or run. The plan requires platform-specific deployment tests separately from pure state-machine fixtures.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
