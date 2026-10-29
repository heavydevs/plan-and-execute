# F032 / task 068 - Provider-top switching and evidence-bounded handoff design

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Adopt an opt-in effective-dispatch switch controller with provider-local evidence and a deterministic, evidence-bounded handoff by default.

## Questions addressed

- Compare worker field, native session resume, extra read-only summary and deterministic capsule (source section 4).
- Decide opt-in chain, entry rung, no-op identity, retry budget, phase state and handoff validation from evidence.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The verified baseline has different chain selection in choose_route and availability.select, repeated effective tops and early last-provider exhaustion. The original ten-case fixture replay is preserved as historical baseline evidence.
- Workers are fresh/ephemeral in the normal paths. Starting a new process of the prior provider cannot recover its vanished conversation without deliberately changing persistence policy.
- The concise prompt omits plan_dir in failure_context and excludes prior reports by default. A permitted evidence capsule therefore needs a small explicit isolation-rule amendment, not a hidden transcript injection.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `choose_route` L301-346; `failure_context` L776-811; `design_route_task` L924-931; `ladder_exhausted` L2152-2169
- `skill/plan-and-execute/scripts/availability.py` (SHA-256 `39e4e02663a26a1a3d6324037fef96bbf7d5c28cc2511a89d0431b377fa97c0d`): `select` L116-168
- `skill/plan-and-execute/scripts/routingctl.py` (SHA-256 `f792363c783596aef972925edb9aad5d97b86da43e45a212a69c5a2355a78616`): `lift_tier` L214-220; `route_rungs` L230-242
- `skill/plan-and-execute/scripts/runner_contract.py` (SHA-256 `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6`): `worker_prompt` L44-80
- `skill/plan-and-execute/scripts/assistant_triage.py` (SHA-256 `af9d5a1054aae9c747916a60f3f0c836209f878c1c31638909eedcd28d9109c2`): `Skip` L33-34; `dumps` L37-38; `strict_json` L41-50; `redact` L53-62
- `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` (SHA-256 `72da10bd5e05fd08d213ed29ca649e83fbe23d4f082bf1c3159e87402cbef8cd`): `# Token-efficiency contract` L1; `## Objective` L5; `## 1. Avoid the harness when the harness does not pay for itself` L9; `## 2. Keep useful shared context while it is useful` L15

## External basis

- [E014] [AutoMix: Automatically Mixing Language Models](https://arxiv.org/abs/2310.12963) - Aggarwal et al. / arXiv; accessed 2026-10-28.
- [E012] [FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance](https://arxiv.org/abs/2305.05176) - Chen, Zaharia and Zou / arXiv; accessed 2026-10-28.
- [E038] [Fallbacks and provider failover](https://docs.litellm.ai/docs/proxy/reliability) - LiteLLM; accessed 2026-10-28.
- [E039] [Failover and fallbacks explained](https://openrouter.ai/blog/insights/reliability-failover/) - OpenRouter; accessed 2026-10-28.
- [E054] [Work with sessions, Agent SDK](https://code.claude.com/docs/en/agent-sdk/sessions) - Anthropic; accessed 2026-10-28.
- [E010] [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) - Shinn et al. / arXiv; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.
- [E018] [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) - Anthropic; accessed 2026-10-28.
- [E021] [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) - OpenAI; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Fixed-count fallback with accumulated evidence | No migration cost, but verified waste and reachability defects remain. |
| recommended | Effective dispatch state plus deterministic capsule | No extra model call, bounded context and a testable explanation for every transition. |
| deferred | Nullable worker summary validated against deterministic evidence | Low marginal output cost but unavailable on crashes and can anchor the receiver; evaluate later. |
| rejected | Resume prior session or call another model solely to summarize every failure | Adds retention, privacy and quota cost and still cannot guarantee factual diagnosis. |

## Implementation instructions

1. Keep provider_switch.mode=legacy by default; expose an explicit effective_top mode with strict subkey validation and routing-fingerprint coverage. Version1 full config snapshots must not inherit a new global policy.
2. Freeze the allowed chain for a task phase from the declared policy and override rules. Resolve each candidate through tier lifting, profile/native effort and snapshot before building distinct dispatches. The selected provider is authoritative for both ladder and command.
3. Persist phase/provider-local evidence and an actual-dispatch receipt before recording outcomes. Keep global functional failures/max_attempts separate. No eligible provider is exhausted until it was attempted or excluded with a reason.
4. On semantic or unknown top failure, move to the next qualified provider. Permit at most one documented identical retry for mechanical/budget cases. Environmental, plan_defect and timeout_ceiling never cause capability switching.
5. Reserve enough remaining attempts for at least one dispatch of each remaining eligible provider when the configured budget can do so; otherwise emit a preflight budget warning and explicit budget_exhausted outcome. Never silently increase the user budget.
6. Build a deterministic capsule from pinned subtask state, changed-path summary and validation/evidence references. Sanitize before truncation, mark hypotheses unverified, append after static rules and deterministic evidence, bind it to the next dispatch only.
7. Keep the optional previous-worker summary field as a later measured enhancement behind its own flag. Do not add a paid summary call or native transcript retention by default. Tasks070-081 implement and review the detailed contract.

## Acceptance tests to implement and run

- [ ] Disabled mode reproduces baseline routes and argv without changing existing assertions, except a separately justified empty-tier bug fix.
- [ ] No-op embedded effort and equal strong/max models switch without burning redundant top attempts.
- [ ] Both default claude-to-codex and explicit codex-to-claude max chains reach the last provider before exhaustion.
- [ ] The strong three-provider fixture reaches its third provider within max_attempts=8, or rejects an impossible budget before dispatch.
- [ ] Quota/destination unavailability respects cooldowns and fallback-disabled policy without semantic failure increments.
- [ ] Handoff tests cover secrets, path/command/subtask validation, byte bounds, next-attempt expiry, both prompts and missing reports.
- [ ] Manifest1-4, missing failure_classes, version1 config snapshots, ledger migration, design-phase state and telemetry rollups remain compatible.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

For each task compare total cost of all attempts plus handoff preparation and review, divided by validated success. Deterministic handoff has no inference call but adds bounded receiver input. A useful target is zero avoidable duplicate top dispatches and full allowed-chain reachability, not an invented savings percentage.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Equivalent logical tiers do not prove equal quality across providers. No live model superiority, quota independence, token saving or independent maximum-model review is claimed.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Detailed design boundary and acceptance mapping

**State and authority.** Store a schema-versioned switch state under the task, partitioned by `design` and `implementation`. Each phase records the allowed-chain fingerprint, current provider, provider-local classified outcomes and actual effective dispatch identities. Keep secrets, full argv, environment values and transcripts out of that state. Record the dispatch identity at execution time; do not recompute a past attempt using a newly refreshed catalog. A stale configuration fingerprint requires an explicit reconciliation event, not reinterpretation of old failures.

**Budget rule.** Let B be remaining functional attempts and U the number of eligible providers not yet tried in the phase. When B is at most U, select an untried provider before spending another retry on a tried one. Availability-only failures do not consume B; they have a separate bounded dispatch/probe budget. If B is smaller than U at intake, warn or reject the requested coverage guarantee rather than silently altering `max_attempts`. At runtime, policy changes or new unavailability can reduce coverage; report those reasons explicitly. Preserve safety blocks for plan defects and hard time limits. Mechanical/budget's optional one repeat is subordinate to the remaining-provider reservation. Phase bookkeeping must not reset the shared task-wide budget implicitly.

**Handoff data contract.** Proposed capsule limit: 4,000 UTF-8 bytes, configurable within a small validated range; this is an engineering budget to test, not a tokenizer guarantee. Include schema/attempt/phase IDs, from/to identity hashes, reason, completed subtask IDs, validated changed-file references, evidence packet and last-validation references, and optional sanitized unverified hypotheses. Check paths stay in the repository/owned artifacts, commands correspond to actual recorded validation and subtask IDs exist. Omit unknown facts rather than guessing. The receiving model is instructed to verify hypotheses independently. The capsule is data and cannot override tools, permissions, route or acceptance. Bind it to a concrete next dispatch ID so an availability retry does not consume it prematurely or a later unrelated attempt replay it.

**Crash and reset.** Missing/invalid worker output still permits the deterministic evidence-only capsule. Reset must explicitly state whether it starts a new semantic retry epoch; retain historical events for audit and never clear cooldowns merely to bypass quota. Restart after crash reconciles a recorded dispatch without double-counting an outcome. Ambiguous external side effects require reconciliation before another execution.

**Why not native resume?** It is same-provider state, changes transcript retention and can preserve anchoring. It also does not help after the old provider is unavailable. A separate paid summary has similar evidence limits with extra latency. The deterministic option is therefore the initial default for the opt-in switching feature. An optional nullable worker summary can be evaluated against the capsule-only arm later, without weakening schema or evidence checks.

**Acceptance ownership.** Original AC01 belongs to the legacy replay harness and configuration gate; AC02-07 to effective identity, per-provider state, budget reservation and coherent dispatch; AC08 to availability; AC09-10 to sanitation and capsule lifecycle; AC11 to migration/reset/phase fixtures; AC12 to metadata-only telemetry. Preserve all twelve original cases in the implementation matrix. A research report is not a passing acceptance test.

## Task handoff

Task **068** now implements this recommendation; task **069** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
