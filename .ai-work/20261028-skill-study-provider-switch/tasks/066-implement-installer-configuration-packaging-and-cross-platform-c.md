---
task_id: "066"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 063, 065"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 066 — Implement installer, configuration, packaging and cross-platform CI

## Objective

Validate the actual distributable and installed dependency layout, preserve edited user installations, and separate metadata-only pack inspection from lifecycle/full-suite execution.

## Requirements covered

- R002
- R003
- R004
- R005
- R007
- R032
- R037
- R038
- R039
- R042
- R044

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation contract with its regression tests; source coupling requires a shared acceptance boundary, not an arbitrary file-count split.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: This task owns one behavior or correction gate with independently checkable outcomes.
- Context that is genuinely shared by all subtasks:
- Read only the assigned decision, source targets and accepted prerequisite receipts.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated reports, provider guides or historical conversation transcripts.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read assigned research and pin applicable contracts
  - Read docs/research/20261028-skill-optimization/prepared-research/066-distribution.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Check actual pack manifests for required runtime files and forbidden plans, receipts, credentials and logs.
- [ ] **S003** — Implement revised contract 2
  - Separate ignore-scripts metadata inspection from full lifecycle validation and test the extracted distributable layout.
- [ ] **S004** — Implement revised contract 3
  - Preserve local installation edits and rollback failed upgrades without changing global configuration.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement installer, configuration, packaging and cross-platform CI

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- lib/installer.js
- tools/package-skills.js
- tools/validate-skill.js
- bin/plan-and-execute.js
- test/optimization/distribution_self_test.py
- package.json
- package-lock.json
- .npmignore
- .github/workflows/ci.yml
- skill/plan-and-execute/references/INSTALLATION.md
- skill/plan-and-execute/references/INSTALLATION.pt-BR.md
- docs/research/20261028-skill-optimization/implementation/066-receipt.json
- docs/research/20261028-skill-optimization/implementation/066-outcome.md

## Dependencies

- 001
- 063
- 065

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/066-distribution.md.
- Use only task 066 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/066-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.
- Edit package-lock.json only with npm install --package-lock-only --ignore-scripts after owner confirmation; no npm publish, no -g install; npm pack only with --dry-run or --pack-destination <tmp>.

## Acceptance criteria

- No native plan, private log, .env, bytecode or node_modules entry appears in a distributable archive.
- Selective-explicit-selective round trips retain correct hashes and policy metadata.
- A locally edited installed file prevents automatic replacement/removal.
- Companion packages resolve a matching shared runtime after a clean temporary install.
- CLI/docs/version constraints and actual package contents are checked without publishing.
- A nested planning file is rejected even when docs is included in package files.
- Both skills resolve shared runtime resources after clean temporary installation.
- An edited installed SKILL.md prevents overwrite without explicit force authorization.
- Metadata-only pack evidence cannot be reported as a full prepack or test pass.
- Temporary installs use an isolated npm prefix and HOME/USERPROFILE/APPDATA; hashes of the real installed skill dirs and %APPDATA%/plan-and-execute/orchestrator.config.json are identical before and after.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_066`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_066`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
