# 010 - Adaptive Study: research revision 2

Date: 2026-10-28. Feature: `F003`. Implementation TODO `010`; independent review TODO `011`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Maintain a decision-oriented evidence ledger with explicit applicability and refresh triggers; stop research by unresolved decision risk, not source count.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The revision distinguishes search discovery from inspected evidence and introduces a bounded value-of-information rule. Author book resources are not represented as a full-book reading.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Separate user-selected depth from discovery breadth and stopping criteria.
- Evaluate authoritative evidence retrieval, access dates and deduplication without silently omitting requirements.

**Baseline observations:**
- studyctl normalizes explicit internal/external study choices and attaches evidence to planning. Its records distinguish questions, sources and synthesis.
- The former plan repeated research as a future task even though the user now requests research in advance. Prepared reports should be inputs, not a reason to restart the same literature search.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/studyctl.py` | `fefef4d70d93e92a2aaff124af727d26596de4a7935232c9b009df6269c94d82` | normalize_study:706; attach_study:1001 |
| `skill/plan-and-execute/scripts/studyctl_concise.py` | `7dc5480368dba06e5c5a14f91b4c41d896ec3b86c8864641929177a3f5d35735` |  |
| `skill/plan-and-execute/references/ADAPTIVE_STUDY.md` | `349f06551e9fd94a33f437d814c4c116339b9a111cebfe506bb6a5f0b59f50a3` | # Adaptive study protocol:1; ## 1. Classify before broad repository inspection:5; ### Simple:9; ### Medium:13 |
| `skill/plan-and-execute/references/STUDY_CHOICES.md` | `8c8adbcdc085eb181009926e3f6306fd99b5ff888de0cef6990e60e3843c4266` | # Complex-study choices:1; ## Recommendation marker:7; ## Interactive choice UI:31; ## Choice 1 — internal study:45 |

## Deeper analysis and competing approaches

### 1. Design analysis

A research record should answer a material design question: what could change the implementation, what evidence bears on it, and what remains unknown. Merely accumulating official URLs does not establish a decision. Preserve the prior conclusion and state whether new evidence strengthens, narrows or reverses it.

### 2. Design analysis

Use a shared source register but separate applicability per task. For example, an API cache rule is not evidence about subscription billing in a CLI. A model list proves a listed identifier, not permission, quality, effective reasoning effort or isolated quota. Store those as separate fields with unknown values when necessary.

### 3. Design analysis

Repeated broad research during implementation wastes tokens and can make a stable plan drift. Refresh only when a relevant CLI version, source digest, model contract or account capability changes. A retrieved page date and a claim observation date are different; record both when available.

### 4. Design analysis

Stop after each high-impact question has an evidence-backed decision or a safe capability-negotiation path. A missing critical fact cannot be hidden in an optimistic assumption. When the alternative would require a costly experiment, define a falsifiable test and a conservative fallback instead of declaring the hypothesis verified.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Fixed number of sources | Easy to automate | Counts quantity rather than decision coverage | Reject as readiness criterion |
| Unbounded exhaustive search | Potentially broad | Diminishing returns and no stopping rule | Reject |
| Question/evidence/decision ledger | Refreshes only material uncertainty | Needs disciplined applicability notes | Recommended |
| Always ask a separate research model | Isolation and parallelism | Extra cost and repeated retrieval | Use only for independent high-value gaps |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Add a compact reusable evidence record with material question, source/version/date, repository applicability, confidence and implementation consequence.
2. Distinguish verified source facts, observed repository behavior and proposed design. Store failed access attempts and unknowns explicitly rather than substituting a plausible fact.
3. Deduplicate shared external sources by stable ID while giving each task its own applicability analysis. Refresh only version-sensitive decisions or contradicted evidence.
4. Use a stopping condition: every high-impact question is answered or has a concrete implementation-time capability probe; no unresolved issue can silently change acceptance.
5. Preserve user-requested study breadth and the original source. Do not silently narrow a broad study to one blog or use an arbitrary source count as semantic proof.
6. Record discovery-only, abstract-only and inspected-section scopes separately; do not count inaccessible sources as verified support.
7. Attach every recommended change to a material question, repository applicability and a falsification condition.
8. Refresh evidence only on explicit invalidation signals; a task begins from its assigned report rather than restarting the literature survey.

## Acceptance and counterexamples

- A source with no date/version is flagged for refresh when it affects CLI behavior.
- Two tasks sharing the same source retain different applicability notes without copying an entire article.
- A contradictory provider document yields a probe requirement, not an invented resolution.
- Known prepared reports are consumed without requiring another broad research phase.
- A source that was only located cannot satisfy a verified-interface claim.
- An API pricing record cannot silently substitute for subscription-quota evidence.
- A provider-version change invalidates only affected recommendations, not all 32 reports.

## Cost, latency and quality decision

For each extra search, compare its expected chance of changing a material decision times avoided rework against search/read cost. This is an engineering stopping rule, not a measured probabilistic claim.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-BOOK] Chip Huyen, [AI Engineering supporting resources](https://github.com/chiphuyen/aie-book). Accessed 2026-10-28. Reading scope: Author-maintained book description and supporting-material index inspected; no claim of reading the paid book. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CONTEXT] Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-EVALSKILLS] OpenAI, [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E008], [E009], [E003], [E002]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.chiphuyen.com AI Engineering evaluation agents cost; site.anthropic.com effective context engineering agents retrieval; site.developers.openai.com eval skills.

## Unverified limits and refresh triggers

- No complete commercial book was available. This research uses the public AI Engineering excerpt and a public SRE chapter, explicitly labeled as such.
- Public material for AI Engineering is limited to the author resource index in this round; no paid book was read. Unknown account-specific facts remain unknown.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
