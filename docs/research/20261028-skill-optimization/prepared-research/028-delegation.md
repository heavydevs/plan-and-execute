# 028 - Delegation: research revision 2

Date: 2026-10-28. Feature: `F012`. Implementation TODO `028`; independent review TODO `029`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use a measured delegation gate with explicit input revision and isolation boundaries; prefer one qualified context for sequential work and bounded fresh workers for independently useful tasks.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision adds the empirically important single-agent/lower-effort comparator and worktree base-revision checks. It does not assume that a fresh context or a subagent is automatically cheaper.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Compare isolation benefits with coordination, cache writes and repeated repository exploration.
- Keep root route fixed; separate native session resume from cross-provider handoff.

**Baseline observations:**
- run_concise composes multiple runtime contracts, so tests of run_isolated alone do not cover the production prompt.
- The current runner launches fresh workers and receives bounded task artifacts. Its run_process/pump_stream path accumulates captured output; large outputs require a bounded capture contract independent of the full disk log.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_concise.py` | `495d986c1582ce5ed432fe304d995d244159e2168d2b4aafa6185b13ed79aba8` |  |
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | worker_prompt:711; pump_stream:1193; run_process:1214 |
| `skill/plan-and-execute/scripts/runner_contract.py` | `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6` | install_runner_contract:36; worker_prompt:44 |
| `skill/plan-and-execute/references/DELEGATION.md` | `40cd1984a718285408ab63a0fe97242d0c2eef675a90df3f9ef1b0109d28bb99` | # Delegation policy and role contracts:1; ## Request:11; ## Rules, in order:15; ## Token accounting:24 |

## Deeper analysis and competing approaches

### 1. Design analysis

Delegation has startup, context reconstruction, review and merge costs. A cheap worker may take more turns, omit constraints or induce repair work in the root agent. Evaluate the complete validated result, not the worker invoice in isolation. The new vendor experiment is evidence of a tradeoff, not proof of a universal delegation strategy.

### 2. Design analysis

Use read-only exploration workers only for independent search questions with bounded result contracts. Serialize writes to shared files or use real worktree isolation and merge validation. Pin the starting commit and include relevant uncommitted changes explicitly; a child created from a default branch can otherwise analyze an obsolete codebase while appearing isolated and correct.

### 3. Design analysis

Conversation forking and filesystem isolation are separate controls. A fork may reuse a large prompt cache but also inherits irrelevant or misleading reasoning. A fresh worker receives less context but may redo repository discovery. Preserve both as evaluated options where the host supports them; retain portable fresh-process execution as the reference behavior.

### 4. Design analysis

Do not accumulate an entire worker stream in RAM merely to retain the final report. Drain stdout and stderr concurrently, write raw output to bounded/rotated owned artifacts, retain a bounded diagnostic tail and parse structured completion separately. This deterministic optimization is independent of choosing an external agent framework.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| One qualified agent throughout | Reuse coherent context | Context can grow across unrelated domains | Preferred for sequential cohesive work |
| Fresh worker for every microstep | Strong separation | Coordination and reread overhead | Reject |
| Bounded selective delegation | Useful isolation and concurrency | Requires strict contracts and base pinning | Recommended |
| Native fork/workflow replaces all workers | Potential cache reuse | Host-specific semantics and stale checkout risk | Opt-in adapter after equivalence tests |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Add deterministic delegation receipts recording role, read/write scope, capability floor, estimated coordination cost and reason for keeping work at root.
2. Use fresh workers for independent contexts or capability gaps. Keep small cohesive work local and prevent concurrent writers with overlapping scopes unless an explicit integration strategy exists.
3. Implement a bounded stream spool that drains stdout and stderr concurrently, preserves full owned logs on disk, and retains only the final structured envelope and bounded diagnostic windows in memory.
4. Keep worker prompt static prefixes stable in both raw and composed entrypoints. Use referenced artifacts rather than historical chat messages for cross-provider continuity.
5. Treat same-provider session resume as an opt-in future experiment with retention and cache accounting, not a hidden fallback that changes fresh-context semantics.
6. Compare delegation with a single qualified model at lower effort on held-out tasks, including review and repair cost.
7. Pin worker base revision and uncommitted-input policy; verify isolated worktree starts from the intended source.
8. Bound in-memory output while preserving independently parsed final reports and owned diagnostic logs.

## Acceptance and counterexamples

- A noisy fake CLI emits many megabytes without proportional memory growth or pipe deadlock.
- A final structured report remains recoverable after long tool output; missing or truncated envelopes fail visibly.
- Two delegated writers cannot silently claim the same source scope.
- Above-floor work cannot be retained on an underqualified worker merely to avoid coordination cost.
- Prefix hashes match across tasks for raw and production entrypoints.
- A worker based on the default branch rather than the pinned working revision is rejected.
- Concurrent writers never share an overlapping scope without serialization.
- Multi-megabyte output does not grow the diagnostic buffer without bound.
- Native fork support cannot silently claim fresh-context isolation.

## Cost, latency and quality decision

C_total=C_root+C_workers+C_review+C_merge+C_repairs; compare latency and non-inferior validated quality. Cache affinity is an observed benefit, not a reason to include unnecessary history.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CLAUDE-SUBAGENTS] Anthropic, [Create custom subagents](https://code.claude.com/docs/en/sub-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-MUSE] Meta, [Extending and automating Muse Code](https://dev.meta.ai/docs/muse-code/extending). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SUBPROCESS] Python Software Foundation, [Subprocess management](https://docs.python.org/3/library/subprocess.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CONTEXT] Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E016], [E054], [E021], [E018], [E041]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Anthropic cost intelligence subagents experiments October 2026; Claude subagents worktree default branch context fork; Muse Code subagent worktree isolation; Python subprocess communicate memory buffering.

## Unverified limits and refresh triggers

- No native subagent dispatch exists in this environment; this report does not claim an independent worker or measured cache hit.
- Vendor delegation results concern a specific harness and task set. No new authenticated model or native worktree experiment was performed here.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
