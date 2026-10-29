# 018 - Lifecycle: research revision 2

Date: 2026-10-28. Feature: `F007`. Implementation TODO `018`; independent review TODO `019`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use owned, generation-aware leases and scoped receipt validity for resume; keep cleanup local, guarded and independent of model judgment.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision adds fencing against stale runners, an explicit uncertain-execution outcome and scoped fingerprints; PID existence and whole-repository hash equality are not enough.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Trace durable state under power loss, quota pauses, stale leases and cancellation.
- Preserve product files and Plan 2 inputs while deleting only verified control artifacts.

**Baseline observations:**
- lifecyclectl uses an active pointer and runner lease to prevent duplicate execution, recover interrupted tasks and guard cleanup.
- The reusable project resource map is outside disposable plan directories. The former Plan2-input exception is no longer needed, but prepared research is still a retained project artifact.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/lifecyclectl.py` | `f4a1b9fd2cbd413d073d3f6d14de85df2fabf5e2b6c873a67d258afac7ee6d33` | lease_is_live:334 |
| `skill/plan-and-execute/scripts/lifecyclectl_concise.py` | `70dec1d0ec3973869993c505bca5906073c681ca5f24f824e376515da4f252d6` |  |
| `skill/plan-and-execute/scripts/planctl.py` | `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4` | cleanup_plan:3460 |
| `skill/plan-and-execute/references/LIFECYCLE.md` | `df87ef9b893228773a33b1490112f8ac5acbb541bf6691a9d58ba4f20b7c187b` | # Lifecycle protocol:1; ## Current/status:9; ## Activate:24; ## Resume:34 |

## Deeper analysis and competing approaches

### 1. Design analysis

PID reuse can make a dead runner look alive or make a stale controller target a different process. Lease ownership should include host, PID, process start identity and generation. A runner that loses ownership must not complete a task afterward. Remote-host uncertainty should pause with a diagnosable reason instead of killing or launching processes speculatively.

### 2. Design analysis

Crash recovery must separate a task that never started, one whose worker exited, and one whose external side effect may have occurred without a saved result. The last state is uncertain, not automatically retryable. Reconcile outputs or use operation-specific idempotency before reexecuting migrations or paid requests.

### 3. Design analysis

A valid receipt depends on the tested command, acceptance contract, environment and relevant source/dependency digests. Hashing the whole evolving repository for every task can make legitimate earlier receipts stale after unrelated work. Prefer scoped fingerprints plus a final composed integration run; retain global receipts for genuinely global validation only.

### 4. Design analysis

Cleanup removes owned control artifacts after acceptance, not source, live application logs or prepared research. Resolve roots, reject symlinks and require sentinel ownership. Preserve failed-plan evidence. Relocation should use a guarded controller operation or recreation from the specification, not hand editing status fields.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| PID-only liveness | Cheap | PID reuse and stale writers | Reject |
| Blind replay after interruption | Simple recovery | Duplicate side effects and paid calls | Reject |
| Owned lease plus reconciliation | Auditable local recovery | Explicit uncertain-state handling | Recommended |
| Distributed workflow migration | Cross-host coordination | Too large a migration for current need | Defer |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Use PID plus process-start identity and host identity when deciding whether a local lease is live. Treat uncertain remote leases conservatively.
2. Add fault-injection tests around claim, checkpoint, atomic replacement and lease release; ensure recovery never fabricates validation or completion.
3. Keep cancel/reset scoped to recognized plan roots and registered jobs. Never run an indiscriminate git clean/reset or remove product source/tests.
4. Pin successful validation receipts to the source/command/map state that produced them; reuse a receipt only if those inputs still match.
5. Preserve prepared reports outside disposable controls and retain incomplete plan state on failure. Document portable relocation rather than asking users to edit task status manually.
6. Fence task completion by lease generation and verify process-start identity before process actions.
7. Represent ambiguous post-crash effects as uncertain and require reconciliation before replay.
8. Use scoped contract/input fingerprints for task receipts and reserve whole-repository fingerprints for integration checks.

## Acceptance and counterexamples

- A reused PID does not authorize killing an unrelated process.
- Interruptions after each state-write boundary retain completed subtasks and recover only in-progress state.
- Symlinks, parent paths and directories without the plan sentinel cannot be cleaned.
- Cancelled jobs are stopped before their control directory is removed.
- Successful cleanup preserves implementation, tests, shared resource inventory and research reports.
- A reused PID cannot satisfy an old lease or be killed by a stale controller.
- A runner that lost its lease cannot publish task completion.
- An unrelated file change does not invalidate a task receipt while its actual dependency change does.

## Cost, latency and quality decision

Saved valid work avoids model redispatch. Count duplicated attempts and recovery reads; correctness takes priority when the prior execution may have produced side effects.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-ATOMIC] Python Software Foundation, [os.replace and filesystem interfaces](https://docs.python.org/3/library/os.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REPLAY] LangChain, [Graph API: re-execution and idempotency](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRY] Amazon Builders Library, [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-HARNESS] Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E056], [E047], [E007], [E040]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.docs.langchain.com durable execution idempotency; site.aws.amazon.com builders-library timeouts retries backoff jitter; site.docs.python.org os.replace.

## Unverified limits and refresh triggers

- Power loss, network filesystems and Windows locks require actual platform tests; POSIX mocks are not proof of those guarantees.
- Cross-host filesystems, power-loss durability and platform process behavior require dedicated integration tests; a local lease design does not prove distributed exactly-once execution.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
