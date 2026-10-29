# F002 / task 008 - Oversized request fragmentation and prepared packages

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep deterministic immutable fragments, add integrity and coverage verification, and use bounded semantic batches only when preparation is justified.

## Questions addressed

- Trace source hashes, fragment coverage, digest loss and cross-fragment contradictions.
- Compare deterministic grouping with bounded fan-out; measure re-read tokens and resume loss.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- preplanctl.assess_source uses estimated working-set size plus breadth/dependency signals rather than raw file count.
- validate_package checks that fragment files exist, then checks digest/coverage state; the inspected implementation does not recompute every fragment content hash at that final gate.
- docx_blocks reads direct body paragraphs. A specification inside table cells is therefore a coverage risk that needs a fixture, not a claim that every Office input is already lossless.

### Read targets and integrity

- `skill/plan-and-execute/scripts/preplanctl.py` (SHA-256 `71daeaf4fbdaa22120e45e9742cb267e537f618223ac047fca8c4ca55ecdeeb0`): `docx_blocks` L92-115; `assess_source` L174-218; `validate_digest` L634-655; `validate_package` L704-721
- `skill/plan-and-execute/references/PRIMARY_PLANNING.md` (SHA-256 `246075b5098308f8e14b6c6004a4c37e1e9650bb6c96606e5c75b941a17c38c3`): `# Primary planning for oversized requests` L1; `## 1. Why this path exists` L9; `## 2. Route by working-set pressure, not maximum context size` L28; `## 3. Split deterministically before asking a model to summarize` L45
- `skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md` (SHA-256 `9407add1e9062e3bdfb65af9c391e0f232b9512c3dfec0fa5f7dbbc9269fc683`): `# Planning input contract` L1; `## Accepted final-planning inputs` L7; `## Prepared package layout` L16; `## Consumption rules` L45

## External basis

- [E006] [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172) - Liu et al. / arXiv; accessed 2026-10-28.
- [E003] [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) - Anthropic; accessed 2026-10-28.
- [E007] [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) - Anthropic; accessed 2026-10-28.
- [E008] [Agents, adapted from AI Engineering](https://huyenchip.com/2025/01/07/agents.html) - Chip Huyen; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Existence and declared coverage checks | Cheap but insufficient evidence that immutable inputs are unchanged. |
| recommended | Hash-pinned fragments with selective retrieval | Small deterministic I/O cost; retains provenance and bounded worker prompts. |
| rejected | Feed the whole source to every worker or summarize summaries without originals | Higher token cost and no reliable recovery of omitted constraints. |

## Implementation instructions

1. Recompute source/fragment hashes before accepting a prepared package and before final planning consumes it. Reject missing, changed, duplicate or escaping fragment references.
2. Add extraction coverage for table cells and document ordering, either in host extraction or a documented deterministic OOXML walker. Preserve headings, stable source anchors and explicit unsupported-content warnings.
3. Keep digest facts traceable to fragment IDs; record contradictions without resolving them in cheap extraction workers. Audit unique source obligations, not just the existence of a digest file.
4. Batch by semantic section within bounded token limits. For a large repetitive source deduplicate only the routing estimate, never the authoritative fragments.
5. Retain thresholds as tunable operational estimates. Measure digest omission and repeated reads before changing defaults or introducing fan-out.

## Acceptance tests to implement and run

- [ ] Mutating one byte of a fragment after coverage approval invalidates the package.
- [ ] A DOCX fixture with requirements in paragraphs and table cells preserves all obligations in source order.
- [ ] Duplicates, missing IDs, contradictory clauses and symlinks are rejected or explicitly recorded.
- [ ] An interrupted batch resumes from validated digests without processing completed raw fragments again.
- [ ] Permuting a requirement between beginning, middle and end does not change final requirement coverage.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Hashing is linear deterministic work, preferable to repeating expensive source reads. Report estimated source/digest sizes separately from billed tokens; fan-out is optional and must not weaken coverage.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Image-only or embedded-object requirements still require an explicit extraction path. No live model comparison of digest quality was performed.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **008** now implements this recommendation; task **009** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
