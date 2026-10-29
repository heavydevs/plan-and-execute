# F013 / task 030 - Claude Code and Claude Agent SDK adapter

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep the Claude CLI adapter thin and version-qualified, with explicit session, schema, permission and usage contracts.

## Questions addressed

- Verify print mode, no-session-persistence, structured schema, tool restrictions and resume flags.
- Measure subscription quota separately from API cash and cache write/read economics.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- build_worker_command uses Claude print mode with disabled session persistence; a subsequent fresh process cannot be assumed to remember the previous attempt.
- The runner has separate worker and summary command builders. A read-only summary must remain a restricted command path rather than a general implementation worker with a polite prompt.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `build_worker_command` L1034-1190; `build_summary_command` L2319-2455
- `skill/plan-and-execute/scripts/provider_self_test.py` (SHA-256 `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd`): `test_codex_output_schema_is_api_compatible` L470-536
- `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md` (SHA-256 `ba6e2fe3334f9204445aaf20ea28fa1675638029b7de568bfcb9068693af999a`): `# Claude Code model routing` L1; `## Current capability map` L5; `## Elevation mechanics (how a route is actually obtained)` L22; `## DIRECT mode` L38

## External basis

- [E015] [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference) - Anthropic; accessed 2026-10-28.
- [E017] [Manage costs effectively](https://code.claude.com/docs/en/costs) - Anthropic; accessed 2026-10-28.
- [E054] [Work with sessions, Agent SDK](https://code.claude.com/docs/en/agent-sdk/sessions) - Anthropic; accessed 2026-10-28.
- [E052] [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) - OpenAI; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Assume all Claude versions share flags and billing | Minimal adapter maintenance but vulnerable to protocol and account changes. |
| recommended | Small versioned contract fixtures and restrictive summary path | Predictable upgrades without rewriting the harness in an SDK. |
| rejected | Migrate everything to Agent SDK for this change | Adds a new dependency/runtime surface without a demonstrated requirement; sessions can be evaluated later. |

## Implementation instructions

1. Add recorded help/version fixtures and a capability map for the exact installed Claude CLI. Probe flags non-generatively and fail visibly on unsupported combinations.
2. Preserve fresh-context defaults. Separate optional resume/session-retention experiments from normal execution and document that conversation persistence does not snapshot source files.
3. Test structured report extraction, schema rejection, malformed envelopes and nonzero statuses separately. A valid JSON shape cannot replace deterministic product validation.
4. Qualify read-only paths with an actual tool allowlist/sandbox boundary and clean environment, including third-party endpoint profiles.
5. Capture available usage fields in native units, retaining null for absent values. Do not equate subscription tokens with API invoices or assume a universal cache rate.

## Acceptance tests to implement and run

- [ ] Default worker argv retains no-session-persistence and existing approved permission behavior.
- [ ] Summary mode cannot write a planted repository file or execute an unapproved mutating tool in a supported test environment.
- [ ] Invalid JSON, missing report fields, quota errors and semantic failures take different paths.
- [ ] A model alias mapped through another endpoint is reported with host and backend identity.
- [ ] Unknown usage is null and no secret environment values enter diagnostics.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Avoid an extra model call for ordinary post-failure summaries. CLI contract tests should use fake processes; authenticated smoke tests require explicit permission and report real cost separately.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Installed CLI version, current account authentication and maximum authorized model are not verified in this session.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **030** now implements this recommendation; task **031** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
