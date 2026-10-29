# 024 - Workload Affinity: research revision 2

Date: 2026-10-28. Feature: `F010`. Implementation TODO `024`; independent review TODO `025`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Route by measured workload capability and validation strength, with separate design, functional UI, monitoring and repair requirements rather than a universal model leaderboard.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The previous broad frontend affinity becomes a multi-axis acceptance contract. Gemini 3.8 Flash remains an observed available candidate, not an untested cheapest or universally best monitoring model.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Separate visual quality, code reasoning and cheap diagnostic workloads in evaluation.
- Compare manager-quota preservation with capability floors and independent Antigravity model families.

**Baseline observations:**
- workload_routing supports role/profile filtering and preferred pools without expanding the allowed provider chain.
- The current user scenarios distinguish frontend design, routine code, repair and observation. These have different acceptance conditions, and preserving the manager's quota is a preference, not permission to lower a capability floor.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/workload_routing.py` | `1a387675edbf3ef9e9b58dbc2fdcfa072173329ca864a4d1577ad7ca369147b1` | candidates:121; antigravity_preset:193 |
| `skill/plan-and-execute/scripts/configure.py` | `4e454ce5f6e141194bb5b2e95d5ba42e9b7a4f94d8bf4c957c2c1af3d003e8cd` | Cancelled:24; Question:29; terminal_ask:38; discover:58 |
| `skill/plan-and-execute/references/VALIDATION_WORKLOADS.md` | `a1c1e961444bc6d8f2537b17e6bfc8790d9a65b30a53a89de74432a2c654b081` | # Plan-free validation and workload-aware routing:1; ## DIRECT does not mean unmonitored:5; ## Four independent axes:25; ## Explicit profile configuration:36 |

## Deeper analysis and competing approaches

### 1. Design analysis

Visual design, screenshot reproduction, interactive behavior and accessibility are different workloads. A model that scores well on general code may miss visual hierarchy; a visually attractive output may break keyboard navigation or API behavior. Represent workload requirements as capabilities and test obligations rather than a subjective brand preference.

### 2. Design analysis

Build a small repository-specific front-end corpus with responsive states, keyboard interactions, semantic structure and functional assertions. Visual baselines require a pinned browser/font/viewport environment. Keep a human or independently qualified visual review when acceptance includes aesthetics; automated image similarity cannot establish design quality by itself.

### 3. Design analysis

Monitoring is primarily parsing, counters and health probes. It should use no model during normal operation. Invoke a low-cost eligible observer only for a novel ambiguous diagnostic packet; a repair task is a separate workload and can require stronger reasoning. The observed model catalog can supply Flash candidates, but quota, capability and inference cost remain account- and harness-specific.

### 4. Design analysis

Manager quota preservation is a preference after safety and quality floors. An Antigravity-hosted Claude route must not inherit the maximum native Claude capability merely because the family name matches. Compare qualified routes at the required effort; when the highest effective route is unavailable, pause or use another qualified route rather than silently downgrade.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| One global best model | Easy settings | Ignores visual versus functional capability | Reject |
| Static brand affinity table | Cheap routing | Stale or unsupported superiority claims | Bootstrap only, with dated evidence |
| Workload capabilities plus task-specific validation | Auditable quality floor | Needs representative examples | Recommended |
| Always use multimodal frontier for frontend | Strong general baseline | Pays high cost for mechanical CSS edits | Use only when risk and evidence justify |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Create a small versioned workload evaluation set for frontend, implementation, repair and observer roles. Record criteria and observations per actual model/profile rather than hardcoding brand superiority.
2. For frontend, combine functional flows, controlled screenshot comparisons, accessibility checks and human/design review. A visually attractive screenshot does not certify behavior.
3. For observers, measure anomaly recall, false alarms, bounded output, latency and inability to write. Prefer deterministic classification first, then an eligible inexpensive model for ambiguous evidence.
4. Use account-scoped quota-pool metadata to prefer Antigravity alternatives only after confirming model/effort support and acceptable workload quality. Unknown data cannot establish equivalence to the highest native Claude route.
5. Record the selected role, floor, profile and exclusion reasons. Fall back deterministically to another allowed suitable profile, never to a cheaper but disallowed capability.
6. Separate visual design, UI behavior, accessibility, observation and repair capabilities in workload evidence.
7. Use deterministic monitoring first; route only bounded novel ambiguity to a permitted observer.
8. Treat manager-quota preference as secondary to capability, privacy and validation floors; never infer effective effort from a family label.

## Acceptance and counterexamples

- A preferred intermediate profile is excluded from a maximum-capability task when its validated range is lower.
- An observer profile cannot be selected for a source-writing task or gain write tools on fallback.
- Frontend evaluation detects broken keyboard navigation even when screenshots match.
- A depleted Gemini pool can use another configured pool without assuming all accounts have independent allocations.
- Unknown economics remains unknown; ties use stable policy instead of invented prices.
- A visual-only success cannot satisfy a task with keyboard and functional acceptance checks.
- A cheap observer route is never selected to implement an architecture-sensitive repair.
- A manager quota preference cannot lower the minimum effective capability.
- Unknown quota or cost values do not become zero-cost priority.

## Cost, latency and quality decision

Compare quality-constrained cost per workload stratum; report visual acceptance, functional pass rate and accessibility defects separately. Monitor cost should approach zero model tokens on healthy runs.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-FRONTEND] SALT-NLP authors / ACL, [Design2Code](https://aclanthology.org/2025.naacl-long.199/). Accessed 2026-10-28. Reading scope: Primary publication abstract and author benchmark description inspected, not every paper experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-VISUAL-TESTS] Microsoft Playwright, [Visual comparisons](https://playwright.dev/docs/test-snapshots). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-ACCESSIBILITY] W3C WAI, [Evaluating Web Accessibility Overview](https://www.w3.org/WAI/test-evaluate/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-MODELS] Google, [Choose a model](https://antigravity.google/docs/models). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E013], [E025], [E026], [E050], [E051]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: Design2Code front end benchmark limitations; Playwright visual comparisons stable screenshots; W3C accessibility evaluation automated testing; Anthropic cost intelligence subagents evaluation.

## Unverified limits and refresh triggers

- No authenticated model A/B trial or independent visual evaluation was run. The report defines how to obtain that evidence before enabling automatic selection.
- No live cross-model frontend benchmark or account pricing test was performed. Public catalog presence is verified; comparative quality and marginal subscription cost remain hypotheses.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.

## Capability identity versus availability identity

Keep capability identity separate from availability identity: changing only a quota pool, request ID, log path or credential reference cannot create a stronger rung. Resolve known aliases and native effort before deduplication; retain the harness/backend boundary rather than equating model-family names across hosts.

This is an engineering contract for the proposed implementation, not a claim that quota-pool isolation or cross-harness intelligence equivalence was measured.
