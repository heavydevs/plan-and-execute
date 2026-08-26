# Changelog

All notable changes to this project are documented here.

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
