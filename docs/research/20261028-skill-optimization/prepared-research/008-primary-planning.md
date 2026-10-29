# 008 - Primary Planning: research revision 2

Date: 2026-10-28. Feature: `F002`. Implementation TODO `008`; independent review TODO `009`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use content-addressed, lossless source fragments and obligation coverage; retain deterministic extraction and calibrate staging on working-set pressure.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The original hash and table recommendations are retained, but the revision adds nested-table/merged-cell handling, extraction limits, consumption-time integrity, and evidence against a universal long-context failure assumption.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Trace source hashes, fragment coverage, digest loss and cross-fragment contradictions.
- Compare deterministic grouping with bounded fan-out; measure re-read tokens and resume loss.

**Baseline observations:**
- preplanctl.assess_source uses estimated working-set size plus breadth/dependency signals rather than raw file count.
- validate_package checks that fragment files exist, then checks digest/coverage state; the inspected implementation does not recompute every fragment content hash at that final gate.
- docx_blocks reads direct body paragraphs. A specification inside table cells is therefore a coverage risk that needs a fixture, not a claim that every Office input is already lossless.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/preplanctl.py` | `71daeaf4fbdaa22120e45e9742cb267e537f618223ac047fca8c4ca55ecdeeb0` | docx_blocks:92; assess_source:174; validate_digest:634; validate_package:704 |
| `skill/plan-and-execute/references/PRIMARY_PLANNING.md` | `246075b5098308f8e14b6c6004a4c37e1e9650bb6c96606e5c75b941a17c38c3` | # Primary planning for oversized requests:1; ## 1. Why this path exists:9; ## 2. Route by working-set pressure, not maximum context size:28; ## 3. Split deterministically before asking a model to summarize:45 |
| `skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md` | `9407add1e9062e3bdfb65af9c391e0f232b9512c3dfec0fa5f7dbbc9269fc683` | # Planning input contract:1; ## Accepted final-planning inputs:7; ## Prepared package layout:16; ## Consumption rules:45 |

## Deeper analysis and competing approaches

### 1. Design analysis

Do not replace a long specification with a summary before preserving authoritative text. The source index should bind raw bytes, extraction version, ordered blocks and fragment hashes. Deduplicating repeated text can inform routing economics, but may erase repeated obligations when used on the authoritative representation.

### 2. Design analysis

An ordered OOXML walker is less disruptive than adding a general document-processing stack if the existing extractor only needs paragraphs and tables. It must traverse nested cells, avoid emitting a merged cell multiple times and surface tracked changes, text boxes or unsupported structures as explicit coverage limitations. ZIP/XML input limits prevent the extractor from becoming a resource-exhaustion entrypoint.

### 3. Design analysis

A fragment file existing is not enough. Validate its digest at handoff and at consumption; checking only modification time misses same-size rewrites. For large sources, stream the hash and reuse it only within a verified immutable generation. Coverage must relate each source obligation to a digest and then to an implementation requirement, not count files.

### 4. Design analysis

Older long-context studies and newer position-robust simple retrieval findings do not justify one universal token threshold. Keep the current thresholds as operational defaults and measure omission, contradiction handling and repeated reading on this workload. Long-context one-shot planning remains a valid comparator for cohesive inputs that fit reliably.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| One-shot long context | No intermediate summarization | Potential omissions and expensive rereads | Keep as comparator below measured pressure |
| Untraceable summary pyramid | Very small downstream prompt | Silent requirement loss | Reject |
| Lossless fragments plus bounded digests | Recoverable and traceable | Extraction and coverage overhead | Recommended for staged route |
| Vector database for every request | Selective semantic retrieval | Index cost and approximate recall | Defer until corpus reuse justifies it |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Recompute source/fragment hashes before accepting a prepared package and before final planning consumes it. Reject missing, changed, duplicate or escaping fragment references.
2. Add extraction coverage for table cells and document ordering, either in host extraction or a documented deterministic OOXML walker. Preserve headings, stable source anchors and explicit unsupported-content warnings.
3. Keep digest facts traceable to fragment IDs; record contradictions without resolving them in cheap extraction workers. Audit unique source obligations, not just the existence of a digest file.
4. Batch by semantic section within bounded token limits. For a large repetitive source deduplicate only the routing estimate, never the authoritative fragments.
5. Retain thresholds as tunable operational estimates. Measure digest omission and repeated reads before changing defaults or introducing fan-out.
6. Hash raw source, extracted block stream and fragments; reject stale fragments at final consumption, not only during initial preparation.
7. Traverse nested tables in document order and bound ZIP/XML input; record unsupported source structures rather than silently omitting them.
8. Measure obligation recall and contradiction coverage against one-shot and staged baselines before changing token thresholds.

## Acceptance and counterexamples

- Mutating one byte of a fragment after coverage approval invalidates the package.
- A DOCX fixture with requirements in paragraphs and table cells preserves all obligations in source order.
- Duplicates, missing IDs, contradictory clauses and symlinks are rejected or explicitly recorded.
- An interrupted batch resumes from validated digests without processing completed raw fragments again.
- Permuting a requirement between beginning, middle and end does not change final requirement coverage.
- A same-size fragment rewrite with unchanged timestamp is rejected.
- Nested and merged table cells produce ordered, nonduplicated source anchors.
- A requirement appearing only in a table cannot disappear from the final coverage map.
- Large repeated blocks change routing estimates without deletion from authoritative evidence.

## Cost, latency and quality decision

Preparation pays when C_extract+C_digest+C_review is lower than avoided rereads and recovery, while obligation recall meets the declared floor. Hashing is linear in input bytes and should not invoke an LLM.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-DOCX] python-docx maintainers, [Document objects, python-docx 1.2.0](https://python-docx.readthedocs.io/en/latest/api/document.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LITM] Liu et al. / TACL and arXiv, [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172). Accessed 2026-10-28. Reading scope: Paper abstract and publication metadata inspected; no reproduction and no claim to have read every experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRIEVAL] Google Research / Max McKinnon, [Retrieval Quality at Context Limit](https://research.google/pubs/retrieval-quality-at-context-limit/). Accessed 2026-10-28. Reading scope: Official publication abstract inspected; the result concerns simple factoid retrieval, not multi-file implementation correctness. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CONTEXT] Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-HARNESS] Anthropic, [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E006], [E003], [E007], [E008]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.python-docx.readthedocs.io iter_inner_content tables paragraphs document; site.arxiv.org Lost in the Middle long contexts; site.research.google retrieval quality context limit.

## Unverified limits and refresh triggers

- Image-only or embedded-object requirements still require an explicit extraction path. No live model comparison of digest quality was performed.
- Simple retrieval results do not establish multi-hop specification synthesis quality. No paid-model comparison or full Office-format conformance test was run.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
