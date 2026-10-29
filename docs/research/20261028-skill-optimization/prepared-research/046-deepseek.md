# 046 - Deepseek: research revision 2

Date: 2026-10-28. Feature: `F021`. Implementation TODO `046`; independent review TODO `047`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep DeepSeek compatibility, resolved model identity and billing evidence explicit; validate unsupported or ignored fields rather than assuming full Anthropic equivalence.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

New documentation confirms accepted legacy names can serve replacements and Claude-prefixed aliases can map to DeepSeek backends. Effective-route identity and price freshness are now mandatory.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Verify model effort compatibility and host sandbox inherited by each profile.
- Separate published prices, off-peak windows and unknown subscription costs.

**Baseline observations:**
- The repository includes DeepSeek profile tests and provider guidance while execution may still use a different host CLI.
- DeepSeek documents an Anthropic-compatible interface and native thinking controls. API compatibility does not establish identical parameters, model capability or billing.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/routing_config.py` | `4c21ed17b26062511023e151edd60f56eb68219129418303f17ddc2b26e9d4e4` | validate:112; load:285 |
| `skill/plan-and-execute/scripts/deepseek_provider_self_test.py` | `f28eb83e4c2c43cd31bdd8a9506385b7cd7ebc1eeb987c3ea7a998b2de346461` | utc:32; argv:36; with_profile:42; test_profiles_resolve_on_both_harnesses:49 |
| `skill/plan-and-execute/references/MODEL_ROUTING_DEEPSEEK.md` | `7f13e72569bb294e560edb9df7cca73576b6a402cbc6f7b2e1e53ff731315fc4` | # DeepSeek routing (lazy reference):1; ## Profiles:5; ## Bootstrap catalog (dated 2026-10-01, evidence not placement):16; ## Pricing:27 |

## Deeper analysis and competing approaches

### 1. Design analysis

An Anthropic-shaped endpoint is not the Anthropic model or full feature set. Keep the compatibility matrix close to the adapter, covering tool use, structured results, thinking parameters, ignored headers and unsupported content. Reject a required feature that is ignored rather than relying on an HTTP success response.

### 2. Design analysis

Record requested and resolved model names when the provider exposes the latter. Alias retirement without a request error can invalidate a previous price or quality observation. Capability snapshots need dated evidence and a requalification path, not only a list of accepted strings.

### 3. Design analysis

Treat cache and off-peak economics as versioned optional evidence. A discount must not override privacy, capability or deadline requirements, and a missing token field is unknown, not zero. Do not delay urgent work merely to reach an off-peak interval unless the user explicitly selected that policy.

### 4. Design analysis

Use isolated environment profiles and deterministic compatibility fixtures before live experiments. Preserve the legacy disabled behavior and stable prompt prefix. Raw provider errors can contain request details; redact before they enter the failure capsule or telemetry.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Assume complete Anthropic compatibility | Low adapter complexity | Ignored options and misidentified models | Reject |
| Hardcode latest DeepSeek alias | Easy updates | Silent serving replacement and drift | Bootstrap only |
| Capability matrix plus resolved identity | Detects material drift | Requires evidence refresh | Recommended |
| Always choose cheapest/off-peak route | Lower listed input price | May violate quality, latency or consent | Reject as global policy |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Represent the backend model and native thinking/effort mapping as catalog evidence with a version/date, independent of the host's logical tier labels.
2. Test supported parameter translation for the chosen API/harness combination; omit unsupported options only through an explicit compatibility rule, not by silently lowering a requested capability.
3. Keep sandbox and tool permissions those of the actual harness; a different endpoint must not gain broader write/network authority.
4. Treat published prices, cache behavior and any off-peak window as dated metadata. Preserve unknown subscription economics and missing usage as null.
5. Use backend/pool identity for availability and telemetry and retain the same bounded failure/handoff contract.
6. Test required parameters against documented supported and ignored fields; successful HTTP is not sufficient compatibility evidence.
7. Track alias replacement and backend identity separately from requested model labels and refresh price/quality evidence.
8. Treat off-peak discounts as optional evidence that cannot override deadline, privacy or capability constraints.

## Acceptance and counterexamples

- A compatible endpoint does not cause Claude-native effort values to be sent blindly.
- A route with unverified high-effort support cannot satisfy a maximum task merely through a label.
- Time-window price fixtures cover boundaries and timezone interpretation without assuming current discounts.
- Endpoint/profile changes invalidate route intent and preserve unrelated cooldown state.
- No endpoint credentials appear in process logs, manifests or economic reports.
- A required schema or thinking option reported ignored cannot qualify the route.
- A retired alias serving a replacement triggers evidence requalification without rewriting past attempts.
- Missing usage remains null and positive infinity is rejected.
- No automatic paid endpoint or off-peak waiting policy is enabled.

## Cost, latency and quality decision

Compare total input/cache/output and retry cost per validated result, not advertised base-token price alone. Distinguish observed invoice units from estimates.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-DEEPSEEK] DeepSeek, [Anthropic API compatibility](https://api-docs.deepseek.com/guides/anthropic_api/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-DEEPSEEK-MODELS] DeepSeek, [Model aliases and first API call](https://api-docs.deepseek.com/quick_start/pricing). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OPENAI-CACHE] OpenAI, [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-LOGGING] OWASP, [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E036], [E037], [E044], [E013]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: DeepSeek Anthropic API compatibility model aliases ignored fields; DeepSeek retired model aliases served replacement pricing; provider cache usage cost accounting.

## Unverified limits and refresh triggers

- No authenticated DeepSeek execution, price refresh experiment or host sandbox validation was performed.
- No DeepSeek API call or invoice was inspected. Serving identity is only verifiable when the endpoint provides it or the account owner confirms it.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.
