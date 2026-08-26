# Changelog

All notable changes to this project are documented here.

## 0.7.0 - 2026-08-26

- Adds schema-v4 TODO boundaries that explicitly justify why one fresh worker should keep the selected concerns in the same context.
- Requires planners and reviewers to split independent semantic domains, such as unrelated person and store CRUDs, while avoiding mechanical file-by-file microtasks.
- Adds a durable required-subtask checklist to every schema-v4 task definition, with controller-owned start, complete, reset, interruption recovery, and parent-completion gates.
- Preserves completed subtasks after power, host, or provider interruption so another fresh AI can continue from the first unfinished checkpoint without prior chat history.
- Adds directional `learning_targets` and concise `learnings/<source>-to-<target>.md` artifacts for validated, evidence-grounded discoveries that are relevant to declared future TODOs.
- Treats declared learning sources as context prerequisites so a target cannot race ahead before its possible learning artifacts are finalized.
- Rejects undeclared, backward, stale, oversized, unreferenced, tampered, or late learning transfer; immutable plan-time execution context remains separate from runtime discoveries.
- Requires workers to report exact `context_files_read`, `learning_files_read`, and `completed_subtask_ids` values before deterministic validation can accept the task.
- Adds opt-in isolated worker adapters for Gemini CLI, Qwen Code, Kimi Code CLI, and Trae Agent alongside Claude Code and Codex.
- Uses the current Kimi prompt-mode contract without incompatible approval flags; provider-specific retry exit codes remain configurable instead of being assumed.
- Keeps Claude Code and Codex as the only standard skill-installation targets, the only quick-start pair, and the default provider order.
- Extends `pae resume --provider`, `pae doctor`, model routing, lifecycle recovery, completion-report schema, examples, bilingual documentation, and package metadata.
- Adds dedicated task-memory and provider-adapter self-tests plus integrated package validation for schema-v1 through schema-v4 compatibility.

## 0.6.0 - 2026-08-26

- Adds schema-v3 progressive execution context with an explicit create/omit decision for global `CONTEXT.md`.
- Creates scoped `contexts/<topic>.md` files only for information shared by at least two and fewer than all TODOs.
- Keeps single-TODO information in the task definition and makes shared-context omission the default.
- Grounds every context item through `source_refs` and stores its minimality rationale separately from rendered worker context.
- Enforces hard limits on file count, item count, line length, total rendered size, duplicate text, and task assignment.
- Generates exact `context_files` mappings and an `Assigned execution context` section in every task definition.
- Requires fresh workers to read exactly their assigned context files and report `context_files_read`; missing or extra reads are rejected.
- Detects context tampering and prevents references to unassigned scoped context.
- Adds `contexts_minimal` to independent plan review and updates audit output, examples, bilingual documentation, installer validation, and self-tests.
- Preserves generated context across interruption/resume and removes it with guarded plan cleanup, cancel, or reset.

## 0.5.0 - 2026-08-26

- Makes the no-argument skill invocation state-aware: resume the unique unfinished implementation before creating a new request.
- Adds `.ai-work/.active-plan.json` discovery with stale-pointer repair and ambiguity protection.
- Adds atomic runner leases to prevent concurrent strict runners in the same plan.
- Recovers tasks left `in_progress` after power, network, or process interruption without counting a technical failure.
- Adds `lifecyclectl.py` for current, activate, recover, resume, deactivate, cancel, and reset operations.
- Adds `pae current`, `pae resume`, `pae cancel`, and `pae reset` for both Claude Code and Codex workspaces.
- Clears active lifecycle state after final summary generation, including completed plans retained with `--no-cleanup`.
- Makes cancel/reset remove recognized plan artifacts and status while preserving repository implementation changes.
- Adds lifecycle documentation and deterministic self-tests for pointer repair, interruption recovery, duplicate-runner prevention, completion, cancellation, and reset safety.

## 0.4.0 - 2026-08-26

- Adds an adaptive pre-plan study gate that must pass before requirements or executable TODOs are drafted.
- Makes internal repository study mandatory and records concrete source locations, findings, and planning impact.
- Evaluates explicit external-research triggers instead of making web research always required or relying on a free-form decision string.
- Requires authoritative version-appropriate external sources only when a trigger is active, and allows repository-only planning when every trigger is false.
- Adds stable material-question and evidence ids, high-impact question rules, an independent study review, and a stopping rule.
- Adds `studyctl.py` with `validate`, `render`, `attach`, and `validate-plan` commands.
- Adds deterministic proof that internal and external findings were copied into plan analysis and that synthesized constraints, requirements, risks, and validation implications affected the plan.
- Preserves canonical evidence as `study.json` and `STUDY.md` with a SHA-256 hash in `manifest.json`.
- Re-enters the study gate when execution discovers a material unknown, different version, contradictory contract, or new security, migration, or compatibility risk.
- Adds protocol documentation, a complete study-spec example, Python self-tests, validation rules, bilingual README updates, and CI packaging of `skill.zip`.

## 0.3.0 - 2026-08-25

- Adds a no-argument guided intake flow that creates a localized Markdown request draft and opens it in VS Code or another available editor.
- Adds `requestctl.py` with create, validate, extract, latest, and reopen commands.
- Adds an easy continue/reopen handoff in the skill workflow after the user saves the request.
- Accepts an existing requirements/task-description file as the complete skill argument.
- Preserves caller-owned files by copy and moves generated drafts into the plan as `REQUEST.md`.
- Stores and validates the request SHA-256 in `manifest.json`.
- Makes `TODO.md` a concise one-line-per-task status index; detailed model and execution metadata remains in task definitions.
- Rewrites the primary documentation in English with an outcome-focused quick start.
- Adds Portuguese README, installation, and publishing documentation.
- Updates canonical repository links to `heavydevs/plan-and-execute`.
- Expands Python and Node tests for editor detection, request validation, copy/move behavior, packaging, and concise TODO rendering.

## 0.2.0 - 2026-08-25

- Requires complete study of the request, repository, and authoritative sources when needed before drafting TODOs.
- Adds deterministic `request part (Pxxx) -> requirement (Rxxx) -> TODO` traceability.
- Adds `ANALYSIS.md`, `PLAN_REVIEW.md`, and the `planctl.py audit` quality gate.
- Requires independent plan review for coverage, atomicity, dependencies, and validation.
- Rejects executable `extreme` TODOs and requires atomicity rationale for `high` tasks.
- Adds recursive decomposition, replanning, and planning/review model-routing guidance.

## 0.1.0 - 2026-08-25

- Renames the skill to `plan-and-execute`.
- Adds an npm installer for Claude Code and Codex.
- Supports workspace and user installation scopes.
- Adds `install`, `status`, `paths`, `doctor`, and `uninstall` commands.
- Protects local changes with an ownership marker and SHA-256 hash.
- Adds Node tests, Python self-tests, and GitHub Actions workflows.
