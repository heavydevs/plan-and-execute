# F015 / task 034 - Antigravity and legacy Gemini adapter

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Make Antigravity model, effort, quota and permission discovery authoritative for that host; keep Gemini legacy compatibility explicitly separate.

## Questions addressed

- Check agy models, embedded-effort slugs, conversation persistence and per-family quotas.
- Distinguish current Antigravity behavior from legacy Gemini; document CLI/help/model-list discrepancies.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The adapter suppresses a separate effort argument for recognized embedded-effort model slugs. A logical effort increment can therefore leave the actual command unchanged.
- The configuration and workload modules can represent different Antigravity profiles and quota pools. Current docs expose a wider effort vocabulary with model-dependent support, so a universal high-only statement is not reliable.
- The runner uses a fresh prompt invocation without a continuation ID; the exact conversation retention behavior is a version-specific operational question.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `build_worker_command` L1034-1190
- `skill/plan-and-execute/scripts/routing_config.py` (SHA-256 `4c21ed17b26062511023e151edd60f56eb68219129418303f17ddc2b26e9d4e4`): `embedded_effort_model` L106-109
- `skill/plan-and-execute/scripts/workload_routing.py` (SHA-256 `1a387675edbf3ef9e9b58dbc2fdcfa072173329ca864a4d1577ad7ca369147b1`): `antigravity_preset` L193-214
- `skill/plan-and-execute/references/INSTALLATION.md` (SHA-256 `679e881535934274a60615aaa36befbf30bc15ae6302dc66dceb6a7a8d45b2ff`): `# Install Plan and Execute for Claude Code, Codex and Antigravity` L1; `## Activation mode` L9; `## Recommended: install with npx` L23; `# Claude and Codex for every project; selective auto-routing` L63

## External basis

- [E022] [Antigravity CLI reference](https://antigravity.google/docs/cli/reference/) - Google; accessed 2026-10-28.
- [E023] [Headless mode](https://antigravity.google/docs/cli/headless/) - Google; accessed 2026-10-28.
- [E024] [Permissions](https://antigravity.google/docs/permissions/) - Google; accessed 2026-10-28.
- [E025] [Models](https://antigravity.google/docs/models/) - Google; accessed 2026-10-28.
- [E026] [Plans](https://antigravity.google/docs/plans) - Google; accessed 2026-10-28.
- [E027] [Usage command](https://antigravity.google/docs/cli/commands/usage) - Google; accessed 2026-10-28.
- [E028] [Gemini CLI migration](https://antigravity.google/docs/cli/gcli-migration/) - Google; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Hardcode current model names and a universal effort cap | Cheap initially, but brittle and misleading across hosted models. |
| recommended | Observed capability intersection and explicit pools | Small probe/cache cost and accurate host-specific decisions. |
| rejected | Always prefer hosted Opus or Flash irrespective of task | Can under-route difficult work or spend a scarce pool without evidence. |

## Implementation instructions

1. Persist normalized agy version/help/models/usage observations with timestamp. Intersect CLI-supported effort with each model's advertised capability; do not assume max in help applies to every slug.
2. Derive effective dispatch from resolved slug plus native effort. Collapse no-op transitions and preserve unsupported capability as an exclusion reason.
3. Map quota pools from explicit account evidence or configuration, not a universal Gemini-versus-Claude assumption. Prefer a suitable alternate pool only within the permitted chain.
4. Pin a verified read-only observer path. Approval skipping must not be mistaken for a sandbox; on unsupported versions disable advisory dispatch rather than widen authority.
5. Keep the legacy Gemini adapter behind its own contract and deprecation note. Do not auto-migrate user configuration or silently substitute a different CLI.

## Acceptance tests to implement and run

- [ ] An embedded high slug receives no redundant effort flag and is not retried as a supposedly stronger identical dispatch.
- [ ] A model with lower effort support cannot satisfy a higher required route without explicit qualification.
- [ ] Separate configured pools have separate cooldowns; shared pools remain shared.
- [ ] Usage discovery failure leaves quota unknown and does not consume semantic attempts.
- [ ] Headless parser, conversation metadata and read-only restrictions have version-pinned fixtures.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Prefer deterministic monitoring; use the cheapest qualified observer according to actual account economics. This research does not establish a universal cheapest Flash model or identical native/hosted Opus capability.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Actual quota independence, model availability, conversation persistence and highest effective effort require the user's installed CLI/account.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **034** now implements this recommendation; task **035** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
