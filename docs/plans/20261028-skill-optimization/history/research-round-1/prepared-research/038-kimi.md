# F017 / task 038 - Kimi Code CLI adapter

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Add version-aware Kimi command contracts before changing flags: the current and legacy documentation describe materially different non-interactive modes.

## Questions addressed

- Verify print mode, sessions, automatic context compaction and schema/report extraction.
- Check accounting, interruption and permission boundaries against pinned upstream code.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The existing Kimi worker appends a configured permission flag and --prompt. The current official command reference says --prompt cannot be combined with --yolo, --auto or --plan.
- The legacy reference instead documents --print and its own non-interactive semantics. This is a documentation/source incompatibility risk, not a reproduced failure of an installed CLI in this environment.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `build_worker_command` L1034-1190; `parse_provider_report` L1412-1425
- `skill/plan-and-execute/scripts/provider_self_test.py` (SHA-256 `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd`): `sample_route` L20-26; `sample_report` L29-43; `test_default_provider_policy` L46-60; `test_worker_command_adapters` L63-143

## External basis

- [E030] [kimi command, current documentation](https://moonshotai.github.io/kimi-code/en/reference/kimi-command) - Moonshot AI; accessed 2026-10-28.
- [E031] [kimi command, legacy documentation](https://moonshotai.github.io/kimi-cli/en/reference/kimi-command.html) - Moonshot AI; accessed 2026-10-28.
- [E041] [subprocess module](https://docs.python.org/3/library/subprocess.html) - Python Software Foundation; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Reuse one permission/prompt combination | May work on a pinned release but is not portable across documented protocol changes. |
| recommended | Version-qualified minimal adapter variants | Small targeted maintenance cost and an explicit unsupported-version result. |
| rejected | Blindly add --print because an older page mentions it | Can fix one version while breaking another; unsupported changes are not evidence-based. |

## Implementation instructions

1. Introduce bounded version/help discovery and explicit supported protocol variants. Never combine flags from the old and new references.
2. For a current variant, construct the documented non-interactive invocation and handle its permission boundary explicitly; for a legacy variant, retain only the tested compatible syntax.
3. Normalize stream-json messages into terminal outcome, bounded report and usage. Intermediate text, context-compaction events and tool output are not a completion artifact.
4. Treat session reuse as opt-in with documented storage/retention; default cross-provider continuation remains an evidence capsule and the worktree.
5. Add a diagnostic that identifies unknown versions without silently switching to unrestricted operation. Preserve user configuration and never run an automatic upgrade.

## Acceptance tests to implement and run

- [ ] Current fixtures reject --prompt combined with obsolete or mutually exclusive permission flags.
- [ ] Legacy fixtures keep their documented print-mode syntax instead of receiving current-only flags.
- [ ] A missing terminal report, malformed JSONL or interrupted stream cannot pass acceptance.
- [ ] Budget, transient and permanent errors are normalized only when the version contract establishes their meaning.
- [ ] Session identifiers and logs never introduce secrets into a shared handoff.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Version/help probes are deterministic and cached. Avoid paid calls to discover a syntax error; use fixtures before an explicitly authorized live smoke test.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No installed Kimi executable was run, so actual compatibility must be confirmed with its version/help and one bounded authorized test.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **038** now implements this recommendation; task **039** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
