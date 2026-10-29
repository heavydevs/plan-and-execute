# F024 / task 052 - Progress windows, cancellation and process-tree safety

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep per-command sliding progress windows distinct from hard ceilings and liveness; strengthen semantic progress and process-tree tests.

## Questions addressed

- Distinguish progress from heartbeat and fixed ceilings from per-command idle windows.
- Check Windows/POSIX descendant cleanup, CPU false progress and quiet remote I/O.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- progress_signal distinguishes PROGRESS, ERROR and HEARTBEAT. progress_watch and process_tree support output/metrics/file signals and descendant cleanup.
- The configuration already separates task idle timeout, validation idle windows and hard ceilings. Zero values have documented disable/default behavior that must not be silently changed.

### Read targets and integrity

- `skill/plan-and-execute/scripts/progress_signal.py` (SHA-256 `5d6feb7540126d4d6bf94cc454d8d7410e8fa89832b8b597be2bc491a9416b3d`): `parse_signal` L59-80; `probe_file` L104-129
- `skill/plan-and-execute/scripts/progress_watch.py` (SHA-256 `304401062eb2773ce91e25a38c01f9490f62fd1b2b97fbe4d184d27fb69f6798`): `progress_line` L35-42; `safe_glob` L45-50; `validate_policy` L53-95; `ProgressState` L98-168
- `skill/plan-and-execute/scripts/process_tree.py` (SHA-256 `dd7cf0e6c7706426b81301b4725c27863fe0f1e5483d3736413aecea09a3ffa4`): `_remember_group_cpu` L22-27; `posix_session_processes` L30-79; `posix_group_metrics` L82-121; `_parse_cpu_time` L124-140

## External basis

- [E041] [subprocess module](https://docs.python.org/3/library/subprocess.html) - Python Software Foundation; accessed 2026-10-28.
- [E042] [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) - Microsoft; accessed 2026-10-28.
- [E043] [Monitoring Distributed Systems, Site Reliability Engineering chapter 6](https://sre.google/sre-book/monitoring-distributed-systems/) - Google SRE; accessed 2026-10-28.
- [E045] [Logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) - OpenTelemetry; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Raise every timeout after a stall | Quick workaround but hides deadlocks and spends quota/time without evidence. |
| recommended | Semantic progress plus separate ceilings and owned cleanup | More precise failure diagnosis with bounded monitoring overhead. |
| rejected | Treat any log line or CPU increment as progress | Allows infinite noisy loops and confuses liveness with useful work. |

## Implementation instructions

1. Prefer completed-work counters or pinned progress files/probes over arbitrary changing text. Heartbeats and watcher telemetry must not refresh semantic progress.
2. Treat CPU activity as supporting evidence, not proof that useful work advances; test busy loops and silent remote I/O separately.
3. Use monotonic clocks for durations and bounded read-only probes. Preserve expected quiet periods without extending an explicit hard ceiling.
4. On cancellation/timeout, terminate the owned tree and drain remaining output safely. Use Windows Job Objects and POSIX process ownership primitives through their tested platform adapters.
5. Record the exact timeout class and last meaningful progress evidence. A hard ceiling is blocked-for-review, not proof a stronger model is needed.

## Acceptance tests to implement and run

- [ ] Repeated heartbeat-only output does not keep a stalled command alive.
- [ ] Increasing completed-work counters renew idle time while a fixed hard ceiling still wins.
- [ ] Each command starts a new idle window; the validation set has no unintended aggregate timeout.
- [ ] A child scheduled to write later cannot escape timeout cleanup on supported Windows/POSIX runs.
- [ ] A CPU-busy infinite loop and a quiet but externally advancing operation produce distinct diagnostic evidence.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure false-stall and missed-stall rates, cancellation latency and probe overhead. Do not activate an expensive model merely because five minutes elapsed.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Real descendant behavior, permissions and breakaway processes require platform CI. A fake process test only covers the configured contract.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **052** now implements this recommendation; task **053** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
