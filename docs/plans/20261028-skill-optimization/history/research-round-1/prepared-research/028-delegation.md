# F012 / task 028 - Fresh workers, delegation gates and prompt-cache boundaries

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Make delegation evidence-based and context-bounded; retain fresh cross-provider workers and do not enable transcript resumption by default.

## Questions addressed

- Compare isolation benefits with coordination, cache writes and repeated repository exploration.
- Keep root route fixed; separate native session resume from cross-provider handoff.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- run_concise composes multiple runtime contracts, so tests of run_isolated alone do not cover the production prompt.
- The current runner launches fresh workers and receives bounded task artifacts. Its run_process/pump_stream path accumulates captured output; large outputs require a bounded capture contract independent of the full disk log.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_concise.py` (SHA-256 `495d986c1582ce5ed432fe304d995d244159e2168d2b4aafa6185b13ed79aba8`): file-level contract
- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `worker_prompt` L711-749; `pump_stream` L1193-1211; `run_process` L1214-1317
- `skill/plan-and-execute/scripts/runner_contract.py` (SHA-256 `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6`): `install_runner_contract` L36-143; `worker_prompt` L44-80
- `skill/plan-and-execute/references/DELEGATION.md` (SHA-256 `40cd1984a718285408ab63a0fe97242d0c2eef675a90df3f9ef1b0109d28bb99`): `# Delegation policy and role contracts` L1; `## Request` L11; `## Rules, in order` L15; `## Token accounting` L24

## External basis

- [E016] [Create custom subagents](https://code.claude.com/docs/en/sub-agents) - Anthropic; accessed 2026-10-28.
- [E054] [Work with sessions, Agent SDK](https://code.claude.com/docs/en/agent-sdk/sessions) - Anthropic; accessed 2026-10-28.
- [E021] [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) - OpenAI; accessed 2026-10-28.
- [E018] [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) - Anthropic; accessed 2026-10-28.
- [E041] [subprocess module](https://docs.python.org/3/library/subprocess.html) - Python Software Foundation; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Fresh worker for every small step | Strong separation but needless startup, repeated reads and coordination. |
| recommended | Selective isolation plus bounded output and artifact handoff | Preserves resumability and reduces unrelated context with measurable overhead. |
| rejected | Automatically resume all old sessions across retries | Retains stale/incorrect context and transcripts, and cannot transparently cross providers. |

## Implementation instructions

1. Add deterministic delegation receipts recording role, read/write scope, capability floor, estimated coordination cost and reason for keeping work at root.
2. Use fresh workers for independent contexts or capability gaps. Keep small cohesive work local and prevent concurrent writers with overlapping scopes unless an explicit integration strategy exists.
3. Implement a bounded stream spool that drains stdout and stderr concurrently, preserves full owned logs on disk, and retains only the final structured envelope and bounded diagnostic windows in memory.
4. Keep worker prompt static prefixes stable in both raw and composed entrypoints. Use referenced artifacts rather than historical chat messages for cross-provider continuity.
5. Treat same-provider session resume as an opt-in future experiment with retention and cache accounting, not a hidden fallback that changes fresh-context semantics.

## Acceptance tests to implement and run

- [ ] A noisy fake CLI emits many megabytes without proportional memory growth or pipe deadlock.
- [ ] A final structured report remains recoverable after long tool output; missing or truncated envelopes fail visibly.
- [ ] Two delegated writers cannot silently claim the same source scope.
- [ ] Above-floor work cannot be retained on an underqualified worker merely to avoid coordination cost.
- [ ] Prefix hashes match across tasks for raw and production entrypoints.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Account for startup, input, output, cache writes/reads and reviewer calls. Stable prompt text improves eligibility but is not proof of a cache hit or lower subscription usage.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No native subagent dispatch exists in this environment; this report does not claim an independent worker or measured cache hit.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **028** now implements this recommendation; task **029** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
