# F009 / task 022 - Provider chains, cooldowns, quotas and availability ledgers

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep availability as a separate bounded state machine, with stable provider/model/quota-pool identity and no functional-failure inflation.

## Questions addressed

- Trace declared versus escalated chains and quota_pool/model cooldown identities.
- Preserve exit 75 and zero functional-failure increments for availability faults.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- availability.read accepts a bounded version1 ledger with cooldowns, per-phase state and compact events; unavailable records categorized failures rather than raw model output.
- availability.select fingerprints route inputs, derives a chain and applies visited/cooldown/CLI checks. The current fixed failure slot and escalated-tier chain must not leak into the new coherent switching policy.
- workload_routing identity and cooldown keys already distinguish provider profiles and pools; reuse them instead of adding a second incompatible identity scheme.

### Read targets and integrity

- `skill/plan-and-execute/scripts/availability.py` (SHA-256 `39e4e02663a26a1a3d6324037fef96bbf7d5c28cc2511a89d0431b377fa97c0d`): `read` L63-87; `unavailable` L95-113; `select` L116-168
- `skill/plan-and-execute/scripts/routing_config.py` (SHA-256 `4c21ed17b26062511023e151edd60f56eb68219129418303f17ddc2b26e9d4e4`): `ConfigError` L45-46; `merge` L49-53; `global_path` L56-63; `read` L66-81
- `skill/plan-and-execute/scripts/workload_routing.py` (SHA-256 `1a387675edbf3ef9e9b58dbc2fdcfa072173329ca864a4d1577ad7ca369147b1`): `identity` L86-88; `cooldown_keys` L106-109

## External basis

- [E038] [Fallbacks and provider failover](https://docs.litellm.ai/docs/proxy/reliability) - LiteLLM; accessed 2026-10-28.
- [E039] [Failover and fallbacks explained](https://openrouter.ai/blog/insights/reliability-failover/) - OpenRouter; accessed 2026-10-28.
- [E040] [Timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - Amazon Builders Library; accessed 2026-10-28.
- [E027] [Usage command](https://antigravity.google/docs/cli/commands/usage) - Google; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Treat every nonzero result as a failed implementation | Simple but burns semantic attempts on quota and missing tools. |
| recommended | Separate availability ledger with explicit intent | Reuses existing primitives and makes routing decisions reproducible. |
| rejected | Delegate availability decisions to a monitoring LLM | Adds cost to a deterministic decision and risks ignoring policy or cooldown state. |

## Implementation instructions

1. Specify a stable candidate identity containing host, backend profile, resolved model and quota pool, with null for unknown metadata. Never store endpoint credentials.
2. Preserve exit75 when no allowed candidate is currently available. Bound probes and attempts per run; honor cooldown before consulting a paid model.
3. Add an availability-intent contract for the future switch controller: candidate order and effective rung are explicit; the selector must not secretly rebuild a different semantic chain.
4. Fingerprint every option that changes candidate construction, including phase and switch configuration. Keep version1 ledgers readable and discard only stale cached intent, not useful cooldowns.
5. Differentiate missing executable, authentication, quota, transient capacity and invalid model. An invalid model triggers bounded catalog repair or a plan defect, not unlimited provider cycling.

## Acceptance tests to implement and run

- [ ] Quota in one configured pool does not block another pool unless the configuration explicitly shares it.
- [ ] Availability failures leave functional failure counts and semantic ladder evidence unchanged.
- [ ] Fallback-disabled and CLI-pinned cases never widen the allowed chain.
- [ ] A changed route fingerprint invalidates cached intent while retaining unrelated valid cooldowns.
- [ ] Every eligible unavailable candidate yields a bounded, redacted reason; all-unavailable returns75 without a spin loop.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

No model call is needed to classify explicit quota/auth/CLI failures. Measure avoided paid redispatches and time to eligible fallback; do not count unknown quota as free capacity.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Provider error strings and quota grouping can change. Live account discovery is unverified here and must be stored as dated evidence.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **022** now implements this recommendation; task **023** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
