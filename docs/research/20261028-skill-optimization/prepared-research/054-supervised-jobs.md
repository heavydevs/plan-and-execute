# 054 - Supervised Jobs: research revision 2

Date: 2026-10-28. Feature: `F025`. Implementation TODO `054`; independent review TODO `055`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Make supervised validation jobs idempotent, generation-bound state machines that resume validation without redispatching the implementation model and reconcile uncertain job outcomes before restart.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision adds the crash window between process launch and receipt persistence, map-generation binding and the difference between detached job liveness and validated success.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Trace job ownership, fingerprints, restart requests and terminal evidence pinning.
- Measure resume without model redispatch and safe cancellation of tracked descendants.

**Baseline observations:**
- jobctl tracks job status, ownership, process identity, waiting and cancellation separately from model execution.
- run_isolated can resume validation after a worker checkpoint, avoiding another model call when only a mapped job remains.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/jobctl.py` | `63d30aea7a3e7b372078542556c1078e09af486f594c19a200f3f633609a64af` | status_job:220; start_job:367; wait_job:452; stop_job:461 |
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | validation_checkpoint_fingerprint:1489 |
| `skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md` | `acf86af8b92d5faf5ed56364ff3aec56a1ab43cee445e961cbba9ab6576ce526` | # Progress windows and fixed ceilings:1; ## Timeout inventory:5; ## Portable progress and error contract:25; ## Refactor for progress:48 |

## Deeper analysis and competing approaches

### 1. Design analysis

A durable job is not just a subprocess launched with a detached flag. Its record should bind job id, task/attempt, command, working directory, input/map digest and owned process identity. A receipt from an older command or changed source cannot satisfy the current task even when it reports exit zero.

### 2. Design analysis

Launching a process and writing metadata are not one atomic transaction. If the host crashes between those operations, recovery must reconcile the owned process or an idempotency marker before launching a duplicate. Never promise exactly-once execution merely because a JSON file was written atomically.

### 3. Design analysis

An implementation report may be ready while long validation remains running. Persist that checkpoint so resume waits for or revalidates the same job instead of spending another model call to reimplement the feature. A succeeded job still needs freshness checks; a missing process with no terminal record is an unknown outcome, not success.

### 4. Design analysis

Cancellation and cleanup must be ordered: request stop, establish terminal state, preserve diagnostic evidence, then remove only disposable owned artifacts. Remote or inaccessible process state must fail closed. Keep this machinery reusable for standalone validation rather than creating a second job engine.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Rerun implementation after every interruption | Easy control flow | Duplicates edits and model cost | Reject |
| Treat a detached PID as durable state | Minimal metadata | PID reuse and lost outcomes | Reject |
| Journaled job identity plus reconciliation | Resumable and cost-efficient | Requires crash-window tests | Recommended |
| External workflow database for every job | Strong centralized durability | Operational dependency disproportionate here | Defer until multi-host scale requires it |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Pin each job request to validation ID, source/map/command digest and execution identity. A stale succeeded job cannot satisfy a new acceptance state.
2. Make start/resume idempotent for an existing live matching job and refuse ambiguous ownership. Do not relaunch merely because a status wait returned75.
3. Persist bounded terminal receipts before releasing ownership, and define recovery after process loss between completion and receipt writing.
4. Preserve job evidence on ordinary interruption. Explicit cancellation/reset must stop owned descendants before removing controls.
5. Keep external side effects outside assumed exactly-once guarantees; expose an idempotency key or a reconciliation requirement for commands that cannot safely repeat.
6. Bind job evidence to task, attempt, command and source/map generation; stale success cannot satisfy acceptance.
7. Test the launch-before-record crash window and reconcile ownership before redispatch.
8. Resume pending validation from its implementation checkpoint without invoking the model again.

## Acceptance and counterexamples

- Two start requests for the same pinned live job create only one process.
- A completed validation checkpoint resumes without redispatching the model.
- A succeeded job with changed source/map/command is rejected as stale.
- Wait timeout leaves the live job intact and returns its state, not a false failure.
- Crash/cancel tests preserve receipts or explicitly report uncertainty rather than inventing completion.
- Crash after process launch does not produce a second writer during recovery.
- A successful receipt with an outdated map/input digest is rejected.
- Validation-only resume performs zero model dispatches.
- Cleanup cannot delete state while an owned job termination remains uncertain.

## Cost, latency and quality decision

Avoid a full model retry when only validation remains; compare recovery work, repeated tests and model calls per interruption scenario.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-PERSISTENCE] LangChain, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REPLAY] LangChain, [Graph API: re-execution and idempotency](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ATOMIC] Python Software Foundation, [os.replace and filesystem interfaces](https://docs.python.org/3/library/os.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-WINDOWS-JOBS] Microsoft, [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E040], [E047], [E007], [E042]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: LangGraph durable execution idempotent tasks checkpoint replay; Python atomic replace durable state; Windows process tree job lifecycle.

## Unverified limits and refresh triggers

- Arbitrary shell commands cannot be made exactly-once merely by saving a JSON job record. External services need their own idempotency/reconciliation contract.
- Local checkpoint tests cannot establish multi-host exactly-once semantics. Remote coordination is explicitly outside the portable single-host implementation.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
