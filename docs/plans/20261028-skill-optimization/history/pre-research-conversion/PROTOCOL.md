# Plan 1 execution protocol

Date: 2026-10-28. Baseline version: 0.11.0. Remote source commit: `193fefd`.
Local backup commit: `6e6ba53`; both have tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.
The local branch is `feat/skill-study-and-provider-switch`, derived from the restored local `main`.

## Scope and authority

The attachment is preserved byte-for-byte as the control workspace's `REQUEST.md`.
Its outer request asks for a first plan whose product is a second implementation plan.
It also expressly adds the provider-top switching improvement **inside Plan 1**.
Accordingly, Plan 1 contains broad per-feature research and this bounded implementation
track; Plan 2 implements only the remaining accepted optimizations. Do not duplicate
completed Plan 1 changes as Plan 2 TODOs. This interpretation is explicit, not a claim
that any implementation or external review has already run.

The attachment's new focused-branch instruction governs this task. The earlier
main-only request governed the preceding 0.11.0 implementation. No remote branch,
commit or push is created by this preparation. The source path from the user's host
maps here to `/mnt/data/workspaces/plan-and-execute`; never modify another host path.

Do not commit, push, create a PR, publish to npm or run authenticated models without
explicit user confirmation. Do not change installed skills or user-global routing.
Do not print environment/profile secret values. Non-generative CLI discovery must
be bounded and redact credentials. The root model stays unchanged.

## Current state and honest gates

All 86 tasks start **pending**. `autostart` is false. No active pointer is installed.
Native `plan_review.status=approved` records only the host's structural planning pass;
it does not satisfy the independent maximum-model review required by the user.
TODO 001 is that real gate. The host currently has no `claude`, `codex` or `agy`
executable on PATH. Do not impersonate a worker or assert a strongest-model review.

The source request assesses as FINAL_PLAN (8,439 estimated working-set tokens),
not automatic oversized PRIMARY_PLAN. This first plan exists by user instruction,
not by artificially changing size thresholds or replacing feature research with
mechanical source-fragment summaries.

## Fresh reviewer policy

Each topic task has a separate review TODO with `model_tier=max`. At dispatch, check
current authenticated availability, capability and maximum native effort. Concrete
model names are resolved then, not hard-coded from marketing labels or old defaults.
`xhigh` is the portable requested effort; use the strongest supported native setting
for that model after discovery. A cheap fallback is not an approved substitute for
this requirement. If the strongest permitted reviewer cannot run, keep the gate pending.

Record actual provider, model, native effort, catalog/discovery evidence and a fresh
session identifier in the review packet. Do not save secrets or full transcripts.
The reviewer receives only the candidate result, relevant source/diff/tests and this
rubric, never the author's conversation. It writes findings; the author fixes them.
A failing review does not silently approve or edit the author's implementation.
Use controller reset/claim/checkpoints for rework; never hand-edit task status.
After author changes, recompute reviewed-input hashes and perform a fresh re-review.

## Context and cost policy

Use `TASK_INPUTS.json` to select the current task's input paths; read only that entry.
Use the source symbol index to locate ranges, not as a substitute for reading code.
Use deterministic tools for indexing, hashing, tests, replay and resource sampling.
No model is needed for a periodic log poll. Research starts at its assigned standard
or strong tier; user-required max capability is concentrated in explicit review gates.
At most two independent read-only research workers run concurrently. Shared source
writes and provider-switch implementation remain sequential at dependency barriers.

Reuse checked source metadata by ID. Do not treat another topic's conclusions as facts
without evidence. Keep each report compact: a decision page plus retrievable appendices,
not a transcript. No arbitrary claim of token savings: store unknown cost as null.
Source currency/version matters more than source count. Stop exploration only when
all material alternatives, risks and acceptance contracts have checked evidence.

## Whole-project coverage

The 32-topic inventory is a **seed**. The full audit must disposition all 188 baseline
tracked files and their relevant symbols, cross-module contracts and tests. Distinguish
implementation, tests, documentation, fixtures and packaging. The inventory task must
prove coverage and add missing topics before any final synthesis. If more topics are
found, report `plan_defect` and have the orchestrator replan only remaining work using
native controllers, preserving completed evidence. No invented retrospective TODOs.

Research each supported adapter/profile separately: Claude, Codex, Antigravity/legacy
Gemini, Qwen, Kimi, Trae Agent, Muse Code, GLM and DeepSeek. Current CLI discovery must
confirm actual flags, versions, model lists and persistence; absent CLIs are recorded
as unverified. Do not confuse a same-named CLI or a model vendor with its host adapter.

## Research deliverable contract

Each assigned output packet is UTF-8 JSON, schema version 1, with:

- `task_id`, `kind`, `status: completed`, `summary`, and at least one `evidence` item.
- Evidence items have `classification: verified|inference`, a nonempty `claim`, and
  `source_refs`. Every ref resolves to a packet source ID or repository file path.
- `sources`: `id` (`E001`...), `title`, `publisher`, `url`, `accessed_at` (ISO date),
  `source_type`, `checked_version`, `finding`, and `verification_scope`. Source types
  include official_documentation, official_code, paper, author_book_excerpt, author_book_metadata.
- `alternatives`: at least current_baseline and one competing design, each with costs,
  benefits, risks and evidence. Costs must distinguish subscription quota, API currency,
  cache writes/reads and validation effort. Missing measurements are null.
- `decision`, `evaluation` (metrics, baseline, test cases and expected falsification),
  `proposed_changes` (possibly empty), `unknowns`, and `verified_artifacts` (path + SHA-256).

Each report has date, base commit/tree, current behavior with code ranges, verified
versus inferred findings, an alternatives table, decision, cost/quality model,
compatibility risks, deterministic test proposal and numbered E### bibliography.
Do not claim to have read paywalled books from a title page. Use accessible author
material, explicitly scoped excerpts or an authorized copy; record inaccessible parts.
Use source identifiers in prose instead of copying long vendor documentation.

## Review deliverable contract

In addition to the common packet fields, reviews contain `reviewer` with actual
`provider`, `model`, `model_tier: max`, `native_effort`, `fresh_context: true`,
`session_id`, and `capability_evidence` (repository-relative metadata file).
`reviewed_inputs` contains path/SHA-256 pairs. `findings` is a list with severity,
location, evidence, status and resolution. `verdict` must be approved and no critical
or high finding may be unresolved. Unknown capability is not accepted as verified.

The JSON checker enforces structure, hashes and file boundaries. It cannot prove
semantic correctness or actual model identity by itself; the orchestrator must match
the receipt to the real dispatch metadata. File existence alone is never approval.

## Provider-switch track

The ADR must decide declared versus effective chains; provider-local evidence;
effective model/effort no-ops; entry rung; retry exceptions; per-phase state; attempt
budget; native session alternatives; and handoff a/b/c/d modes from the attachment.
Do not pre-decide these implementation details merely from this planning document.

The deterministic capsule is the availability-safe baseline to compare, not an
already-approved implementation. Validate paths against current Git changes, commands
against actual validation evidence and subtask IDs against the manifest. Redact before
truncating, mark unverified and expire after one next attempt. Preserve deterministic
failure evidence. Probe raw and concise runners, pattern hooks, strict output schemas,
snapshot model resolution, workload native effort and the design phase.

All twelve attachment acceptance cases remain mandatory; `ACCEPTANCE_MATRIX.md` and
`ACCEPTANCE_MATRIX.json` map each case to its implementation and independent review tasks. The two related problems
(empty-tier dispatch and missing evidence path) must be fixed or explicitly deferred
with reason and regression impact. Opt-in off must preserve existing assertions.
No claim of real savings from replay: measure the documented scenario matrix first,
then obtain separate authorization for real authenticated evaluation.

## Resource map and validation

Each task uses `resource_watch.py run --validation P1_<task>` through the reusable
project map. Those checks validate the delivered evidence packet and review contracts,
not just file existence. Runtime/implementation tasks must additionally run affected
self-tests and record exact commands, exit codes and log paths in `validation_results`.
Task 080 also runs full npm ci, npm run check and npm pack --dry-run and reports results.

The preliminary full baseline timed out at the host command limit, without a full-suite
result. Do not relabel it passed or a confirmed repository defect. The audit must get
an untruncated baseline on a capable host and separate environmental issues from defects.
A fresh map fingerprint does not prove semantic correctness of old map entries.

## Plan 2 materialization and cleanup

TODO 084 writes a Plan 2 spec and FINAL_PLAN_INPUT under durable `docs/plans/`, not
by editing Plan 1 control files. The **orchestrator**, outside the isolated worker,
materializes and audits the second native plan with planctl/studyctl/service_map before
accepting that TODO. It stays inactive until the reviewed handoff. This manager action
avoids granting the worker permission to mutate another plan's control state.

If final review changes source code or decisions, revalidate the Plan 2 fingerprint
and reopen its approval through controllers. The last TODO is the whole-skill review.
After successful handoff, guarded cleanup may remove Plan 1 control state, never
research evidence, source files, Plan 2 control state or the shared resource inventory.
While any task or maximum-capability review remains pending, retain the entire plan.
