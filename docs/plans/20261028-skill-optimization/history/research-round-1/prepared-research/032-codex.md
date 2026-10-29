# F014 / task 032 - Codex CLI, Agent SDK and schema adaptation

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Validate Codex as an ephemeral execution protocol with explicit schema and sandbox adaptation; do not infer supported flags from model names.

## Questions addressed

- Verify ephemeral runs, exec resume/fork, required nullable fields and current sandbox flags.
- Compare native compaction with short artifact handoffs using pinned CLI evidence.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The Codex worker uses exec and ephemeral mode. The completion schema adapter makes optional fields required-nullable for the supported structured-output contract.
- run_concise modifies the effective worker prompt and therefore requires composed-entrypoint tests, not only a raw argv golden.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `codex_output_schema` L650-676; `build_worker_command` L1034-1190; `parse_provider_report` L1412-1425
- `skill/plan-and-execute/scripts/provider_self_test.py` (SHA-256 `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd`): `sample_route` L20-26; `sample_report` L29-43; `test_default_provider_policy` L46-60; `test_worker_command_adapters` L63-143
- `skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md` (SHA-256 `3cde22d4a24a081052aebfd7d992c8d1c3e4577745aa6f8ea324a7460f280024`): `# Codex model routing` L1; `## Current capability map` L5; `## Elevation mechanics (how a route is actually obtained)` L22; `## DIRECT mode` L37

## External basis

- [E019] [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) - OpenAI; accessed 2026-10-28.
- [E020] [Security](https://learn.chatgpt.com/docs/security) - OpenAI; accessed 2026-10-28.
- [E052] [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) - OpenAI; accessed 2026-10-28.
- [E021] [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) - OpenAI; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Trust a successful codex process and its narrative | Low validation overhead but cannot prove user acceptance. |
| recommended | Versioned CLI/schema fixtures plus independent checks | Small maintenance cost and clear protocol boundaries. |
| rejected | Implicit session continuation for every retry | Changes retention/isolation and can reintroduce unrelated history without measured benefit. |

## Implementation instructions

1. Record CLI version/help and model-discovery evidence without starting a paid task; select tested capability branches for exec, structured output and sandbox flags.
2. Maintain a schema transformation test for nested objects, required nullable fields, additionalProperties and invalid outputs. Refusal or incomplete output is not a passing task.
3. Keep ephemeral mode for normal cross-task isolation. Same-provider resume/fork is a separate opt-in contract, never a way to transfer private reasoning state to another provider.
4. Use read-only sandbox for observation/review where supported and verify that output/log paths can still be written only in owned locations.
5. Parse JSONL events incrementally and preserve the final report independently of progress text. Link deterministic validation evidence through the production prompt.

## Acceptance tests to implement and run

- [ ] Schema fixtures remain accepted by the adapter without weakening additionalProperties checks.
- [ ] Ephemeral default argv and composed static prefix remain stable.
- [ ] Malformed events, partial final JSON, a nonzero exit and a valid blocked report remain distinguishable.
- [ ] An unsupported sandbox/effort flag fails preflight instead of falling back to unrestricted execution.
- [ ] Cache and cost records distinguish reported usage from estimates and do not import outdated no-write-cost assumptions.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure accepted outcomes and input/output/cache units. Do not copy API billing rules into subscription estimates without evidence for the actual host route.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No real Codex invocation or sandbox escape test was executed; fake CLI contract tests cannot certify provider service behavior.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **032** now implements this recommendation; task **033** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
