# 022 - Availability: research revision 2

Date: 2026-10-28. Feature: `F009`. Implementation TODO `022`; independent review TODO `023`. Product baseline: `0.11.0` / tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Prepared design evidence, not implemented code. Implementation and independent review remain pending.**

## Recommended direction

Use one coherent allowed-provider chain and a bounded availability policy with explicit quota scopes, combined retry budgets and non-secret route fingerprints.

This is a conditional engineering recommendation for this repository, not a proof of a global optimum or a measured saving on the user's workload.

## Change from the previous report

Beyond cooldown correctness, the revision includes hidden SDK/CLI retry multiplication, privacy-preserving fallback constraints and quota observations that expire independently of capability evidence.

The previous report is retained under `docs/plans/20261028-skill-optimization/history/research-round-1/prepared-research/` for audit. New W-prefixed sources below are the current-round evidence; old E-prefixed sources remain background.

## Questions and repository evidence

- Trace declared versus escalated chains and quota_pool/model cooldown identities.
- Preserve exit 75 and zero functional-failure increments for availability faults.

**Baseline observations:**
- availability.read accepts a bounded version1 ledger with cooldowns, per-phase state and compact events; unavailable records categorized failures rather than raw model output.
- availability.select fingerprints route inputs, derives a chain and applies visited/cooldown/CLI checks. The current fixed failure slot and escalated-tier chain must not leak into the new coherent switching policy.
- workload_routing identity and cooldown keys already distinguish provider profiles and pools; reuse them instead of adding a second incompatible identity scheme.

All listed file hashes matched the preserved 0.11.0 source in this revision. This is integrity checking, not a second full code audit.

| Code anchor | SHA-256 | Selected symbols / location |
|---|---|---|
| `skill/plan-and-execute/scripts/availability.py` | `39e4e02663a26a1a3d6324037fef96bbf7d5c28cc2511a89d0431b377fa97c0d` | read:63; unavailable:95; select:116 |
| `skill/plan-and-execute/scripts/routing_config.py` | `4c21ed17b26062511023e151edd60f56eb68219129418303f17ddc2b26e9d4e4` | ConfigError:45; merge:49; global_path:56; read:66 |
| `skill/plan-and-execute/scripts/workload_routing.py` | `1a387675edbf3ef9e9b58dbc2fdcfa072173329ca864a4d1577ad7ca369147b1` | identity:86; cooldown_keys:106 |

## Deeper analysis and competing approaches

### 1. Design analysis

Availability is not a capability verdict. A rejected request may consume no useful attempt, while an interrupted stateful worker may already have edited files. Record availability events and functional outcomes separately, and reconcile uncertain side effects before launching a substitute. Do not reduce a provider slot from the total number of all historical failures.

### 2. Design analysis

Use a chain selected by an explicit stable policy and carry the same candidate identity from ladder selection into dispatch. A recalculation at the escalated tier must either be forbidden in the new mode or be a named, tested reordering event. Account, backend, model and quota-pool identity should be separate non-secret fields; cooldown one observed scope without disabling unrelated pools.

### 3. Design analysis

Backoff needs jitter, a maximum wait and a global retry budget that includes SDK or CLI automatic retries. Otherwise a nominal eight-attempt task can perform many more API attempts, exhaust a subscription and keep emitting heartbeats without progress. Record opaque internal attempt counts as unknown rather than reporting only runner invocations as total model requests.

### 4. Design analysis

Fallback must preserve confidentiality, permitted provider lists, required tool/schema capabilities and spending consent. A cheaper or available provider is not eligible if it violates one of these constraints. Exhausted eligible availability should pause with a persisted next action; it must neither silently add a provider nor call the most expensive route indefinitely.

The analysis above is a repository design synthesis. The linked publications establish capabilities or bounded empirical observations, not this skill's future measured performance. Exact account behavior and installed-version compatibility remain implementation-time checks.

| Alternative | Benefit | Cost / failure risk | Disposition |
|---|---|---|---|
| One provider-wide cooldown | Simple | Blocks independent account/model pools | Reject when finer evidence exists |
| Retry every layer independently | Masks transient errors | Multiplicative spend and latency | Reject |
| Scoped ledger plus coherent chain and total budget | Predictable recovery | More explicit state and migrations | Recommended |
| Gateway-managed routing replaces runner policy | Central operations | Can hide backend changes and side effects | Optional adapter only with observable contracts |

## Ownership and scope boundary

TODO 022 implements the availability contract and backward-compatible selector seam. The opt-in top-switch controller is integrated only by 074; disabled behavior must remain unchanged.

Implementation may preserve an already-satisfied invariant with a regression test and a documented no-change rationale; do not add code solely to make every recommendation produce a diff.

## Implementation instructions

1. Specify a stable candidate identity containing host, backend profile, resolved model and quota pool, with null for unknown metadata. Never store endpoint credentials.
2. Preserve exit75 when no allowed candidate is currently available. Bound probes and attempts per run; honor cooldown before consulting a paid model.
3. Add an availability-intent contract for the future switch controller: candidate order and effective rung are explicit; the selector must not secretly rebuild a different semantic chain.
4. Fingerprint every option that changes candidate construction, including phase and switch configuration. Keep version1 ledgers readable and discard only stale cached intent, not useful cooldowns.
5. Differentiate missing executable, authentication, quota, transient capacity and invalid model. An invalid model triggers bounded catalog repair or a plan defect, not unlimited provider cycling.
6. Track quota scope and observation expiry independently from functional failure evidence and provider capability.
7. Document and cap the combined runner, CLI and SDK retry budget; report unobservable internal retries as unknown.
8. Include allowed-provider, privacy, workload, snapshot and effective-routing settings in the availability fingerprint.

## Acceptance and counterexamples

- Quota in one configured pool does not block another pool unless the configuration explicitly shares it.
- Availability failures leave functional failure counts and semantic ladder evidence unchanged.
- Fallback-disabled and CLI-pinned cases never widen the allowed chain.
- A changed route fingerprint invalidates cached intent while retaining unrelated valid cooldowns.
- Every eligible unavailable candidate yields a bounded, redacted reason; all-unavailable returns75 without a spin loop.
- Quota exhaustion in one configured pool leaves another observed-independent pool eligible.
- A fallback that violates required capabilities or data policy is rejected with a reason.
- SDK retry fixtures cannot multiply an unbounded runner wait.
- Availability pauses preserve subtasks without adding a functional failure.

## Cost, latency and quality decision

Compare wall time and all paid requests per validated task, including failed and hidden retries. Quota remaining and API cash cost are separate constraints, never silently converted into one numeric price.

Compare total cost per independently validated outcome against the current implementation and a simpler qualified single-worker baseline. Count failed attempts, reviews, cache writes/reads, advisory calls and tool/runtime overhead in their native units. Unknown prices, quotas or usage remain unknown, not zero. Preserve capability and security floors; no automatic rollout follows from fixture replay alone.

## Evidence used in this revision

- [W-LITELLM] LiteLLM, [Reliability and fallbacks](https://docs.litellm.ai/docs/proxy/reliability). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-RETRY-LAYERS] LiteLLM, [Router retries and SDK retries](https://docs.litellm.ai/docs/routing). Accessed 2026-10-28. Reading scope: Relevant retry/cooldown documentation excerpts inspected; no proxy deployment or authenticated test. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OPENROUTER] OpenRouter, [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-OVERLOAD] Google SRE Book, [Handling overload](https://sre.google/sre-book/handling-overload/). Accessed 2026-10-28. Reading scope: Public chapter retry/load-control sections inspected; this is distributed-system evidence adapted to the runner. Public source reading is not an independent code review or reproduction of vendor experiments.
- [W-AGY-USAGE] Google, [Usage command](https://antigravity.google/docs/cli/commands/usage). Accessed 2026-10-28. Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

Prior-round context: [E038], [E039], [E040], [E027]. See `SOURCE_REGISTER.md` for records; these were not all independently refreshed.

Search themes inspected in this round: LiteLLM retries max_retries num_retries cooldown routing; OpenRouter provider selection require parameters data collection fallback; Google SRE overload retry budget; Antigravity usage quota model.

## Unverified limits and refresh triggers

- Provider error strings and quota grouping can change. Live account discovery is unverified here and must be stored as dated evidence.
- The independence of a user account quota pool is not established by a public model menu. Scope comes from verified account metadata or explicit configuration with provenance.

No authenticated provider invocation, live quota/cost benchmark, independent model review, or Windows runtime test was performed in this research revision.

Refresh only evidence contradicted by the installed CLI, selected account/billing plan or changed code contract. Unknown required capability blocks that candidate; it does not justify widening permissions.

## Capability identity versus availability identity

Keep capability identity separate from availability identity: changing only a quota pool, request ID, log path or credential reference cannot create a stronger rung. Resolve known aliases and native effort before deduplication; retain the harness/backend boundary rather than equating model-family names across hosts.

This is an engineering contract for the proposed implementation, not a claim that quota-pool isolation or cross-harness intelligence equivalence was measured.
