# F010 / task 024 - Workload routing for frontend, repair and monitoring

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Route by task-specific quality evidence first, then cost and quota preference; never use one global intelligence rank as a frontend or observer score.

## Questions addressed

- Separate visual quality, code reasoning and cheap diagnostic workloads in evaluation.
- Compare manager-quota preservation with capability floors and independent Antigravity model families.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- workload_routing supports role/profile filtering and preferred pools without expanding the allowed provider chain.
- The current user scenarios distinguish frontend design, routine code, repair and observation. These have different acceptance conditions, and preserving the manager's quota is a preference, not permission to lower a capability floor.

### Read targets and integrity

- `skill/plan-and-execute/scripts/workload_routing.py` (SHA-256 `1a387675edbf3ef9e9b58dbc2fdcfa072173329ca864a4d1577ad7ca369147b1`): `candidates` L121-175; `antigravity_preset` L193-214
- `skill/plan-and-execute/scripts/configure.py` (SHA-256 `4e454ce5f6e141194bb5b2e95d5ba42e9b7a4f94d8bf4c957c2c1af3d003e8cd`): `Cancelled` L24-25; `Question` L29-35; `terminal_ask` L38-55; `discover` L58-76
- `skill/plan-and-execute/references/VALIDATION_WORKLOADS.md` (SHA-256 `a1c1e961444bc6d8f2537b17e6bfc8790d9a65b30a53a89de74432a2c654b081`): `# Plan-free validation and workload-aware routing` L1; `## DIRECT does not mean unmonitored` L5; `## Four independent axes` L25; `## Explicit profile configuration` L36

## External basis

- [E013] [RouteLLM: Learning to Route LLMs from Preference Data](https://arxiv.org/abs/2406.18665) - Ong et al. / arXiv; accessed 2026-10-28.
- [E025] [Models](https://antigravity.google/docs/models/) - Google; accessed 2026-10-28.
- [E026] [Plans](https://antigravity.google/docs/plans) - Google; accessed 2026-10-28.
- [E050] [Visual comparisons](https://playwright.dev/docs/test-snapshots) - Microsoft Playwright; accessed 2026-10-28.
- [E051] [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/) - W3C; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | One global model ordering | Low setup cost but cannot represent visual skill, repair reliability or tool isolation. |
| recommended | Role-specific qualification plus explicit economic preferences | A small calibration cost with transparent quality floors. |
| rejected | Always choose a named Flash model or hosted Opus because it sounds cheaper | Availability, limits and capability vary by account, model and host. |

## Implementation instructions

1. Create a small versioned workload evaluation set for frontend, implementation, repair and observer roles. Record criteria and observations per actual model/profile rather than hardcoding brand superiority.
2. For frontend, combine functional flows, controlled screenshot comparisons, accessibility checks and human/design review. A visually attractive screenshot does not certify behavior.
3. For observers, measure anomaly recall, false alarms, bounded output, latency and inability to write. Prefer deterministic classification first, then an eligible inexpensive model for ambiguous evidence.
4. Use account-scoped quota-pool metadata to prefer Antigravity alternatives only after confirming model/effort support and acceptable workload quality. Unknown data cannot establish equivalence to the highest native Claude route.
5. Record the selected role, floor, profile and exclusion reasons. Fall back deterministically to another allowed suitable profile, never to a cheaper but disallowed capability.

## Acceptance tests to implement and run

- [ ] A preferred intermediate profile is excluded from a maximum-capability task when its validated range is lower.
- [ ] An observer profile cannot be selected for a source-writing task or gain write tools on fallback.
- [ ] Frontend evaluation detects broken keyboard navigation even when screenshots match.
- [ ] A depleted Gemini pool can use another configured pool without assuming all accounts have independent allocations.
- [ ] Unknown economics remains unknown; ties use stable policy instead of invented prices.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Compare cost per accepted task in each workload, including retries, screenshots, reviewers and observation overhead. Subscription quota and API spend are separate columns; no universal cheapest-model claim is made.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No authenticated model A/B trial or independent visual evaluation was run. The report defines how to obtain that evidence before enabling automatic selection.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **024** now implements this recommendation; task **025** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
