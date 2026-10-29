# F022 / task 048 - Independent validation, evidence packets and failure classification

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Make acceptance depend on pinned deterministic validation evidence and ensure the production prompt exposes the allowed evidence packet.

## Questions addressed

- Trace report normalization, validation checkpoints and deterministic acceptance outside worker claims.
- Check missing evidence-packet path in the concise prompt and stagnation fingerprints.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- Production runner_contract.worker_prompt calls failure_context without the plan directory, so the inspected path does not include the available evidence-packet pointer.
- Worker completion reports, runner validations and resumable validation checkpoints are distinct. Passing report schema checks alone is not product acceptance.

### Read targets and integrity

- `skill/plan-and-execute/scripts/run_isolated.py` (SHA-256 `00ffc3bce6093d63198b910eaad7e8a76f739dd226eb6399c2e6fa54301908df`): `failure_context` L776-811; `validation_checkpoint_fingerprint` L1489-1494; `finish_task_validation` L2045-2149
- `skill/plan-and-execute/scripts/artifact_contract.py` (SHA-256 `477646cf30634e334e5c704a6cbe86e9dea4712f7527f51501c43462cadc08f3`): `_error` L100-101; `concise_line` L104-129; `concise_list` L132-162; `_md` L165-167
- `skill/plan-and-execute/scripts/runner_contract.py` (SHA-256 `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6`): `worker_prompt` L44-80
- `skill/plan-and-execute/references/WORKFLOW.md` (SHA-256 `f95cc605684b7fe58d3c3ab2cd3a3aead456bad851f45746fe26ed771e19892c`): `# Execution workflow` L1; `## Roles` L5; `## Native execution loop` L13; `### 1. Select` L15

## External basis

- [E052] [Structured model outputs](https://developers.openai.com/api/docs/guides/structured-outputs) - OpenAI; accessed 2026-10-28.
- [E053] [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) - OpenAI; accessed 2026-10-28.
- [E007] [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents) - Anthropic; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Trust worker validation declarations | Cheapest apparent path, but it can accept unobserved or stale success. |
| recommended | Pinned independent receipts and task-local evidence pointers | Low token overhead with falsifiable acceptance. |
| rejected | Paste every historical report/log into each retry | Expensive, privacy-sensitive and likely to anchor the next worker on stale diagnosis. |

## Implementation instructions

1. Pass the correct plan directory through the composed prompt path and explicitly permit only the assigned evidence packet and bounded relevant diagnostic artifacts.
2. Pin validation receipts to command, source state, resource-map digest and attempt/job identity. Reuse a successful receipt only when the inputs are still current.
3. Keep failure classification deterministic where evidence is explicit. Record environmental faults and test time limits separately from semantic code failures.
4. Sanitize diagnostic data before truncation and preserve machine-readable evidence references so a new worker can inspect facts without the whole history.
5. Add negative tests where a worker claims success but output behavior, a negative case or an integration contract fails. The runner must keep the task incomplete.

## Acceptance tests to implement and run

- [ ] The composed prompt contains a valid evidence-packet pointer after a failed validation.
- [ ] A changed source/map/command invalidates a previously successful receipt.
- [ ] A valid success JSON with failing tests cannot complete the task.
- [ ] A repeated failure fingerprint is stable under timestamps/PIDs but changes for a genuinely different failure.
- [ ] A resumed completed worker checkpoint validates without unnecessary model redispatch.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Avoid repeating model implementation when only validation remains. Measure tests rerun, stale receipts rejected and incorrect completion prevented; do not treat fewer tests as an optimization by itself.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- A narrow unit suite does not prove end-user quality. Real integration/environment coverage must be declared rather than implied.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **048** now implements this recommendation; task **049** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
