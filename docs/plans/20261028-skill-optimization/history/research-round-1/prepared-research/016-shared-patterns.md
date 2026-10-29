# F006 / task 016 - Versioned shared contracts and selective invalidation

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Strengthen versioned shared patterns with compare-and-swap updates and selective consumer invalidation, without building a global context dump.

## Questions addressed

- Check signatory adoption, contract revision races and invalidation of completed tasks.
- Bound registry loading and evidence required to reopen a consumer.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- patternctl already represents explicit signatories and pattern revisions; pattern_runner_contract integrates them into execution.
- Shared normative patterns and runtime learnings are different contracts. Reopening every completed task would erase the selectivity the existing mechanism is intended to provide.

### Read targets and integrity

- `skill/plan-and-execute/scripts/patternctl.py` (SHA-256 `d25665ba2ebe2a3464e0d3f83c8fe26bf683101af2a9c1cb1c347487b91fd62d`): `PatternError` L23-24; `now_utc` L27-28; `read_json` L31-35; `write_json` L38-40
- `skill/plan-and-execute/scripts/pattern_runner_contract.py` (SHA-256 `c96b6c1696d57fd7d096ce06f58c78e168854783e6990c6cc5b0bc322b46a1c8`): `install_pattern_runner_contract` L12-165
- `skill/plan-and-execute/references/SHARED_PATTERNS.md` (SHA-256 `d9f785d9acf44b667d6cc3301e2e1520a15a1b7af5460535d00e3c6676f1382f`): `# Versioned shared-pattern contracts` L1; `## 1. Promote only real cross-cutting contracts` L13; `## 2. Pattern artifacts` L24; `## 3. Plan-time creation` L53

## External basis

- [E056] [os.replace and operating-system interfaces](https://docs.python.org/3/library/os.html#os.replace) - Python Software Foundation; accessed 2026-10-28.
- [E047] [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) - LangChain; accessed 2026-10-28.
- [E011] [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/abs/2510.04618) - Zhang et al. / arXiv; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Last writer wins and broad reopening | Simple, but races and excessive rework undermine durable progress. |
| recommended | Revision-aware updates and selective invalidation | Small deterministic bookkeeping with bounded revalidation. |
| rejected | Duplicate the same contract in every task | Copies drift and increase tokens while obscuring the authoritative version. |

## Implementation instructions

1. Require the updater to provide the observed revision/digest and reject a stale writer rather than silently overwriting a newer contract.
2. Bind each consumer acceptance to the exact pattern revision. A revision change reopens only completed signatories that used an older revision; pending consumers just read the new revision.
3. Record a concise change rationale and migration impact. Avoid copying whole prior pattern histories into worker prompts.
4. Serialize writes for shared pattern files or use a tested lock/atomic write seam. Do not claim atomicity across independent files without recovery tests.
5. Limit registry lookup to assigned pattern IDs and make adoption evidence part of deterministic validation.

## Acceptance tests to implement and run

- [ ] Two writers using the same starting revision cannot both silently succeed.
- [ ] An unaffected completed task remains completed after an unrelated pattern change.
- [ ] A stale completed signatory is reopened exactly once with a reason.
- [ ] Malformed or escaping pattern paths cannot be read or deleted.
- [ ] A worker receives only assigned current contracts, not the entire registry/history.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Compare number of invalidated tasks, bytes loaded and repeated validations. Preserve the current simple file-backed design unless measured contention justifies another store.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Cross-host concurrent execution requires an explicit storage/locking contract; local filesystem tests cannot establish distributed locking.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **016** now implements this recommendation; task **017** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
