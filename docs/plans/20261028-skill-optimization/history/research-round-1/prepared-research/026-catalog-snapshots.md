# F011 / task 026 - Model catalog evidence, caches, snapshots and refresh

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep provider-scoped cache and plan snapshots; add evidence-preserving capability reconciliation and make unknown tiers explicit.

## Questions addressed

- Check TTL by facet, stale fallback, empty-tier lifting and immutable in-progress routes.
- Measure refresh costs and verify model/effort against live discovery without inventing entries.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- model_catalogctl manages per-provider cache files, independent facet freshness and plan-local model matrices. Snapshot refresh rebases pending tasks, not running attempts.
- The catalog distinguishes capability, quality and economics. A provider model ID existing in a list does not prove its effort support, workload quality or price.

### Read targets and integrity

- `skill/plan-and-execute/scripts/model_catalog.py` (SHA-256 `848e9b723845dc294bc39dc267357168dfc77f5ecdba67dd5f92f4556db88cbb`): `validate` L212-252; `facet_freshness` L295-308
- `skill/plan-and-execute/scripts/model_catalogctl.py` (SHA-256 `3406cf04a4a35aa3bdee9d69d3c9605410428c538c969994825ca0487464b69a`): `plan_refresh` L230-241; `refresh` L288-354
- `skill/plan-and-execute/references/MODEL_CATALOG.md` (SHA-256 `c751d391d8ce957720f3e5bf056c5fbb33413c2d6e19deaa6504a7a5c800841e`): `# Model catalog contract` L1; `## Schema (`schema_version` 1)` L5; `## Freshness policy (`2026-10-01-v1`)` L36; `## Digest and versioning` L48

## External basis

- [E025] [Models](https://antigravity.google/docs/models/) - Google; accessed 2026-10-28.
- [E022] [Antigravity CLI reference](https://antigravity.google/docs/cli/reference/) - Google; accessed 2026-10-28.
- [E015] [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference) - Anthropic; accessed 2026-10-28.
- [E019] [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) - OpenAI; accessed 2026-10-28.
- [E058] [Semantic Versioning 2.0.0](https://semver.org/) - SemVer; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Embedded dated model map only | Fast and offline, but cannot establish current availability or pricing. |
| recommended | Scoped observed catalog plus pinned attempts | Bounded discovery cost, reproducible execution and controlled refresh. |
| rejected | Fetch all provider catalogs and prices on every task | Wastes latency and can make identical retries choose unstable routes. |

## Implementation instructions

1. Collect non-generative version/help/model-list observations through bounded adapter-specific probes and persist only normalized public capability metadata.
2. Key compatibility by CLI version and resolved model/profile. Invalidate capability facts on version changes without needlessly refreshing price and quality evidence.
3. Keep missing model/price/quality fields null and provide explicit reasons. Lift a missing tier upward when allowed; never synthesize a nonexistent model or silently lower the floor.
4. On an invalid-model response, allow one documented refresh/re-resolution path, then report a plan/configuration defect. Prevent indefinite refresh loops.
5. Pin the chosen effective model for an in-progress attempt and record catalog digest/provenance. Refreshing a shared cache must not rewrite an active worker route.

## Acceptance tests to implement and run

- [ ] Fresh facets produce no network/probe calls; expired or changed-version capability triggers only its required source.
- [ ] A failing refresh retains the last valid cache with a visible stale warning.
- [ ] Concurrent refreshes of different providers do not overwrite one another.
- [ ] An empty advanced tier lifts to a configured stronger tier or yields an explicit ineligible candidate.
- [ ] An in-progress task retains its model while pending tasks can rebase with an audit entry.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Count refresh/probe calls and cache age, not just token savings. Bootstrap is fallback evidence with a date; it is not authorization to claim current model economics.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Specific model slugs and version probes remain environment-dependent. This session read documentation but did not query authenticated provider inventories.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **026** now implements this recommendation; task **027** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
