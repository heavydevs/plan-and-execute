# 014 - Context Learning: research revision 2

Date: 2026-10-28. Feature: `F005`. Implementation TODO `014`; independent review TODO `015`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use provenance-bearing task context and directional learnings with explicit trust and cache boundaries, not an accumulating transcript or universal memory.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision prevents unvalidated hypotheses from becoming shared rules and separates context relevance from provider-specific cache economics. Historical long-context weakness is no longer assumed universal.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Compare global versus scoped context and validated directional learnings.
- Measure repeated prefixes, assigned-read enforcement and anchoring from prior errors.

**Baseline observations:**
- The current context system separates universal context, task-scoped context and directional learnings. The production worker prompt is built by runner_contract.
- Useful worktree changes and completed subtasks survive a worker; transcripts are not the intended cross-task memory.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/planctl.py` | `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4` | render_task:1784 |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `477646cf30634e334e5c704a6cbe86e9dea4712f7527f51501c43462cadc08f3` | _error:100; concise_line:104; concise_list:132; _md:165 |
| `skill/plan-and-execute/scripts/runner_contract.py` | `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6` | worker_prompt:44 |
| `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` | `4ed0e09d146e6a228943f9607de92a3156e19ca5c5e19b77bdd78ffa5de82447` | # Execution context and validated learning:1; ## Omission is the default:5; ## Global `CONTEXT.md`:18; ## Scoped context files:36 |
| `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` | `72da10bd5e05fd08d213ed29ca649e83fbe23d4f082bf1c3159e87402cbef8cd` | # Token-efficiency contract:1; ## Objective:5; ## 1. Avoid the harness when the harness does not pay for itself:9; ## 2. Keep useful shared context while it is useful:15 |

## Deeper analysis and competing approaches

### 1. Design analysis

Keep three classes distinct: mandatory cross-task contracts, scoped facts with provenance, and hypotheses from failed attempts. Only validated facts can become directional learnings. Hypotheses are optional next-attempt data and must not be upgraded into normative instructions by repeated summarization.

### 2. Design analysis

A useful learning entry needs a producing task, evidence reference, applicable consumers and an invalidation trigger. When the underlying file or contract changes, consumers should recheck the narrow fact. Do not copy every discovered implementation detail to a global CONTEXT.md merely because it might someday help.

### 3. Design analysis

Keep prompt rules stable and append task-specific context after them, but do not infer guaranteed cache savings from byte equality alone. Model, effort, tools, host, retention and cache-write rules can affect the result. Native CLI caching may not expose all API controls, so measure usage rather than changing flags speculatively.

### 4. Design analysis

Compare assigned-context retrieval with full-history replay and semantic memory on held-out tasks. Evaluate incorrect reuse and omitted dependencies alongside token count. A smaller prompt that silently loses a business invariant is not an optimization.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Full transcript replay | Maximum historical detail | Repeated cost, stale instructions and secrets | Reject as default |
| One global summary | Cheap to read | Scope leakage and anchoring | Use only universal constraints |
| Scoped provenance records | Selective and auditable | Requires invalidation ownership | Recommended |
| Vector memory for all learnings | Flexible discovery | Approximate recall and index overhead | Defer unless retrieval measurements justify it |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Attach a provenance hash, producing task, applicable consumers and expiry/invalidation rule to each reusable learning.
2. Load only universal constraints and the receiving task's assigned entries. Repeated conventions used by multiple tasks belong in a versioned pattern, not copied learning prose.
3. Require deterministic evidence before promoting a failed worker's hypothesis into a reusable fact. Keep disproven hypotheses clearly labeled and bounded.
4. Add a compact context accounting receipt: selected file IDs, byte counts and reason for inclusion, without retaining prompts or secrets.
5. Keep static prompt rules stable across tasks; append task-specific evidence afterward. Test cache structure but measure actual cache usage per host rather than assuming an exact hit.
6. Assign each learning a trust class, producer, consumer set and source/contract digest.
7. Keep failed-attempt hypotheses separate from normative shared facts; invalidate them when their evidence changes.
8. Measure stale-learning errors and task success as well as context bytes; cache reuse is an observed metric, not a structural assertion.

## Acceptance and counterexamples

- An unrelated task cannot receive a learning merely because it ran later.
- Changing a cited file invalidates or flags the learning before reuse.
- A malicious or unsupported note cannot alter acceptance, permissions or provider policy.
- The universal context contains only constraints needed by all tasks and remains within its existing budget.
- Byte-stable prefixes and bounded task suffixes survive different task IDs and prior failure lengths.
- A disproven hypothesis never appears as a validated shared fact.
- A source-contract change invalidates its learning without deleting unrelated knowledge.
- The static prefix remains stable while task-specific reports are loaded only for their assigned consumers.

## Cost, latency and quality decision

Compare retained tokens and retrieval work against error-induced rework. The cheapest valid memory is often a checked path/symbol reference; semantic storage is justified only by demonstrated repeated retrieval benefit.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-CONTEXT] Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LITM] Liu et al. / TACL and arXiv, [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172). Accessed 2026-10-28. Reading scope: Paper abstract and publication metadata inspected; no reproduction and no claim to have read every experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRIEVAL] Google Research / Max McKinnon, [Retrieval Quality at Context Limit](https://research.google/pubs/retrieval-quality-at-context-limit/). Accessed 2026-10-28. Reading scope: Official publication abstract inspected; the result concerns simple factoid retrieval, not multi-file implementation correctness. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-PERSISTENCE] LangChain, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E003], [E011], [E010], [E021]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.anthropic.com effective context engineering agents; site.research.google retrieval quality at context limit; site.docs.langchain.com persistence checkpointer store.

## Unverified limits and refresh triggers

- Research on memory/context reports workload-specific gains, not proof for this repository. Independent implementation review remains necessary.
- Actual cache behavior and long-context reliability vary by host/model. No universal percentage savings or model-independent context ceiling is claimed.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
