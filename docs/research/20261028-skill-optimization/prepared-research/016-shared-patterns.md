# 016 - Shared Patterns: research revision 2

Date: 2026-10-28. Feature: `F006`. Implementation TODO `016`; independent review TODO `017`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep a small versioned pattern registry with conditional writes and precise consumer invalidation; distinguish semantic changes from formatting edits.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision adds semantic-change classification, a single-writer boundary and a bounded pattern delta, avoiding unnecessary reopen cascades from formatting-only changes.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Check signatory adoption, contract revision races and invalidation of completed tasks.
- Bound registry loading and evidence required to reopen a consumer.

**Baseline observations:**
- patternctl already represents explicit signatories and pattern revisions; pattern_runner_contract integrates them into execution.
- Shared normative patterns and runtime learnings are different contracts. Reopening every completed task would erase the selectivity the existing mechanism is intended to provide.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/patternctl.py` | `d25665ba2ebe2a3464e0d3f83c8fe26bf683101af2a9c1cb1c347487b91fd62d` | PatternError:23; now_utc:27; read_json:31; write_json:38 |
| `skill/plan-and-execute/scripts/pattern_runner_contract.py` | `c96b6c1696d57fd7d096ce06f58c78e168854783e6990c6cc5b0bc322b46a1c8` | install_pattern_runner_contract:12 |
| `skill/plan-and-execute/references/SHARED_PATTERNS.md` | `d9f785d9acf44b667d6cc3301e2e1520a15a1b7af5460535d00e3c6676f1382f` | # Versioned shared-pattern contracts:1; ## 1. Promote only real cross-cutting contracts:13; ## 2. Pattern artifacts:24; ## 3. Plan-time creation:53 |

## Deeper analysis and competing approaches

### 1. Design analysis

Patterns are contracts, not a shared scratchpad. The expected digest/revision must accompany an update so a stale worker cannot silently overwrite another decision. Write under the same ownership/lock discipline as lifecycle state; a second ad-hoc locking convention would create deadlocks and incompatible recovery.

### 2. Design analysis

A semantic contract change reopens accepted signatories on an older revision. A formatting edit that leaves the canonical contract unchanged should not trigger code reimplementation. Preserve a canonical representation or explicitly classify the revision and test that classification; do not let an unverified model claim decide it alone.

### 3. Design analysis

Pending consumers read the current contract. Completed consumers retain the exact adopted revision and evidence. Bound the change note to the normative delta, affected consumers and migration test. Sending the complete history to every worker defeats selective loading.

### 4. Design analysis

The Kubernetes source supplies an optimistic concurrency example, not a mandate to run a cluster. A plain local registry with hashes, lock and generation-aware writes is the least disruptive implementation. Use formal schema or interface tests where possible to decide whether a consumer is actually stale.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Copy rules into every task | No registry | Drift and repeated tokens | Reject for evolving contracts |
| Global pattern history in every prompt | Easy visibility | Unbounded context and false invalidation | Reject |
| CAS-style revision and signatories | Minimal selective invalidation | Requires conflict/recovery tests | Recommended |
| Distributed schema registry | Strong external governance | Unneeded service and migration cost | Defer |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Require the updater to provide the observed revision/digest and reject a stale writer rather than silently overwriting a newer contract.
2. Bind each consumer acceptance to the exact pattern revision. A revision change reopens only completed signatories that used an older revision; pending consumers just read the new revision.
3. Record a concise change rationale and migration impact. Avoid copying whole prior pattern histories into worker prompts.
4. Serialize writes for shared pattern files or use a tested lock/atomic write seam. Do not claim atomicity across independent files without recovery tests.
5. Limit registry lookup to assigned pattern IDs and make adoption evidence part of deterministic validation.
6. Require an expected canonical digest and serialize writes using the lifecycle ownership contract.
7. Separate formatting-only changes from semantic revisions; only changed normative contracts reopen stale accepted signatories.
8. Deliver the current pattern and bounded delta, not its full revision history, to each assigned consumer.

## Acceptance and counterexamples

- Two writers using the same starting revision cannot both silently succeed.
- An unaffected completed task remains completed after an unrelated pattern change.
- A stale completed signatory is reopened exactly once with a reason.
- Malformed or escaping pattern paths cannot be read or deleted.
- A worker receives only assigned current contracts, not the entire registry/history.
- Two writers with the same starting digest cannot both overwrite the registry.
- A formatting-only change does not reopen completed consumers.
- A semantic revision reopens exactly its stale signatories and preserves their prior evidence as history.

## Cost, latency and quality decision

Measure number of reopened tasks and repeated context bytes per real contract change. Selective invalidation saves only when the consumer mapping is accurate; missing signatories is a correctness defect.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-CAS] Kubernetes, [Kubernetes API Concepts: updates](https://kubernetes.io/docs/reference/using-api/api-concepts/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ATOMIC] Python Software Foundation, [os.replace and filesystem interfaces](https://docs.python.org/3/library/os.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-PERSISTENCE] LangChain, [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E056], [E047], [E011]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.kubernetes.io API resourceVersion conflict; site.docs.python.org os.replace atomic rename; site.docs.langchain.com checkpointer store persistence.

## Unverified limits and refresh triggers

- Cross-host concurrent execution requires an explicit storage/locking contract; local filesystem tests cannot establish distributed locking.
- Hash equality proves canonical bytes, not semantic equivalence unless the canonical contract format is defined and tested.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
