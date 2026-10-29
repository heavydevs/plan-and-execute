# F001 / task 006 - Selective activation, intake and late promotion

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep a small selective router; add measured near-miss and promotion contracts instead of a second classifier model.

## Questions addressed

- Preserve DIRECT without planning overhead; distinguish size from semantic coupling.
- Measure request validation, explicit invocation and promotion of remaining outcomes.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The entrypoint already distinguishes DIRECT, FINAL_PLAN and PRIMARY_PLAN. DIRECT is an early exit, not the removal of model-capability or optional validation safeguards.
- requestctl and promotectl separate intake from promotion. The latter preserves completed outcomes so promotion need not manufacture retrospective TODOs.

### Read targets and integrity

- `skill/plan-and-execute/scripts/requestctl.py` (SHA-256 `1a5aab982d6fa2397a9ecc7df8a7d27a72dbb697e23e3185360632accedda052`): `RequestError` L80-81; `now_stamp` L84-85; `atomic_write_text` L88-95; `normalize_language` L98-110
- `skill/plan-and-execute/scripts/promotectl.py` (SHA-256 `0ef7b8cbb138f814990420dfc48e4cfb472879d369e7572e08e88ed1c6f96e82`): `PromotionError` L26-27; `_text` L30-36; `_list` L39-51; `normalize_spec` L54-101
- `skill/plan-and-execute/SKILL.md` (SHA-256 `4af12fdfd1a7e7487e0cc96f67f924a548e6f541db1bb0b27221661edefab032`): `# Plan and Execute` L6; `## 1. Lifecycle and configuration` L10; `## 2. Decide DIRECT vs ORCHESTRATED` L16; `### DIRECT EXIT` L20
- `skill/plan-and-execute/references/ROUTING.md` (SHA-256 `a08fc73ed533dea0f73fcfa5e7516a27851d9ef0603c42072d5bc3fd4d2cb14c`): `# Selective activation routing` L1; `## Objective` L5; `## Strong orchestration signals` L11; `## Negative triggers` L21

## External basis

- [E001] [Agent Skills specification](https://agentskills.io/specification) - Agent Skills; accessed 2026-10-28.
- [E002] [Building effective agents](https://www.anthropic.com/research/building-effective-agents) - Anthropic; accessed 2026-10-28.
- [E004] [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) - OpenAI; accessed 2026-10-28.
- [E005] [Evaluating skills](https://developers.openai.com/blog/eval-skills) - OpenAI; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Retain heuristic routing unchanged | Lowest change cost, but missing near-miss cases remain unmeasured. |
| recommended | Deterministic regression corpus plus compact reasons | Low runtime overhead; exposes ambiguous decisions without another inference call. |
| rejected | Always classify with a separate LLM or always orchestrate | Adds latency, tokens and a new failure point even for one grep or a small edit. |

## Implementation instructions

1. Extend the existing routing corpus with short high-risk changes, long repetitive logs, medium cohesive CRUDs, unrelated workstreams and nearly finished tasks under context pressure. Preserve explicit invocation behavior.
2. Represent a route decision with bounded reason codes, estimated working set and remaining outcomes. Do not persist a plan or load orchestration references on a negative implicit match.
3. Add a promotion regression that retains edits and completed tests while creating TODOs only for outstanding deliverables. Keep source evidence pointers rather than copied conversation history.
4. Keep exact lifecycle/configuration commands outside semantic routing. Document the optional validate-or-fix exit in one short pointer, not an eagerly loaded monitoring manual.

## Acceptance tests to implement and run

- [ ] A one-module feature touching seven files remains DIRECT and leaves no plan artifacts.
- [ ] A short security-sensitive fix remains direct when cohesive, but its model floor is not lowered.
- [ ] A promoted task includes only remaining outcomes and preserves the original worktree.
- [ ] Measure entrypoint bytes, referenced files actually loaded and routing false-positive/false-negative cases against baseline.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Use no additional model invocation for route selection. The value is avoided unnecessary orchestration, measured as artifact count and prompt bytes; dollar savings remain unmeasured.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Natural-language route choice still needs host evaluation; passing string checks alone does not prove correct semantic routing.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **006** now implements this recommendation; task **007** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
