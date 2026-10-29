# 012 - Plan Contract: research revision 2

Date: 2026-10-28. Feature: `F004`. Implementation TODO `012`; independent review TODO `013`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use staged plan generations, a single authoritative manifest and recoverable projection rebuilds; avoid claiming a multi-file transaction from atomic rename alone.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The report now specifies the commit boundary for plan revisions, recovery after partial projection writes, and generation-aware evidence instead of a generic transactional-replanning promise.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Trace request-part to requirement to task coverage and concise live projections.
- Evaluate bounded subtasks, high-task splitting, review gates and legacy schema compatibility.

**Baseline observations:**
- planctl creates schema-v4 plans, validates requirement coverage and dependencies, and renders per-task files. artifact_contract supplies the concise projections used in production.
- The existing plan has 86 tasks and an initial independent-review prerequisite inherited by the whole graph. The current user instruction removes research execution and the second-plan deliverable, so those assumptions must be revised explicitly.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/planctl.py` | `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4` | render_task:1784; render_todo:1935; save_manifest:1981; create_plan:2011 |
| `skill/plan-and-execute/scripts/artifact_contract.py` | `477646cf30634e334e5c704a6cbe86e9dea4712f7527f51501c43462cadc08f3` | install_plan_contract:672 |
| `skill/plan-and-execute/scripts/planctl_concise.py` | `650baa02ebcb555acc9fe5874e5c94b4090720bc63f963c76b73f332dd3082e9` |  |
| `skill/plan-and-execute/references/PLAN_SPEC.md` | `6b1014618196c4e0f966751190eb5bb3104798da7ff10694f9944f27b99fc92d` | # Plan spec contract — schema v4:1; ## Top level:5; ## `request_analysis`:25; ## `requirements`:63 |
| `skill/plan-and-execute/references/PLANNING_PROTOCOL.md` | `2c12e549fa7032ef1691ea8c87b805beab4732c6fb976164ed295faf0b266508` | # Final planning protocol:1; ## 1. Preserve meaning, compress representation:5; ## 2. Route planning work explicitly:21; ## 3. Requirements:31 |

## Deeper analysis and competing approaches

### 1. Design analysis

The current manifest is the authority, while TODO.md and task Markdown files are projections. Replanning should normalize the entire specification, validate graph and coverage in a staging generation, and only then publish the new authority. If a projection is missing after a crash, it must be recreated from that generation rather than treated as a different truth.

### 2. Design analysis

A single os.replace does not atomically update manifest, tasks, study, context and active pointer together. The lowest-complexity fix is one writer lock plus a generation identifier and recovery rules. A database is a valid alternative for future multi-writer requirements, but unnecessary for this single-runner repository today.

### 3. Design analysis

Task identity and evidence validity must be separate. Keep stable IDs for the users references, but change a contract digest when acceptance, command, input or dependency changes. Reopen only outputs affected by changed contracts and preserve previous receipts as historical evidence. A code change later in an unrelated task should not automatically erase every earlier task.

### 4. Design analysis

Validate requests, requirements, task graph, source report hashes and generated projections together. Duplicate JSON keys, non-finite numbers and cycles need negative tests. Legacy plan schemas remain readable; stricter new metadata is versioned instead of retroactively invalidating old state without migration.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Edit Markdown task files directly | Immediate | Manifest/projection split-brain | Reject |
| Atomic rename for each file only | Small patch | Partial generations after crash | Insufficient alone |
| Single writer plus staged generation | Bounded implementation and recovery | Requires generation/recovery tests | Recommended |
| SQLite or workflow server migration | Transactions and richer concurrency | Migration and operational burden | Defer until actual multi-writer demand |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Define a plan-revision record containing previous spec hash, amendment, task-ID mapping and changed acceptance/dependencies. Keep completed evidence immutable and invalidate only outputs whose contract changed.
2. Generate manifest, TODO and task files from one normalized specification in a staging directory; audit the staged graph before activation. Do not hand-edit a task projection to disagree with its manifest.
3. Preserve requirement IDs and attach supersession notes for the two-plan clauses. Separate research-prepared metadata from implementation status.
4. Reject cycles, missing requirements, orphan reviews and inconsistent subtask IDs. Use bounded outcome-oriented subtasks, not one TODO per arbitrary file.
5. Replace the initial global model gate with deterministic preflight and put independent review after each implementation. Missing review capability blocks acceptance, not report preparation.
6. Publish plan revisions as validated generations and define recovery when projections lag the authoritative manifest.
7. Bind acceptance to task contract and scoped inputs; preserve old receipts as history rather than rewriting them as current.
8. Test interruption before and after authority publication; recovery must not mark tasks complete or combine generations.

## Acceptance and counterexamples

- A failed revision leaves the previous manifest and task projections readable.
- Every requirement has a consumer; every implementation has explicit acceptance and validation.
- A transformed research task remains pending, with subtasks instructing implementation from its assigned report.
- Legacy schema1-3 files are not silently rewritten using schema4 projection rules.
- No active task creates a second plan or depends on a nonexistent research output.
- A crash after manifest replacement but before task rendering rebuilds consistent projections.
- A stale plan writer cannot replace a newer generation.
- Changing one task contract invalidates its dependent outputs, not unrelated completed tasks.

## Cost, latency and quality decision

The file-backed design avoids a service dependency and model calls for state management. Measure bytes read and rebuild duration against the existing renderer; do not optimize consistency away for small I/O savings.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-ATOMIC] Python Software Foundation, [os.replace and filesystem interfaces](https://docs.python.org/3/library/os.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-REPLAY] LangChain, [Graph API: re-execution and idempotency](https://docs.langchain.com/oss/python/langgraph/graph-api). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-HARNESS] Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CAS] Kubernetes, [Kubernetes API Concepts: updates](https://kubernetes.io/docs/reference/using-api/api-concepts/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E057], [E056], [E047], [E058]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.docs.langchain.com oss python langgraph durable execution idempotent tasks; site.docs.python.org os.replace atomic rename; site.kubernetes.io API resourceVersion conflict.

## Unverified limits and refresh triggers

- Multi-file durability needs fault-injection tests; os.replace alone is not a complete transaction or power-loss guarantee.
- The generation protocol is a design recommendation to implement, not an existing proven crash-consistency guarantee.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
