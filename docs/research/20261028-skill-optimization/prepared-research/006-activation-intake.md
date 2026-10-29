# 006 - Activation Intake: research revision 2

Date: 2026-10-28. Feature: `F001`. Implementation TODO `006`; independent review TODO `007`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep DIRECT as a zero-orchestration fast path, with explicit risk/promotion signals and evaluated activation; do not add a classifier call.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The first report favored a lightweight router but did not price activation errors. The revision adds a false-positive/false-negative decision test and explicitly compares one qualified agent at lower effort with delegated execution. Length is not a proxy for risk or independence.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Preserve DIRECT without planning overhead; distinguish size from semantic coupling.
- Measure request validation, explicit invocation and promotion of remaining outcomes.

**Baseline observations:**
- The entrypoint already distinguishes DIRECT, FINAL_PLAN and PRIMARY_PLAN. DIRECT is an early exit, not the removal of model-capability or optional validation safeguards.
- requestctl and promotectl separate intake from promotion. The latter preserves completed outcomes so promotion need not manufacture retrospective TODOs.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/requestctl.py` | `1a5aab982d6fa2397a9ecc7df8a7d27a72dbb697e23e3185360632accedda052` | RequestError:80; now_stamp:84; atomic_write_text:88; normalize_language:98 |
| `skill/plan-and-execute/scripts/promotectl.py` | `0ef7b8cbb138f814990420dfc48e4cfb472879d369e7572e08e88ed1c6f96e82` | PromotionError:26; _text:30; _list:39; normalize_spec:54 |
| `skill/plan-and-execute/SKILL.md` | `4af12fdfd1a7e7487e0cc96f67f924a548e6f541db1bb0b27221661edefab032` | # Plan and Execute:6; ## 1. Lifecycle and configuration:10; ## 2. Decide DIRECT vs ORCHESTRATED:16; ### DIRECT EXIT:20 |
| `skill/plan-and-execute/references/ROUTING.md` | `a08fc73ed533dea0f73fcfa5e7516a27851d9ef0603c42072d5bc3fd4d2cb14c` | # Selective activation routing:1; ## Objective:5; ## Strong orchestration signals:11; ## Negative triggers:21 |

## Deeper analysis and competing approaches

### 1. Design analysis

The cheapest routing decision is often the one already available from the request and repository metadata. A separate paid classifier has a fixed per-request charge and can still misclassify a tiny security edit or a large repetitive log. Keep explicit invocation and exact lifecycle commands deterministic; let implicit activation require evidence of durable coordination value.

### 2. Design analysis

Use a two-stage contract: cheap selection from purpose, interruption risk and independence, followed only after selection by context preparation. A cohesive CRUD with several files should not pay a planning tax. Conversely, a two-line authorization change can need strong implementation capability without needing durable orchestration. These are separate dimensions.

### 3. Design analysis

The new evaluation must compare four complete outcomes: no orchestration, explicit-only, selective metadata routing, and a paid classifier. Count unrequested planning files as a false-positive side effect. Evaluate late promotion after useful work has already occurred; promotion must not restart accepted work.

### 4. Design analysis

Research supports testing simple alternatives, not assuming the smallest instruction file will select correctly. Keep a small negative/near-miss corpus and a separate held-out activation sample. Metadata lint and phrase-presence tests are necessary structural checks but cannot establish actual host selection behavior.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Keep all requests direct | Lowest setup cost | No durable recovery for genuinely long work | Retain only for cohesive bounded work |
| Always orchestrate | Uniform tracking | Fixed token/latency tax and unnecessary artifacts | Reject as default |
| Selective metadata plus deterministic guards | No added routing model call | Needs host activation evaluation | Recommended |
| Paid classifier before every request | Learnable decision boundary | Extra call, privacy boundary and classification errors | Defer until measured net gain |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Extend the existing routing corpus with short high-risk changes, long repetitive logs, medium cohesive CRUDs, unrelated workstreams and nearly finished tasks under context pressure. Preserve explicit invocation behavior.
2. Represent a route decision with bounded reason codes, estimated working set and remaining outcomes. Do not persist a plan or load orchestration references on a negative implicit match.
3. Add a promotion regression that retains edits and completed tests while creating TODOs only for outstanding deliverables. Keep source evidence pointers rather than copied conversation history.
4. Keep exact lifecycle/configuration commands outside semantic routing. Document the optional validate-or-fix exit in one short pointer, not an eagerly loaded monitoring manual.
5. Record bounded reason codes only in the selected workflow; a rejected implicit match creates no plan, ledger or study files.
6. Evaluate activation false positives, false negatives, extra tokens, latency and final correctness on distinct held-out prompts.
7. Separate routing mode from capability tier so a small risky fix can stay DIRECT with a qualified implementation route.

## Acceptance and counterexamples

- A one-module feature touching seven files remains DIRECT and leaves no plan artifacts.
- A short security-sensitive fix remains direct when cohesive, but its model floor is not lowered.
- A promoted task includes only remaining outcomes and preserves the original worktree.
- Measure entrypoint bytes, referenced files actually loaded and routing false-positive/false-negative cases against baseline.
- A near-finished high-context task stays DIRECT without creating control files.
- A tiny security-sensitive edit can select a strong worker without forcing an orchestration plan.
- Promotion preserves changed files and validated outcomes and schedules only remaining work.

## Cost, latency and quality decision

Compare E[C]=C_select+P(false_positive)*C_unneeded_plan+P(false_negative)*C_recovery using measured task strata; include final validation quality as a constraint, not a weighted excuse for unsafe routing.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-SKILLS] Agent Skills, [Agent Skills specification](https://agentskills.io/specification). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-EVALSKILLS] OpenAI, [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-SIMPLE] Anthropic, [Building effective agents](https://www.anthropic.com/research/building-effective-agents). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-COST] Anthropic, [Optimizing for cost and intelligence](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence). Accessed 2026-10-28. Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E001], [E002], [E004], [E005]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: site.agentskills.io specification progressive disclosure; site.anthropic.com engineering effective harnesses long running agents; site.platform.claude.com docs optimizing cost intelligence October 2026 multiagent.

## Unverified limits and refresh triggers

- Natural-language route choice still needs host evaluation; passing string checks alone does not prove correct semantic routing.
- Automatic skill selection is host/model-dependent; structural metadata tests cannot measure it. No new model-call experiment was conducted.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
