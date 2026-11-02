# P052 — Semantic progress, five-minute stall recovery, and truthful percentage

Research date: 2026-11-02. Repository branch: `checkpoint/plano1-estudo-provider-switch-20261028`. Baseline HEAD inspected: `e912f2eccf926019a6bda72d4e00e690e3833562`.

**Status:** prepared implementation guidance only. No runtime modification, live CLI invocation, test execution, model escalation, or independent model review is claimed. Add one focused implementation TODO (099) and its required independent correction review (100) to the **existing** plan; both remain pending.

## Coverage audit: existing functionality versus missing behavior

| Existing source / plan contract | Already covered | Remaining gap |
|---|---|---|
| `references/PROGRESS_TIMEOUTS.md`, `progress_signal.py`, `progress_watch.py` | 300-second sliding idle policy; `PROGRESS stage=... done=... [total=...] [seq=...]`, `HEARTBEAT`, probes and checkpoint files | `ProgressState.observe_output` renews on each new normalized text; `ProgressMonitor._collect` renews for CPU increases and changed files. Activity can falsely postpone a real stall. `parse_signal` validates nonnegative counters but does not enforce `done <= total` or per-attempt/stage monotonicity. No credible percent display contract. |
| `service_map.py`, `TEST_RESOURCE_MONITORING.md` | Expected-duration metadata and `progress-gap` warning when explicitly configured `expected_duration_seconds > 300` but no mapped signal | No requirement to choose minimal reliable instrumentation at architectural design time, or to flag/adapt when a job unexpectedly crosses five minutes without suitable progress evidence. |
| `resource_watch.py`, `validatectl.py` | Monitored execution from launch; reported stalls, health classes; standalone `repair_route` suggests escalation under semantic failure | Need semantic-stall evidence distinct from noisy CPU/log liveness, bounded diagnostic decision, and an explicit authorized implementation/validation retry loop. A route suggestion is not itself an implementation. |
| `run_isolated.py`, `routingctl.py` | On mapped stalled validation, classification `semantic`, task failure recording and subsequent evidence-based rung escalation already exist | Connect reliable semantic-stall signals to this ladder, verify selected provider/effort is actually stronger and authorized, prevent duplicate/restarted live jobs, and preserve prior validated checkpoints and tests. |
| TODOs 052/053, 054/055, 056/057, 060/061, 062/063, 087/088, 091/092 | Progress clocks, durable jobs, read-only watchdog, low-cost observer, DIRECT monitoring, architecture routing, dynamic repair tasks | None combines **anticipated or discovered long work -> truthful progress -> confirmed absence of progress -> diagnosis -> safe higher-capability code repair -> monitored rerun** as one end-to-end acceptance test. |

The user's requested behavior is **partly present**; therefore avoid duplicating existing watcher, signal, routing, or job implementations. TODO 099 owns the missing end-to-end seam, TODO 100 independently reviews it. Preserve existing task IDs and acceptance checks.

## Recommended architecture

### 1. Instrument before long work, detect at runtime as a fallback

When architectural estimates, workload metadata, or observed prior attempts suggest a validation can exceed **300 seconds total**, ask whether an existing **trusted semantic work-unit counter** exists. Prefer native completed test-case/batch counts, persisted output checkpoints with a known work contract, or a bounded read-only status probe. If reliable, reuse it. If absent and safe/authorized, add a minimal instrumentation hook in the *work-producing code* **before** the next validation run. Do not instrument short commands without a demonstrated need, and do not add noisy per-iteration logging.

When a running validation unexpectedly reaches 300 seconds, evaluate available signals and mark an `instrumentation_gap` if none reliably proves completed work. Attach only safe bounded read-only probes when possible; do not mutate a live process and pretend its historical progress is known. Plan instrumentation for the next authorized implementation attempt if it becomes necessary.

The monitor starts with the process at time zero; five minutes is an *evidence threshold*, not a delay before monitoring. Allow configurable `expected_quiet_seconds` for steps that legitimately cannot emit intermediate results; keep independent optional hard ceilings. Never bypass the user's stop/cancel/pause.

### 2. Distinguish three independent signals

- **Liveness/activity**: PID exists, CPU rises, stdout changes, `HEARTBEAT`, network traffic. Helps diagnosis; **must not** by itself renew the *semantic* five-minute window.
- **Meaningful progress**: a source-owned, verified completed-work counter increases; a uniquely completed stage is acknowledged; a read-only committed checkpoint advances under the expected scope.
- **Dependency health**: application, DB, browser grid, auth, remote job availability. If environmental, repair or pause the environment instead of increasing model intelligence.

Maintain `last_semantic_progress_at` on a monotonic clock independently from `last_activity_at`; identify attempt/run and stage. Treat opaque/untrusted lines as unverified even if they look like PROGRESS. A false-positive busy loop or ever-changing log must not run forever solely because it is active. A long healthy job with real forward checkpoints may run well past five minutes.

Existing `ProgressState` and `ProgressMonitor` own clock decisions; `resource_watch` and `jobctl` consume their trusted results. Do not build a second monitoring daemon or constantly feed output to an AI.

### 3. Cheap portable event format and percentage

Keep the existing backwards-compatible line protocol, for example:

```text
PROGRESS stage=import done=45 total=100 seq=45
HEARTBEAT
ERROR class=semantic fp=0123abcd stage=import
```

The unit `done` is **completed, committed or verified units**, not started work, bytes merely read, CPU utilization or seconds elapsed. Require nonnegative integers, `0 <= done <= total` if total is known and positive, monotonic `done` within the same stage/attempt, `seq` strictly monotonic over actual completed units, and stable/pinned denominators per phase (or explicit invalidation on changed scope). Stage resets must not silently overwrite the global counter. Validate events against the process/generation and a specific trusted producer/probe; parse text as untrusted data, not authority to mark acceptance or success.

**Percentage:** report `floor(100 * done / total)` only for a valid known denominator and label the unit and stage, e.g. `Importação: 45/100 lotes (45% desta etapa)`. Do not extrapolate a **global** percentage from one stage when other work remains. Global percent is allowed only with an explicit fixed, validated weight/total for all required phases, aggregated monotonically, and never show 100% before terminal success. If there is no trustworthy total, report `45 lotes concluídos; total desconhecido` (indeterminate) instead of a fake 45%. Throttle to changed meaningful state or coarse, bounded presentation intervals; keep detailed events on disk when necessary.

### 4. Five-minute stall -> evidence-based repair and retry

At **300 seconds since the last trustworthy semantic advancement** (except a justified explicit quiet window), collect a bounded failure capsule: owned process tree and descendants, last valid progress/counter/percent, status of mapped dependencies, deadlock/wait diagnostics where applicable, recent **redacted** error lines, command/source/map hash, and prior attempts. A deterministic classifier first distinguishes:
- **confirmed implementation defect / infinite loop / reproducible semantic stall** -> terminate **only owned** worker tree after preserving evidence; keep validated checkpoints; if repair was authorized, route a *fresh implementation* to a stronger qualified tier or reasoning effort via existing `routingctl` ladder, then re-run the affected mapped validation with new source hash. Do not just restart identical code and reset the clock.
- **environmental outage / service unhealthy / missing permissions / quota / unavailable provider / configured hard ceiling** -> environment repair, safe pause or policy review; **not** capability escalation.
- **inconclusive evidence or legitimate uninterruptible quiet phase** -> collect bounded additional diagnostics or stop for human review according to explicit policy; no fabricated progress or automatic destructive retry.

Do not increase capability merely due to elapsed wall time. The five-minute threshold triggers *diagnosis*; higher-tier reimplementation requires a supported semantic-fault classification and the user's authorized repair policy. If there is no legitimate stronger model/effort or attempts are exhausted, block with a precise reason.

Orchestrated mode reuses `planctl.fail_task`, route ladder, bounded attempts, lease/generation, `jobctl` status and optional TODO 091 repair graph. Standalone DIRECT mode exposes the same decision but must not silently acquire write permission or create a plan. Never dispatch a duplicate writer or kill an unowned child. A pending detached job remains pending until its terminal outcome is verified.

### 5. Minimum regression matrix

1. Expected >300s in design -> reuses adequate existing probe; absence triggers scoped instrumentation plan before test, not broad log spam.
2. Unexpected >300s mid-run -> instrumentation-gap diagnostic and read-only attach where possible, not retroactive fake events.
3. 20-minute batch run with increasing valid completed-unit checkpoints -> remains alive despite total duration >300s, finishes.
4. Endless timestamp/log spam, constant heartbeats, busy CPU and changing arbitrary file -> **do not** count as semantic progress.
5. Real progress with no aggregate denominator -> count shown, **no fabricated percent**; stage local 45/100 -> explicitly `45%` of that stage.
6. A stage counter resets, denominator changes, `done > total`, duplicate/replayed signals, malformed/truncated log lines or stale-generation updates -> rejected/flagged; never renew idle incorrectly.
7. Valid known-weight multi-stage progress remains monotonic and cannot claim 100% until the whole validation is successful.
8. A deadlock confirmed after 300s and healthy dependencies -> evidence-based semantic classification, owned cleanup, stronger authorized repair route, implementation change and fresh monitored rerun.
9. Database unavailable or remote service stalls -> classified environmental; **no** stronger model and no source overwrite.
10. Ambiguous quiet test with legitimate, documented quiet window -> diagnosis/continued observation or human review; **not** a premature kill.
11. DIRECT validate-only cannot edit code; DIRECT repair explicitly authorized can route and rerun without plan; ORCHESTRATED respects existing task/attempt budget and independent review.
12. Crashes during stop/relaunch and stale job receipt -> no duplicate process, preserved completed subtasks, no false success.
13. Simulated clocks/test fixtures: exact 299/300/301-second boundaries, Windows/POSIX process ownership where available, mapped resource checks, no paid model polling and bounded log/probe overhead.
14. Existing short checks, map fingerprints, CLI exit codes and full JSON diagnostics remain backwards-compatible.

Use deterministic fake clocks/virtual time to avoid real five-minute sleeps in unit tests. Record end-to-end evidence and real source hashes for the independent review.

## Ownership, dependencies and integration

- Proposed TODO 099: one vertical implementation slice over `progress_signal.py`, `progress_watch.py`, `resource_watch.py`, `service_map.py`, `jobctl.py`, `run_isolated.py`, `validatectl.py`, `routingctl.py` and related docs/tests **only as required**; base on accepted 052/053, 054/055, 056/057, 060/061, 062/063, 087/088, 091/092, provider-switch routing contract.
- Proposed TODO 100: separate maximum-qualified reviewer; independently check actual code and runtime tests, fix blockers, re-run and pin evidence.
- Place 099 and 100 before TODO 082, and make integration 082 depend on 100; retain 086 final.
- New implementation tests: `test/optimization/semantic_progress_recovery_self_test.py` with mapped validations `P1_TESTS_099`, `P1_099`, `P1_TESTS_100`, `P1_100`. No test is yet implemented by this plan amendment.

## Primary sources and what they support

1. [Temporal: Detecting Activity Failures](https://docs.temporal.io/encyclopedia/detecting-activity-failures) — long-running work needs application-specific progress/checkpoints, liveness supervision and separately scoped timeouts; heartbeat state can help safe retry.
2. [Prometheus: Instrumentation](https://prometheus.io/docs/practices/instrumentation/) — batch-processing counts, last successfully processed item, stage completion, counter vs gauge and separating batch activity from useful work.
3. [OpenTelemetry: Metrics](https://opentelemetry.io/docs/concepts/signals/metrics/) — cumulative counters versus observable gauges, and units of work as measurable attributes; these are concepts, not a reason to add a telemetry server dependency.
4. [Microsoft: Progress Bars](https://learn.microsoft.com/en-us/windows/win32/uxguide/progress-bars) — determinate percentage requires bounded meaningful progress; unknown work should be indeterminate; never imply 100% until completion.
5. [Python: time.monotonic](https://docs.python.org/3/library/time.html#time.monotonic) — monotonic timestamps for elapsed duration independent of wall-clock adjustment.
6. [Python: subprocess](https://docs.python.org/3/library/subprocess.html#popen-objects) — subprocess output must be drained to avoid blocked pipes mistaken for process stalls.
7. [Oracle Java 21: Diagnostic Tools](https://docs.oracle.com/en/java/javase/21/troubleshoot/diagnostic-tools.html) — jcmd/thread dumps and JVM diagnostics, bounded to known owned processes when applicable.
8. [Microsoft Azure Well-Architected: Monitoring](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/monitoring) — correlate application-level progress with resource/dependency health, not one metric in isolation.
9. [Microsoft Azure Well-Architected: Observability](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/observability) — use structured events, minimal logging, and separate system health from functional processing.
10. [Temporal: Tasks](https://docs.temporal.io/tasks) — persistent checkpoints and replay-resistant retries for long-running operations.

The 300-second threshold is a **user-selected policy**, not a universal recommendation from the cited sources. Source docs establish design principles; this repository's actual model/CLI capabilities and quality/cost deltas require future implementation-time validation.

## Research-only status

This report is not a successful validation of the feature. Implementer and genuinely independent reviewer must execute mapped tests, record hashes and fail rather than fabricate model availability, percent correctness, or security/access evidence.
