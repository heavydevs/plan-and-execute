# F025 / task 054 - Durable supervised jobs and validation handoff

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep supervised jobs as durable owned executions with pinned results; distinguish resuming observation from launching the same side effect again.

## Questions addressed

- Trace job ownership, fingerprints, restart requests and terminal evidence pinning.
- Measure resume without model redispatch and safe cancellation of tracked descendants.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- jobctl tracks job status, ownership, process identity, waiting and cancellation separately from model execution.
- run_isolated can resume validation after a worker checkpoint, avoiding another model call when only a mapped job remains.

### Read targets and integrity

- `skill/plan-and-execute/scripts/jobctl.py` (SHA-256 `63d30aea7a3e7b372078542556c1078e09af486f594c19a200f3f633609a64af`): `status_job` L220-244; `start_job` L367-449; `wait_job` L452-458; `stop_job` L461-477; `supervise` L480-614
- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `validation_checkpoint_fingerprint` L1489-1494
- `skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md` (SHA-256 `acf86af8b92d5faf5ed56364ff3aec56a1ab43cee445e961cbba9ab6576ce526`): `# Progress windows and fixed ceilings` L1; `## Timeout inventory` L5; `## Portable progress and error contract` L25; `## Refactor for progress` L48

## External basis

- [E040] [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - Amazon Builders Library; accessed 2026-10-28.
- [E047] [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) - LangChain; accessed 2026-10-28.
- [E007] [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) - Anthropic; accessed 2026-10-28.
- [E042] [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) - Microsoft; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Restart a validation process whenever observation is interrupted | Simple but can duplicate side effects and discard useful progress. |
| recommended | Idempotent start and pinned terminal receipts | Uses the existing job controller and makes resume cheap and auditable. |
| rejected | Add an external workflow service for every local test | Introduces operational burden before local ownership/receipt defects are measured. |

## Implementation instructions

1. Pin each job request to validation ID, source/map/command digest and execution identity. A stale succeeded job cannot satisfy a new acceptance state.
2. Make start/resume idempotent for an existing live matching job and refuse ambiguous ownership. Do not relaunch merely because a status wait returned75.
3. Persist bounded terminal receipts before releasing ownership, and define recovery after process loss between completion and receipt writing.
4. Preserve job evidence on ordinary interruption. Explicit cancellation/reset must stop owned descendants before removing controls.
5. Keep external side effects outside assumed exactly-once guarantees; expose an idempotency key or a reconciliation requirement for commands that cannot safely repeat.

## Acceptance tests to implement and run

- [ ] Two start requests for the same pinned live job create only one process.
- [ ] A completed validation checkpoint resumes without redispatching the model.
- [ ] A succeeded job with changed source/map/command is rejected as stale.
- [ ] Wait timeout leaves the live job intact and returns its state, not a false failure.
- [ ] Crash/cancel tests preserve receipts or explicitly report uncertainty rather than inventing completion.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Avoid model redispatch and duplicate long test runs. Measure resumed jobs, prevented duplicate launches and stale result rejections; external costs are not inferred from local elapsed time.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Arbitrary shell commands cannot be made exactly-once merely by saving a JSON job record. External services need their own idempotency/reconciliation contract.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **054** now implements this recommendation; task **055** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
