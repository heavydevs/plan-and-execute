# F016 / task 036 - Qwen Code headless adapter

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Treat Qwen headless JSON, budgets and permissions as its own tested protocol, not a Claude-compatible shell command.

## Questions addressed

- Inspect Qwen headless JSON, approvals, safe read-only execution and session persistence.
- Compare budget, cancellation and resume contracts without assuming Claude-compatible flags.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The Qwen adapter currently constructs a headless invocation with configured approval/safe-mode controls and a report schema.
- Provider documentation distinguishes JSON/stream output, session persistence and budget exhaustion; those distinctions must survive normalization in the shared runner.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `build_worker_command` L1034-1190; `run_process` L1214-1317; `parse_provider_report` L1412-1425
- `skill/plan-and-execute/scripts/provider_self_test.py` (SHA-256 `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd`): `sample_route` L20-26; `sample_report` L29-43; `test_default_provider_policy` L46-60; `test_worker_command_adapters` L63-143

## External basis

- [E029] [Headless mode](https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/) - Qwen Code; accessed 2026-10-28.
- [E041] [subprocess module](https://docs.python.org/3/library/subprocess.html) - Python Software Foundation; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | One command template for all versions | Low code volume but hides incompatible output and permission changes. |
| recommended | Small Qwen-specific contract and shared safe process infrastructure | Reuses common safety while respecting vendor semantics. |
| rejected | Parse the last arbitrary JSON object as success | May accept a tool event or partial output that never satisfied the task. |

## Implementation instructions

1. Add version/help fixtures for supported Qwen CLI releases and explicit format selection. Keep JSON-array output and streaming JSONL parsing separate.
2. Normalize terminal result, tool activity, budget exhaustion, quota and transport errors without treating any intermediate assistant message as completion.
3. Qualify read-only operation with supported tool exclusions and sandbox controls. Yolo/approval automation alone must not authorize a supposedly read-only observer.
4. Capture resumable session identifiers only if explicitly enabled and retention is documented. Otherwise keep fresh-worker behavior and artifact handoff.
5. Apply the shared bounded output spool and process-tree cancellation contract rather than maintaining a second unbounded capture implementation.

## Acceptance tests to implement and run

- [ ] Replay JSON and JSONL fixtures with interleaved tool messages, malformed records and missing terminal results.
- [ ] Budget/turn exhaustion is recorded separately from semantic failure and transient availability.
- [ ] A read-only fake/qualified command cannot select shell/write/edit tools outside the allowlist.
- [ ] Large output is drained without deadlock; cancellation stops owned descendants.
- [ ] Unsupported schema or sandbox flags fail closed with an actionable version reason.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Use local fixtures for routine protocol regression and only bounded authorized live smoke tests for upgrades. No extra diagnostic model is needed for known exit/error classes.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- The installed Qwen release and its actual exit-code behavior were not exercised. Published budget codes must be pinned before becoming authoritative classifications.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **036** now implements this recommendation; task **037** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
