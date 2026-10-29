# F019 / task 042 - Muse Code adapter and session protocol

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Qualify the exact Meta Muse Code executable and make session persistence, output envelopes and workspace isolation explicit.

## Questions addressed

- Resolve the exact Meta Muse Code product, exec JSON envelope and session protocol.
- Verify cancellation, summary mode and resumable state without assuming flags from unrelated Muse CLIs.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The repository has a dedicated Muse adapter and tests, rather than a generic command named Muse. The worker uses headless execution with configured model/effort options.
- Meta documentation provides session-log controls and notes that child execution does not itself create an isolated checkout.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `build_worker_command` L1034-1190; `build_summary_command` L2319-2455
- `skill/plan-and-execute/scripts/muse_provider_self_test.py` (SHA-256 `9466b0aaa0bed367dd57339f5c991ccd0c2123b19f51140d6ece98549b50487a`): `sample_report` L25-39; `worker` L42-43; `summary` L46-47; `test_default_worker_argv_has_no_permission_flags` L50-56
- `skill/plan-and-execute/references/MODEL_ROUTING_MUSE.md` (SHA-256 `648cec38d3ee0e61007208c01122e6095188e7b568ee82faa21aa1cf6a33804b`): `# Muse Code model routing` L1; `## Status and evidence` L5; `## Catalog mapping` L9; `## Worker argv` L21

## External basis

- [E033] [Muse Code configuration](https://dev.meta.ai/docs/muse-code/configuration) - Meta; accessed 2026-10-28.
- [E034] [Extending Muse Code](https://dev.meta.ai/docs/muse-code/extending) - Meta; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Assume the command name establishes product and capabilities | Low maintenance but unsafe when products share a name or versions drift. |
| recommended | Identity/version-qualified protocol with explicit retention | A small compatibility layer preserves the existing optional adapter. |
| rejected | Borrow Codex/Claude flags based on superficial similarity | Creates untested semantics, especially for sessions and permissions. |

## Implementation instructions

1. Add version/help fixtures for Meta Muse Code and reject a same-named unrelated executable without the required command contract.
2. Separate JSONL progress/tool events from the final completion payload. Apply the shared bounded spool and schema validation.
3. Choose and document session-log retention for normal fresh workers; only add --no-session-log when supported and covered by a golden test.
4. Require explicit worktree/read-only controls for isolation. Never fall back from unsupported confinement to trust-workspace or approval bypass silently.
5. Normalize backend/usage identity and map failures through the same availability-versus-semantic distinction as other providers.

## Acceptance tests to implement and run

- [ ] A fixture for an unrelated muse executable is rejected before any task starts.
- [ ] No-session-log and resume options are not combined incompatibly.
- [ ] Two children sharing a checkout cannot be mistaken for isolated parallel writers.
- [ ] Read-only summary and implementation command paths have different tested authority.
- [ ] Large or malformed JSONL cannot cause unbounded memory or false completion.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Keep Muse optional and discover only when selected. Do not load its guide or probe it for every Codex/Claude task.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Live Meta account permissions, model list, usage accounting and actual read-only enforcement remain unverified.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **042** now implements this recommendation; task **043** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
