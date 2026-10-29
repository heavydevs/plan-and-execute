# 026 - Catalog Snapshots: research revision 2

Date: 2026-10-28. Feature: `F011`. Implementation TODO `026`; independent review TODO `027`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Keep provider-scoped catalog evidence with independently aged facets and immutable attempt bindings; treat aliases and pricing changes as observable model-resolution events.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

The new evidence invalidates timeless cache-price assumptions and shows that accepted aliases can change serving models. The catalog needs requested/resolved identity and provenance rather than only model names and TTLs.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Check TTL by facet, stale fallback, empty-tier lifting and immutable in-progress routes.
- Measure refresh costs and verify model/effort against live discovery without inventing entries.

**Baseline observations:**
- model_catalogctl manages per-provider cache files, independent facet freshness and plan-local model matrices. Snapshot refresh rebases pending tasks, not running attempts.
- The catalog distinguishes capability, quality and economics. A provider model ID existing in a list does not prove its effort support, workload quality or price.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/model_catalog.py` | `848e9b723845dc294bc39dc267357168dfc77f5ecdba67dd5f92f4556db88cbb` | validate:212; facet_freshness:295 |
| `skill/plan-and-execute/scripts/model_catalogctl.py` | `3406cf04a4a35aa3bdee9d69d3c9605410428c538c969994825ca0487464b69a` | plan_refresh:230; refresh:288 |
| `skill/plan-and-execute/references/MODEL_CATALOG.md` | `c751d391d8ce957720f3e5bf056c5fbb33413c2d6e19deaa6504a7a5c800841e` | # Model catalog contract:1; ## Schema (`schema_version` 1):5; ## Freshness policy (`2026-10-01-v1`):36; ## Digest and versioning:48 |

## Deeper analysis and competing approaches

### 1. Design analysis

Availability, native effort, tool/schema compatibility, economics and measured quality change at different rates. Refresh only the stale facet needed for a decision. A catalog hit saves model and network calls, but a stale safety capability should not inherit the more permissive value from a price refresh.

### 2. Design analysis

An alias can keep working while its backend changes. Bind an attempt to the requested id, observed resolved id when available, harness version, profile and capability evidence digest. If resolution is unobservable, mark it unknown and avoid claiming a duplicate-dispatch proof across two possibly different backends. Do not inspect or store raw credentials to derive identity.

### 3. Design analysis

API cache writes and reads must be data fields, not provider-wide timeless constants. Preserve cash cost, subscription credits and latency independently. Missing price data is not free. Existing plan snapshots protect reproducibility; refresh pending candidates under explicit policy while allowing an in-progress attempt to finish with its original binding.

### 4. Design analysis

Use conditional generation updates for cache writers and bounded stale fallback. A failed refresh should retain the last valid record with its age and warning; it must not overwrite valid evidence with an empty successful-looking document. The added complexity should remain local to the catalog rather than introducing a registry service dependency.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| Hardcoded latest model ids and prices | Minimal I/O | Aliases and pricing drift silently | Reject as sole authority |
| Refresh everything before every task | Current-looking data | Latency and provider calls with little value | Reject |
| Facet-scoped cached evidence plus attempt binding | Efficient and reproducible | Needs explicit unknown/stale states | Recommended |
| Central live catalog service | Shared governance | New availability and privacy dependency | Defer until multi-host scale warrants it |

## Ownership and scope boundary

This implementation owns its declared write scope and acceptance tests. Its following review checks the actual changed code; prepared research is not acceptance evidence.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Collect non-generative version/help/model-list observations through bounded adapter-specific probes and persist only normalized public capability metadata.
2. Key compatibility by CLI version and resolved model/profile. Invalidate capability facts on version changes without needlessly refreshing price and quality evidence.
3. Keep missing model/price/quality fields null and provide explicit reasons. Lift a missing tier upward when allowed; never synthesize a nonexistent model or silently lower the floor.
4. On an invalid-model response, allow one documented refresh/re-resolution path, then report a plan/configuration defect. Prevent indefinite refresh loops.
5. Pin the chosen effective model for an in-progress attempt and record catalog digest/provenance. Refreshing a shared cache must not rewrite an active worker route.
6. Represent requested id, observed resolved id, harness version and evidence digest separately for each attempt.
7. Version cache-write/read prices by model and billing mode; unknown cost never means free.
8. Test concurrent refresh and stale fallback without rewriting bindings of in-progress tasks.

## Acceptance and counterexamples

- Fresh facets produce no network/probe calls; expired or changed-version capability triggers only its required source.
- A failing refresh retains the last valid cache with a visible stale warning.
- Concurrent refreshes of different providers do not overwrite one another.
- An empty advanced tier lifts to a configured stronger tier or yields an explicit ineligible candidate.
- An in-progress task retains its model while pending tasks can rebase with an audit entry.
- An alias backend change invalidates the relevant candidate evidence while keeping the old attempt record intact.
- Failed partial refresh leaves valid prior facets readable with explicit age.
- Legacy config snapshots do not inherit a newly enabled global switch policy.
- Unknown prices cannot win a cost comparison by being treated as zero.

## Cost, latency and quality decision

One metadata refresh should amortize over valid uses; price the refresh itself and compare it with saved dispatch failures. Never apply API cache prices to subscription usage without evidence.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-OPENAI-CACHE] OpenAI, [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-DEEPSEEK-MODELS] DeepSeek, [Model aliases and first API call](https://api-docs.deepseek.com/quick_start/pricing). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-GLM] Z.ai, [Claude Code integration](https://docs.z.ai/devpack/tool/claude). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-EFFORT] Google, [Effort command](https://antigravity.google/docs/cli/commands/effort). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-CAS] Kubernetes, [Kubernetes API Concepts: updates](https://kubernetes.io/docs/reference/using-api/api-concepts/). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E025], [E022], [E015], [E019], [E058]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: OpenAI prompt caching cache writes model generations; DeepSeek legacy aliases replacement model pricing; Z.ai Claude aliases GLM model mapping; Kubernetes resourceVersion conditional update.

## Unverified limits and refresh triggers

- Specific model slugs and version probes remain environment-dependent. This session read documentation but did not query authenticated provider inventories.
- No account-level model-resolution data was fetched. Vendor docs establish possible alias and price behavior, not this account current entitlement.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.

## Capability identity versus availability identity

Keep capability identity separate from availability identity: changing only a quota pool, request ID, log path or credential reference cannot create a stronger rung. Resolve known aliases and native effort before deduplication; retain the harness/backend boundary rather than equating model-family names across hosts.

This is an engineering contract for the proposed implementation, not a claim that quota-pool isolation or cross-harness intelligence equivalence was measured.
