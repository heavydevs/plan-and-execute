# 052 - Progress Processes: research revision 2

Date: 2026-10-28. Feature: `F024`. Implementation TODO `052`; independent review TODO `053`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use separate liveness, semantic-progress and hard-limit clocks with bounded stream capture and owned process-tree cancellation on each supported operating system.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision rejects CPU usage or repeated output as unconditional progress and adds process-identity, pipe-drain and post-cancellation side-effect cases. The five-minute threshold is an escalation policy, not a reason to miss earlier evidence.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Distinguish progress from heartbeat and fixed ceilings from per-command idle windows.
- Check Windows/POSIX descendant cleanup, CPU false progress and quiet remote I/O.

**Baseline observations:**
- progress_signal distinguishes PROGRESS, ERROR and HEARTBEAT. progress_watch and process_tree support output/metrics/file signals and descendant cleanup.
- The configuration already separates task idle timeout, validation idle windows and hard ceilings. Zero values have documented disable/default behavior that must not be silently changed.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/progress_signal.py` | `5d6feb7540126d4d6bf94cc454d8d7410e8fa89832b8b597be2bc491a9416b3d` | parse_signal:59; probe_file:104 |
| `skill/plan-and-execute/scripts/progress_watch.py` | `304401062eb2773ce91e25a38c01f9490f62fd1b2b97fbe4d184d27fb69f6798` | progress_line:35; safe_glob:45; validate_policy:53; ProgressState:98 |
| `skill/plan-and-execute/scripts/process_tree.py` | `dd7cf0e6c7706426b81301b4725c27863fe0f1e5483d3736413aecea09a3ffa4` | _remember_group_cpu:22; posix_session_processes:30; posix_group_metrics:82; _parse_cpu_time:124 |

## Deeper analysis and competing approaches

### 1. Design analysis

The monitor should observe from command start while avoiding expensive diagnosis during normal work. A five-minute expected-duration threshold can request instrumentation or enable additional probes; it should not mean the first five minutes have no logs, process ownership or cancellation handle. Each validation command starts its own clocks.

### 2. Design analysis

Liveness means a process exists; progress means a declared monotonic work signal or a relevant completed stage; health means dependencies remain usable. A busy loop can consume CPU and a heartbeat can repeat forever. Use CPU/output heuristics only with explicit limitations, quiet-period allowances and independent hard budgets; do not claim they prove useful work.

### 3. Design analysis

Concurrent pipe draining prevents output backpressure from resembling a deadlock. Keep a bounded diagnostic tail and stream owned raw evidence to disk with a size policy. Parse progress records with sequence/counter checks, finite numeric values and bounded lines. An untrusted worker-emitted progress token alone cannot authorize completion.

### 4. Design analysis

Cancellation must target the owned process tree, not just the root PID or every process named python. Use platform mechanisms and process-start identity; test grandchildren and delayed side effects. Windows Job Objects and POSIX groups differ, so unsupported containment must be reported rather than simulated as tested.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| One fixed timeout for whole suite | Simple | Kills long productive work or waits too long on deadlock | Reject |
| Any output/CPU resets idle forever | Keeps active jobs alive | Busy-loop and heartbeat false progress | Reject as sole signal |
| Semantic windows plus independent hard budgets | Separates stalls from productive duration | Needs instrumentation and platform tests | Recommended |
| LLM watches raw logs continuously | Flexible interpretation | High token cost and unreliable liveness authority | Reject |

## Ownership and scope boundary

TODO 052 owns progress/cancellation/output-buffer behavior, including the runner seam. TODO 054 builds supervised-job recovery on its accepted contract.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Prefer completed-work counters or pinned progress files/probes over arbitrary changing text. Heartbeats and watcher telemetry must not refresh semantic progress.
2. Treat CPU activity as supporting evidence, not proof that useful work advances; test busy loops and silent remote I/O separately.
3. Use monotonic clocks for durations and bounded read-only probes. Preserve expected quiet periods without extending an explicit hard ceiling.
4. On cancellation/timeout, terminate the owned tree and drain remaining output safely. Use Windows Job Objects and POSIX process ownership primitives through their tested platform adapters.
5. Record the exact timeout class and last meaningful progress evidence. A hard ceiling is blocked-for-review, not proof a stronger model is needed.
6. Observe owned execution from launch; use five-minute policy only for extra instrumentation or diagnosis, not delayed evidence collection.
7. Separate heartbeat, CPU liveness, semantic progress and dependency health; retain independent hard budgets.
8. Drain streams concurrently with bounded memory and verify owned descendant termination before replacement.

## Acceptance and counterexamples

- Repeated heartbeat-only output does not keep a stalled command alive.
- Increasing completed-work counters renew idle time while a fixed hard ceiling still wins.
- Each command starts a new idle window; the validation set has no unintended aggregate timeout.
- A child scheduled to write later cannot escape timeout cleanup on supported Windows/POSIX runs.
- A CPU-busy infinite loop and a quiet but externally advancing operation produce distinct diagnostic evidence.
- Repeated heartbeat and constant progress counters cannot keep a stalled command alive indefinitely.
- A quiet but correctly progressing checkpointed job is not killed prematurely.
- A grandchild cannot write a delayed file after confirmed tree termination.
- Large stderr output cannot deadlock the reader or grow RAM without bound.

## Cost, latency and quality decision

Deterministic counters and bounded probes replace continuous model reads. Measure false stall cancellations, detection delay, observer overhead and peak memory, not only shorter runtime.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-WINDOWS-JOBS] Microsoft, [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SRE] Google SRE Workbook, [Monitoring](https://sre.google/workbook/monitoring/). Accessed 2026-10-28. Reading scope: Public book chapter monitoring sections inspected; not a claim of reading the whole book. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OVERLOAD] Google SRE Book, [Handling overload](https://sre.google/sre-book/handling-overload/). Accessed 2026-10-28. Reading scope: Public chapter retry/load-control sections inspected; this is distributed-system evidence adapted to the runner. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E041], [E042], [E043], [E045]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Python subprocess communicate memory timeout process group; Windows Job Objects kill on close nested jobs; Google SRE monitoring synthetic test signals.

## Unverified limits and refresh triggers

- Real descendant behavior, permissions and breakaway processes require platform CI. A fake process test only covers the configured contract.
- Cross-platform cancellation guarantees require actual Windows and POSIX tests; current research is not evidence that both environments were exercised.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
