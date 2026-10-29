# 042 - Muse: research revision 2

Date: 2026-10-28. Feature: `F019`. Implementation TODO `042`; independent review TODO `043`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use Muse explicit headless session/event contracts, enforce checkout isolation for parallel writers and reconcile cooperative cancellation before replacement workers.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The current Muse docs support per-child worktree isolation but explicitly describe cooperative cancellation. The revision adds cancellation-acknowledgement and base-revision evidence instead of assuming child termination.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Resolve the exact Meta Muse Code product, exec JSON envelope and session protocol.
- Verify cancellation, summary mode and resumable state without assuming flags from unrelated Muse CLIs.

**Baseline observations:**
- The repository has a dedicated Muse adapter and tests, rather than a generic command named Muse. The worker uses headless execution with configured model/effort options.
- Meta documentation provides session-log controls and notes that child execution does not itself create an isolated checkout.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | build_worker_command:1034; build_summary_command:2319 |
| `skill/plan-and-execute/scripts/muse_provider_self_test.py` | `9466b0aaa0bed367dd57339f5c991ccd0c2123b19f51140d6ece98549b50487a` | sample_report:25; worker:42; summary:46; test_default_worker_argv_has_no_permission_flags:50 |
| `skill/plan-and-execute/references/MODEL_ROUTING_MUSE.md` | `648cec38d3ee0e61007208c01122e6095188e7b568ee82faa21aa1cf6a33804b` | # Muse Code model routing:1; ## Status and evidence:5; ## Catalog mapping:9; ## Worker argv:21 |

## Deeper analysis and competing approaches

### 1. Design analysis

Default subagents can share the lead checkout. Parallel write scopes need explicit isolation or serialization, and an isolation request that cannot be honored must not fall back silently. Pin source revision and pass only relevant changes; checkout separation alone does not prevent incompatible edits to the same contract.

### 2. Design analysis

A cancel request is not proof that the child stopped. A worker may finish a write before reaching a cancellation checkpoint. Require terminal status and process/lease reconciliation before starting a replacement writer or deleting its workspace. Uncertain cancellation preserves the plan and evidence.

### 3. Design analysis

Headless sessions and interactive resume commands are separate surfaces. Use documented headless exec with an exact session id for any permitted resume, not the interactive UI. The versioned schema/session protocol can be an optional adapter boundary, but a stable schema version still needs event, usage and terminal-outcome fixtures.

### 4. Design analysis

Muse session logs and child journals can contain the full execution context. Keep them outside normal worker prompts and outside release artifacts. Retain only non-secret identity and bounded evidence references in the shared ledger, with an explicit policy for provider-created logs beyond the plan directory.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Shared checkout for all children | Cheap startup | Write races and cancellation ambiguity | Read-only children only |
| Isolated writers with terminal reconciliation | Safe ownership and recovery | Merge and lifecycle overhead | Recommended |
| Assume cancellation is immediate | Fast replacement | Two writers can overlap | Reject |
| Replace runner with session protocol | Rich state | Provider-specific integration work | Optional after equivalence tests |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Add version/help fixtures for Meta Muse Code and reject a same-named unrelated executable without the required command contract.
2. Separate JSONL progress/tool events from the final completion payload. Apply the shared bounded spool and schema validation.
3. Choose and document session-log retention for normal fresh workers; only add --no-session-log when supported and covered by a golden test.
4. Require explicit worktree/read-only controls for isolation. Never fall back from unsupported confinement to trust-workspace or approval bypass silently.
5. Normalize backend/usage identity and map failures through the same availability-versus-semantic distinction as other providers.
6. Require explicit isolation or serialization for Muse writers and verify the pinned source revision.
7. Wait for terminal cancellation evidence before replacement or cleanup; uncertain state remains recoverable.
8. Use exact headless session ids and versioned event schemas, never interactive resume in unattended execution.

## Acceptance and counterexamples

- A fixture for an unrelated muse executable is rejected before any task starts.
- No-session-log and resume options are not combined incompatibly.
- Two children sharing a checkout cannot be mistaken for isolated parallel writers.
- Read-only summary and implementation command paths have different tested authority.
- Large or malformed JSONL cannot cause unbounded memory or false completion.
- A rejected isolation request cannot run in the shared checkout.
- A cancelled child still writing blocks replacement until terminal reconciliation.
- Interactive muse resume is not selected for a headless recovery.
- An unrelated child log cannot be imported as task evidence.

## Cost, latency and quality decision

Use native parallelism only where independent validated outcomes offset setup and merge cost; avoid repeated full-journal ingestion.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-MUSE] Meta, [Extending and automating Muse Code](https://dev.meta.ai/docs/muse-code/extending). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-MUSE-SESSIONS] Meta, [Audit and resume agent sessions](https://dev.meta.ai/docs/cookbook/audit-agent-sessions). Accessed 2026-10-28. Reading scope: Official cookbook excerpts on session logs, audit and resume inspected. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REPLAY] LangChain, [Graph API: re-execution and idempotency](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E033], [E034], [E044]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Meta Muse Code headless exec session protocol subagent isolation; Meta Muse audit resume session logs; durable execution idempotent replay.

## Unverified limits and refresh triggers

- Live Meta account permissions, model list, usage accounting and actual read-only enforcement remain unverified.
- No Muse executable or session protocol was exercised. Cooperative cancellation behavior is documented, but actual timing and host capabilities need integration tests.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
