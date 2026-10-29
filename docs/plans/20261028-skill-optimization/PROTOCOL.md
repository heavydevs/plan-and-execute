# Single implementation protocol

Date: 2026-10-28. This replaces the former research-then-Plan2 execution workflow. Original instructions remain immutable in `REQUEST_ORIGINAL.md` and the historical snapshot; the current amendment supersedes their plan structure only.

## Authority and honest state

`PLAN1_SPEC.json` is the current portable specification. The native `manifest.json` is authoritative during execution; task Markdown and `TODO.md` are generated projections. All 86 tasks start pending. Research readiness is recorded separately in the prepared report index; report existence cannot complete an implementation task. Autostart is false. No authenticated model has been dispatched in this preparation.

The native `plan_review` records a host structural/synthesis check, not an independent model review. The current amendment authorizes research and local replanning; it does not authorize changing installed copies, user-global configuration, committing, pushing, opening PRs, publishing or paid model experiments. Those actions retain the original explicit-consent boundary. Never print environment/profile secrets.

## Per-task workflow

1. Load only `support/check_delivery.py --inputs <ID>`, the linked report and current source targets. Reports contain dated static observations; inspect changed code instead of treating a historical line number as current truth.
2. Preserve already-satisfied invariants. Implement only the missing behavior and regression evidence; do not add a second mechanism merely to satisfy a report. Do not repeat broad research unless a concrete current-version contradiction changes the decision.
3. Complete the bounded internal checkpoints. Add the declared targeted tests under `test/optimization/` and wire new suites into repository checks. These future test files are intentionally absent before implementation.
4. Run the two mapped validation IDs: `P1_TESTS_<ID>` executes the catalog's argv and creates a machine check receipt; `P1_<ID>` validates the actual deliverable and test evidence. The outer resource watcher owns process observation and cancellation. Do not bypass it by approving worker prose.
5. Produce a concise outcome and schema-v2 receipt. Keep incomplete work pending. The orchestrator, not the worker, accepts completion through native controllers.
6. Execute the successor independent maximum-qualified code review in a fresh context, correct findings, and revalidate changed code. The reviewer may propose fixes; a fresh approval after correction must reflect the final input hashes. Never impersonate another model.

## Prepared evidence and changes

Each topic has Markdown plus JSON under `prepared-research/`; `INDEX.json` pins both hashes and E### source IDs. The source register records exact URLs, access dates and reading scope. External documentation is not evidence of this account's quota, authentication, sandbox behavior or model quality. No live cost savings were measured. Public book excerpts/chapters are not represented as full-book study.

A new decision invalidating a report must produce a bounded amendment with source and rationale; preserve its original version in history, update report/index hashes and rerender affected task projections. A source code hash naturally changes when the planned feature is implemented; it is a baseline anchor, not a prohibition on editing that file.

## Future implementation receipt (schema 2)

Required fields are `schema_version: 2`, `task_id`, `kind: implementation`, `status: completed`, `summary` (max1600 chars), `outcome_sha256`, `prepared_inputs` and `changed_artifacts` (nonempty lists of repository-relative path and SHA-256), `checks_sha256`, `acceptance_coverage`, and `limitations` (list).

`prepared_inputs` pins every assigned prepared report. `changed_artifacts` pins actual changed product/test/tooling files, not research reports alone. When the assigned invariant already holds or a review needs no correction, use `changed_artifacts: []`, `no_changes_needed: true`, a concrete `preservation_reason` (40-800 chars), and hashed `preserved_artifacts`; every declared check and acceptance case still must pass. Never force an unrelated code edit merely to create a diff. `acceptance_coverage` contains every catalog AC ID with `result: passed` and file evidence. The outcome Markdown path is fixed by TASK_INPUTS.json. Do not copy raw logs into the receipt.

`run_task_checks.py` creates `implementation/<ID>-checks.json` from the declared catalog argv, actual exit codes and owned log hashes. It fingerprints current code, tests and assigned decision inputs, rejects code mutation during validation, and does not dispatch models or mark a task complete. A missing future test fails rather than passing a placeholder. Review gates pin the predecessor's original receipt and outcome; their own checks run again after corrections. Integration reruns final regressions across the combined product instead of pretending historical per-task passes describe later code automatically.

Review/correction receipts additionally include `reviewer` (actual provider, model, native_effort, model_tier=max, fresh_context=true, session_id, dispatch_evidence and dispatch_sha256), `reviewed_inputs`, `verdict: approved` and `findings` with no unresolved critical/high finding. Dispatch evidence is bounded metadata, not a full transcript. The orchestrator must verify actual provenance: a self-authored JSON file cannot cryptographically prove a model identity.

## Isolation and economics

Read only the selected report, applicable source symbols, tests and dependency receipts. Reports live outside disposable plan state. No periodic model call is needed to poll logs. Record unknown cost as null; compare total attempt, cache, handoff, review and validation cost per independently validated outcome. Prefer deterministic monitoring and bounded evidence. Preserve the root model and the configured provider/fallback boundaries.

## Dependencies and final acceptance

001 is deterministic preflight, not a universal external-review blocker. Code-writing tasks with overlapping source ownership are serialized by dependencies. Reviews remain real acceptance gates. 068 creates reusable provider-switch fixtures and baseline expectations; 070-080 implement the runtime contract, without duplicate ownership.

082-086 integrate changes, correct regressions, validate the actual package file list, check legacy and disabled behavior, and perform final whole-skill review. No task creates Plan2. All twelve original provider-switch acceptance cases survive. The final report states actual test commands, results, unverified Windows/live-provider behavior and costs. Product output and prepared research survive successful cleanup; the user-requested checkpoint is retained.


## Research revision 2

Consume the assigned revision-2 report and normative blueprint before implementation. Sources W-* identify newly inspected primary material; E-* records are historical background. Source counts and checklists are not semantic review evidence.

Keep capability identity separate from availability/quota identity. Do not classify a credential or quota-pool change as more intelligence. Unknown required capability blocks a candidate until a permitted capability check resolves it.

Receipt applicability: a historical receipt proves only its recorded revision. Current acceptance requires current input fingerprints and affected-contract/integration revalidation. Preserve history, never edit old receipts to look fresh.

The initial 4000-byte deterministic handoff and other operational limits are engineering defaults to test, not measured universal optima. Research selects a bounded recommendation; implementation must preserve security/capability floors and demonstrate the assigned counterexamples.
