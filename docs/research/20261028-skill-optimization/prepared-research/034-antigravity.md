# 034 - Antigravity: research revision 2

Date: 2026-10-28. Feature: `F015`. Implementation TODO `034`; independent review TODO `035`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Treat Antigravity as a versioned multi-backend harness with account-scoped quotas and billing; derive effort from actual model capabilities and keep unproven read-only observation disabled.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

New primary evidence shows a documentation conflict on effort flags and different enterprise billing for partner models. Independent quota must no longer be conflated with no cost, and a fixed Antigravity high-only ceiling is not justified for every future model.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Check agy models, embedded-effort slugs, conversation persistence and per-family quotas.
- Distinguish current Antigravity behavior from legacy Gemini; document CLI/help/model-list discrepancies.

**Baseline observations:**
- The adapter suppresses a separate effort argument for recognized embedded-effort model slugs. A logical effort increment can therefore leave the actual command unchanged.
- The configuration and workload modules can represent different Antigravity profiles and quota pools. Current docs expose a wider effort vocabulary with model-dependent support, so a universal high-only statement is not reliable.
- The runner uses a fresh prompt invocation without a continuation ID; the exact conversation retention behavior is a version-specific operational question.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/run_isolated.py` | `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df` | build_worker_command:1034 |
| `skill/plan-and-execute/scripts/routing_config.py` | `4c21ed17b26062511023e151edd60f56eb68219129418303f17ddc2b26e9d4e4` | embedded_effort_model:106 |
| `skill/plan-and-execute/scripts/workload_routing.py` | `1a387675edbf3ef9e9b58dbc2fdcfa072173329ca864a4d1577ad7ca369147b1` | antigravity_preset:193 |
| `skill/plan-and-execute/references/INSTALLATION.md` | `679e881535934274a60615aaa36befbf30bc15ae6302dc66dceb6a7a8d45b2ff` | # Install Plan and Execute for Claude Code, Codex and Antigravity:1; ## Activation mode:9; ## Recommended: install with npx:23; # Claude and Codex for every project; selective auto-routing:63 |

## Deeper analysis and competing approaches

### 1. Design analysis

The dedicated effort page and headless flag reference are not fully aligned. Preserve both observations, then let a bounded non-generative capability probe or a pinned-version fixture determine supported flags and variants. Do not automatically enable max because one page lists it, and do not permanently cap all variants at high because an older adapter did so.

### 2. Design analysis

Public model availability establishes candidate names but not the user account entitlement. Keep requested slug, resolved variant, backend family, native effort and quota scope separate. Embedded effort in a slug can make an explicit effort flag redundant or contradictory; effective candidate equivalence must account for the actual command and model response contract.

### 3. Design analysis

The enterprise rollout documents a different accounting boundary for partner Claude models and also first-party coordination consumption. Individual plans have baseline quotas and configurable overages. Thus switching away from the manager can preserve one quota while spending cash or another quota. Require the configured billing policy to permit it, and report unknown marginal cost instead of assuming an independent free pool.

### 4. Design analysis

The ordinary terminal sandbox still permits workspace writes. An observer must not receive a repair-capable workspace merely because a cheap Flash model was selected. Keep tool-less or genuinely read-only execution as a tested capability; when unavailable, continue deterministic monitoring and skip optional advice. Do not stall healthy tests waiting for an LLM.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| One provider id and fixed high cap | Simple existing adapter | Conflates backends and may stale | Legacy behavior only |
| Always prefer partner Claude to save manager quota | May conserve one pool | Can incur charges or lower effective capability | Reject as unconditional default |
| Account-scoped variants, effort and billing | Accurate eligibility and cost constraints | Needs capability observations | Recommended |
| Always-on Flash observer | Frequent interpretation | Unnecessary tokens and possible write access | Reject; event-triggered restricted advice only |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Persist normalized agy version/help/models/usage observations with timestamp. Intersect CLI-supported effort with each model's advertised capability; do not assume max in help applies to every slug.
2. Derive effective dispatch from resolved slug plus native effort. Collapse no-op transitions and preserve unsupported capability as an exclusion reason.
3. Map quota pools from explicit account evidence or configuration, not a universal Gemini-versus-Claude assumption. Prefer a suitable alternate pool only within the permitted chain.
4. Pin a verified read-only observer path. Approval skipping must not be mistaken for a sandbox; on unsupported versions disable advisory dispatch rather than widen authority.
5. Keep the legacy Gemini adapter behind its own contract and deprecation note. Do not auto-migrate user configuration or silently substitute a different CLI.
6. Record the conflict between headless effort docs and the effort command; resolve with pinned-version capabilities, not an invented universal cap.
7. Separate partner-model quota from credit/cash and first-party coordination charges; never enable paid overages automatically.
8. Require proven read-only boundaries before any Antigravity observer; otherwise use deterministic monitoring only.

## Acceptance and counterexamples

- An embedded high slug receives no redundant effort flag and is not retried as a supposedly stronger identical dispatch.
- A model with lower effort support cannot satisfy a higher required route without explicit qualification.
- Separate configured pools have separate cooldowns; shared pools remain shared.
- Usage discovery failure leaves quota unknown and does not consume semantic attempts.
- Headless parser, conversation metadata and read-only restrictions have version-pinned fixtures.
- A documented but unavailable max variant is skipped with a capability reason.
- Embedded-effort aliases that yield identical dispatch are collapsed.
- A separate quota pool cannot bypass disabled paid-overage policy.
- Workspace-write sandbox support does not qualify a route as read-only.

## Cost, latency and quality decision

Minimize total validated cost under quality, quota and spending constraints. Manager-token conservation is a secondary metric; account cash, partner credits and coordination tokens remain separate.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-AGY-EFFORT] Google, [Effort command](https://antigravity.google/docs/cli/commands/effort). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-HEADLESS] Google, [Headless mode](https://antigravity.google/docs/cli/headless/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-MODELS] Google, [Choose a model](https://antigravity.google/docs/models). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-PLANS] Google, [Plans and overages](https://www.antigravity.google/docs/plans). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-ENTERPRISE] Google Cloud, [Claude Opus and Sonnet in Antigravity](https://cloud.google.com/blog/products/ai-machine-learning/claude-opus-55-and-claude-sonnet-55-available-in-antigravity/). Accessed 2026-10-28. Reading scope: Official rollout article billing/governance section inspected; enterprise scope explicitly retained. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-PERMISSIONS] Google, [Permissions](https://antigravity.google/docs/permissions/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E022], [E023], [E024], [E025], [E026], [E027], [E028]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.antigravity.google quota Claude Gemini; site.antigravity.google headless sandbox; site.antigravity.google effort xhigh max; Google Cloud Claude Opus Sonnet Antigravity partner billing.

## Unverified limits and refresh triggers

- Actual quota independence, model availability, conversation persistence and highest effective effort require the user's installed CLI/account.
- Actual account pools, supported slugs and installed CLI were not probed. Enterprise billing facts are not generalized to consumer plans; Flash superiority remains an evaluation hypothesis.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
