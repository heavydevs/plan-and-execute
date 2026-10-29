# F007 / task 018 - Leases, resume, cancellation, reset and guarded cleanup

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Harden crash recovery and cleanup around ownership, process identity and durable receipts; retain the file-backed lifecycle instead of introducing a distributed workflow service.

## Questions addressed

- Trace durable state under power loss, quota pauses, stale leases and cancellation.
- Preserve product files and Plan 2 inputs while deleting only verified control artifacts.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- lifecyclectl uses an active pointer and runner lease to prevent duplicate execution, recover interrupted tasks and guard cleanup.
- The reusable project resource map is outside disposable plan directories. The former Plan2-input exception is no longer needed, but prepared research is still a retained project artifact.

### Read targets and integrity

- `skill/plan-and-execute/scripts/lifecyclectl.py` (SHA-256 `f4a1b9fd2cbd413d073d3f6d14de85df2fabf5e2b6c873a67d258afac7ee6d33`): `lease_is_live` L334-344
- `skill/plan-and-execute/scripts/lifecyclectl_concise.py` (SHA-256 `70dec1d0ec3973869993c505bca5906073c681ca5f24f824e376515da4f252d6`): file-level contract
- `skill/plan-and-execute/scripts/planctl.py` (SHA-256 `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4`): `cleanup_plan` L3460-3509
- `skill/plan-and-execute/references/LIFECYCLE.md` (SHA-256 `df87ef9b893228773a33b1490112f8ac5acbb541bf6691a9d58ba4f20b7c187b`): `# Lifecycle protocol` L1; `## Current/status` L9; `## Activate` L24; `## Resume` L34

## External basis

- [E056] [os.replace and operating-system interfaces](https://docs.python.org/3/library/os.html#os.replace) - Python Software Foundation; accessed 2026-10-28.
- [E047] [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) - LangChain; accessed 2026-10-28.
- [E007] [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) - Anthropic; accessed 2026-10-28.
- [E040] [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - Amazon Builders Library; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Trust a PID or delete the whole work root | Low code cost, unacceptable risk to unrelated work and ambiguous recovery. |
| recommended | Owned leases and pinned receipts with fault injection | Uses existing architecture and buys verifiable recovery at low runtime cost. |
| rejected | Replace the runner with Temporal/LangGraph now | Durability concepts are useful, but framework migration adds services/dependencies without demonstrated need. |

## Implementation instructions

1. Use PID plus process-start identity and host identity when deciding whether a local lease is live. Treat uncertain remote leases conservatively.
2. Add fault-injection tests around claim, checkpoint, atomic replacement and lease release; ensure recovery never fabricates validation or completion.
3. Keep cancel/reset scoped to recognized plan roots and registered jobs. Never run an indiscriminate git clean/reset or remove product source/tests.
4. Pin successful validation receipts to the source/command/map state that produced them; reuse a receipt only if those inputs still match.
5. Preserve prepared reports outside disposable controls and retain incomplete plan state on failure. Document portable relocation rather than asking users to edit task status manually.

## Acceptance tests to implement and run

- [ ] A reused PID does not authorize killing an unrelated process.
- [ ] Interruptions after each state-write boundary retain completed subtasks and recover only in-progress state.
- [ ] Symlinks, parent paths and directories without the plan sentinel cannot be cleaned.
- [ ] Cancelled jobs are stopped before their control directory is removed.
- [ ] Successful cleanup preserves implementation, tests, shared resource inventory and research reports.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Favor deterministic checkpoint reuse over new worker calls. Measure recovery work repeated and duplicate-run prevention, not merely how quickly a lease file disappears.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Power loss, network filesystems and Windows locks require actual platform tests; POSIX mocks are not proof of those guarantees.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **018** now implements this recommendation; task **019** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
