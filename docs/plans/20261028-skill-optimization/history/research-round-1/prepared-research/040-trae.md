# F018 / task 040 - Trae Agent adapter

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Keep the ByteDance Trae Agent adapter distinct from the IDE, and make trajectories an owned, protected diagnostic artifact.

## Questions addressed

- Distinguish the configured Trae Agent CLI from the TRAE IDE or another CLI product.
- Verify trajectory handling, provider configuration, secret routing and failure reporting.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The adapter invokes trae-cli run with a working directory and trajectory output path, plus optional underlying provider/model choices.
- The official Trae Agent repository describes an open-source agent and provider configuration. It does not justify borrowing flags or session behavior from the TRAE IDE.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `build_worker_command` L1034-1190; `parse_provider_report` L1412-1425
- `skill/plan-and-execute/scripts/provider_self_test.py` (SHA-256 `a38f2da1c85a09e431c67333a2a29ed2cef8dc5bf27d5ac62d4fa0c82268e1dd`): `sample_route` L20-26; `sample_report` L29-43; `test_default_provider_policy` L46-60; `test_worker_command_adapters` L63-143

## External basis

- [E032] [Trae Agent README and CLI examples](https://github.com/bytedance/trae-agent) - ByteDance; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.
- [E042] [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) - Microsoft; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Treat trajectory files as ordinary harmless logs | Low immediate effort, but interactions and configuration can contain sensitive data. |
| recommended | Thin adapter plus owned redacted diagnostic lifecycle | Uses existing resource registry and avoids copying entire trajectories. |
| rejected | Replace all providers with the Trae runtime | Unnecessary migration that increases dependencies and changes tested execution semantics. |

## Implementation instructions

1. Pin documented Trae Agent CLI/version fixtures and normalize its final output independently of provider-specific message formats.
2. Record both harness and actual model-provider identity so rate limits, capabilities and costs are attributed to the backend rather than the CLI name.
3. Register trajectory files under the task/job ownership and retention policy. Exclude them from packages and worker prompts unless a bounded sanitized excerpt is explicitly authorized.
4. Resolve secrets from allowed environment names at dispatch time; do not copy configuration values into manifests, evidence or model prompts.
5. Share cancellation and bounded process-output infrastructure with other adapters. Keep any Docker isolation choice explicit and version-qualified.

## Acceptance tests to implement and run

- [ ] Golden command fixtures distinguish Trae Agent from unrelated executables.
- [ ] An invalid or missing terminal output cannot be replaced by a plausible trajectory message.
- [ ] A seeded credential in a trajectory is not included in model-facing evidence or publication artifacts.
- [ ] Quota failures are keyed to the configured backend/profile, not every Trae execution.
- [ ] Cleanup preserves active trajectory evidence and removes only registered stale artifacts.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Do not pay to summarize an entire trajectory by default. A bounded deterministic failure packet should be sufficient for known classes; ambiguous diagnosis remains opt-in.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Underlying provider behavior, Docker confinement and installed Trae CLI version were not executed here.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **040** now implements this recommendation; task **041** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
