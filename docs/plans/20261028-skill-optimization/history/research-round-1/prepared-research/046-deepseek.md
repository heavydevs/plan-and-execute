# F021 / task 046 - DeepSeek provider profiles

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep DeepSeek compatibility translation explicit and conservative; separate native thinking controls, harness security and dated economics.

## Questions addressed

- Verify model effort compatibility and host sandbox inherited by each profile.
- Separate published prices, off-peak windows and unknown subscription costs.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The repository includes DeepSeek profile tests and provider guidance while execution may still use a different host CLI.
- DeepSeek documents an Anthropic-compatible interface and native thinking controls. API compatibility does not establish identical parameters, model capability or billing.

### Read targets and integrity

- `skill/plan-and-execute/scripts/routing_config.py` (SHA-256 `4c21ed17b26062511023e151edd60f56eb68219129418303f17ddc2b26e9d4e4`): `validate` L112-213; `load` L285-302
- `skill/plan-and-execute/scripts/deepseek_provider_self_test.py` (SHA-256 `f28eb83e4c2c43cd31bdd8a9506385b7cd7ebc1eeb987c3ea7a998b2de346461`): `utc` L32-33; `argv` L36-39; `with_profile` L42-46; `test_profiles_resolve_on_both_harnesses` L49-69
- `skill/plan-and-execute/references/MODEL_ROUTING_DEEPSEEK.md` (SHA-256 `7f13e72569bb294e560edb9df7cca73576b6a402cbc6f7b2e1e53ff731315fc4`): `# DeepSeek routing (lazy reference)` L1; `## Profiles` L5; `## Bootstrap catalog (dated 2026-10-01, evidence not placement)` L16; `## Pricing` L27

## External basis

- [E036] [Anthropic API compatibility](https://api-docs.deepseek.com/guides/anthropic_api/) - DeepSeek; accessed 2026-10-28.
- [E037] [Thinking mode](https://api-docs.deepseek.com/guides/thinking_mode/) - DeepSeek; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.
- [E013] [RouteLLM: Learning to Route LLMs from Preference Data](https://arxiv.org/abs/2406.18665) - Ong et al. / arXiv; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Assume Anthropic-compatible means identical semantics | Low setup cost but hides translation and capability mismatches. |
| recommended | Qualified native mapping with separate economics | Small explicit adapter contract and trustworthy cost comparisons. |
| rejected | Automatically choose a cheap advertised model for all repairs | Can increase retries or silently fail important validations. |

## Implementation instructions

1. Represent the backend model and native thinking/effort mapping as catalog evidence with a version/date, independent of the host's logical tier labels.
2. Test supported parameter translation for the chosen API/harness combination; omit unsupported options only through an explicit compatibility rule, not by silently lowering a requested capability.
3. Keep sandbox and tool permissions those of the actual harness; a different endpoint must not gain broader write/network authority.
4. Treat published prices, cache behavior and any off-peak window as dated metadata. Preserve unknown subscription economics and missing usage as null.
5. Use backend/pool identity for availability and telemetry and retain the same bounded failure/handoff contract.

## Acceptance tests to implement and run

- [ ] A compatible endpoint does not cause Claude-native effort values to be sent blindly.
- [ ] A route with unverified high-effort support cannot satisfy a maximum task merely through a label.
- [ ] Time-window price fixtures cover boundaries and timezone interpretation without assuming current discounts.
- [ ] Endpoint/profile changes invalidate route intent and preserve unrelated cooldown state.
- [ ] No endpoint credentials appear in process logs, manifests or economic reports.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure total accepted-task cost including retry and review, not only advertised input prices. No current discount, subscription price or universal saving is asserted here.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No authenticated DeepSeek execution, price refresh experiment or host sandbox validation was performed.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **046** now implements this recommendation; task **047** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
