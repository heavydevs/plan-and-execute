# Changelog

All notable changes to this project are documented here.

## Unreleased

- Fixes `pae resume` / `lifecyclectl resume` launching the raw `run_isolated.py` instead of `run_concise.py`, which silently skipped the concise worker prompt and the shared-pattern validate/assignment/adopt hooks; the CLI now drives `lifecyclectl_concise.py`.
- Fixes Windows worker dispatch: npm-installed CLIs (`claude.cmd`, `codex.cmd`, `agy.cmd`) and the VS Code `code.cmd` editor shim are resolved through PATH/PATHEXT before `Popen`, which cannot launch `.cmd` files by bare name. `pae doctor` probes such shims through a shell, and the Windows Store `python` alias (exit 9009) no longer masks a real `python3`/`py` when the CLI looks for an interpreter.
- Hardens the runner-lease liveness check on Windows with a `ctypes` process query instead of `os.kill(pid, 0)`, whose Windows semantics vary by interpreter version.
- Ties the Antigravity `--print-timeout` to `task_timeout_seconds` (`print_timeout: "auto"`, 12h when the runner has no limit) so agy cannot kill a worker the runner would still wait for.
- CI now runs the suite on `windows-latest` and on Python 3.10 (the lowest supported interpreter) in addition to Ubuntu/Python 3.13.
- Documents that validation commands run through the platform shell and should prefer toolchain commands over POSIX builtins when a plan may resume on another OS.
- Escalates worker routes from **classified failure evidence** instead of a retry count: the completion report and `planctl fail --failure-class` record `mechanical`, `semantic`, `environmental`, `budget`, `plan_defect`, or `unknown`; `semantic` jumps a tier, `mechanical`/`budget` repeat the rung once, `environmental` keeps it, `plan_defect` blocks the TODO for replanning. Provider ladders live in `routingctl.py` (Codex: Terra → Astra Low, never Terra High; Claude: Haiku → Sonnet Medium); when evidence asks for a rung above the top on the last provider, the TODO is blocked (`ladder_exhausted`) for replanning instead of burning `max_attempts` at the strongest route.
- Makes `routingctl.py` the single model catalog: `planctl.default_config` now overlays it, so raw `planctl.py`/`run_isolated.py` entrypoints no longer generate plans with stale model ids.
- Omits `--effort` for models that accept none (Claude Haiku) instead of passing it blindly; adds optional per-worker budget guards `claude.max_turns`, `claude.max_budget_usd`, and `codex.rollout_token_budget`, with exhaustion recorded as a resumable `budget` failure.
- Adds two-phase leaves: a `high` TODO may declare `design_route`; the runner dispatches a stronger design worker that writes `tasks/<id>.design.md`, then the implementation worker runs at the TODO's own route with the note (the design attempt does not consume an implementation attempt; reset discards the note).
- Adds decision-first planning evidence: optional `request_analysis.hard_decisions` (id, decision, rationale, `route_used`, source refs) rendered in `ANALYSIS.md`.
- Adds `routingctl.py route --signals ...` and `references/tier-evals.json`: a deterministic leaf-signal → minimum tier/effort floor mirrored in `SKILL.md`, so a small root model routes small-but-risky leaves strong and large-but-mechanical leaves cheap; a regression corpus protects both directions.
- Documents the elevation mechanics per host (Claude `Agent` `model`/`effort`, `isolation: worktree`, `CLAUDE_CODE_SUBAGENT_MODEL`, `opusplan`, `subagentPromptCacheTtl`, dynamic workflows; Codex `spawn_agent` roles, `.codex/agents/*.toml`, `plan_mode_reasoning_effort`, `agents.default_subagent_*`) and the rule that the skill never switches the root session's model/effort (prompt-cache economics): it delegates the leaf instead.
- Corrects the Claude guidance: the built-in `Explore` agent inherits the session model and is only cheap with an explicit `model: "haiku"`; current Claude 5 effort defaults are adaptive and effort controls thoroughness, so implementation workers never run at `low`.
- Reorders worker prompts so static rules form a byte-stable, cache-shareable prefix and per-task values come last; documents concrete prompt-cache facts for Claude Code and Codex.
- Fixes `command_prefix` on Windows (POSIX `shlex` stripped backslashes from configured executable paths), which also makes the end-to-end runner self-test pass on Windows.
- Adds an `antigravity` execution adapter for the Google Antigravity CLI (`agy -p` headless mode with `--output-format json`, `--json-schema`, `--model`, `--effort`, `--print-timeout`), wired through `pae --provider antigravity`, `pae doctor`, and the provider self-tests; marks the Gemini CLI adapter as legacy (CLI sunset 2026-06-18).
- Splits the complex-study two-question protocol into `references/STUDY_CHOICES.md`, loaded only when a `complex` study still needs a depth choice, so `simple`/`medium` studies no longer pay for it; the interaction contract and its regression test are unchanged.
- Moves research citations out of runtime references into `docs/RESEARCH_BASIS.md`; adds an optional host-native fan-out dispatch note for PRIMARY_PLAN digests; points `INTAKE.md` at `planctl_concise.py`.

## 0.8.0 - 2026-09-03

- Changes automatic routing to **DIRECT by default, ORCHESTRATED by evidence, with late PROMOTION when direct work grows**.
- Narrows the skill description with explicit near-miss negatives so routine bug fixes, bounded features/refactors, ordinary test changes, and cohesive multi-file edits do not automatically pay for the planning harness.
- Replaces the large entrypoint with a compact routing control plane; full study/planning/execution details now load only after orchestration is selected.
- Adds a true DIRECT exit that creates no `.ai-work`, study, requirements inventory, TODOs, task files, workers, or lifecycle state.
- Adds `PROMOTION.md` and `promotectl.py` for compact direct-to-orchestrated handoff containing completed work, validated results, active decisions, relevant code, blockers/risks, remaining outcomes, optional context pressure, and bounded git evidence.
- Plans only remaining work after promotion; completed implementation is never rewritten as retroactive TODOs.
- Treats context-window pressure as a secondary signal rather than a universal fixed 90% trigger; high context alone does not promote nearly finished cohesive work.
- Preserves the complete orchestrated contract: persistent `TODO.md`, one task definition per TODO, authoritative `manifest.json`, resumable subtasks, deterministic validation, learning boundaries, cleanup safety, and resume without previous chat history.
- Preserves per-TODO logical `provider`, `model_tier`, and `reasoning_effort` recommendations so another compatible model/provider can resume after quota/availability changes.
- Adds `--activation selective|explicit` plus `--selective`/`--explicit` installer aliases. Selective remains the default; explicit installs Claude with `disable-model-invocation: true` and Codex with `allow_implicit_invocation: false`.
- Upgrades the installer ownership marker to schema v2 with both source and installed-variant hashes while remaining backward-compatible with schema-v1 managed copies.
- Adds a 28-case routing regression corpus covering positive orchestration, late promotion, and near-miss DIRECT requests, plus dedicated routing and promotion self-tests.
- Updates bilingual installation/project documentation and integrated validation for the selective activation architecture.

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
