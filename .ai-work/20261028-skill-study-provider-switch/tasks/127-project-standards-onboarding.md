---
task_id: "127"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R069, R070, R072"
dependencies: "025, 120"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 127 — Implement one-time project onboarding, source-derived coding standards documentation and CLI

## Objective

Implement one-time project onboarding, source-derived coding standards documentation and CLI. Implement pre-decided P066 architecture; all actual implementation/review pending.

## Requirements covered

- R069
- R070
- R072

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation change or independent final-hash correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Consent state, discovery, generated standards docs and the CLI share one onboarding contract and one test boundary.
- Context that is genuinely shared by all subtasks:
- Assigned P066 research, current affected code and accepted predecessor receipts only.
- Concerns deliberately isolated into other TODOs:
- Other task files, complete repo scans, historic chat and unrelated sources.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Inspect P066 and live source
  - Inspect only P066 and the relevant live source, 025/120 evidence and test baselines.
- [ ] **S002** — Implement persisted first-use consent
  - Implement persisted per-project, per-topic standards/UX first-use consent with noninteractive fallback, secure scope, worktrees and atomic state.
- [ ] **S003** — Run approved init/refresh discovery only
  - Perform approved init/refresh only: deterministic module/libraries/usage/representative patterns/ORM/helpers discovery; optional contemporary source study; no recurring full research.
- [ ] **S004** — Generate compact source-hashed standards docs
  - Generate compact source-hashed docs/ai-standards/ AGENT_INDEX.md, manifests, TECH_STACK.md, ARCHITECTURE.md, CODING_RULES.md, REUSE_CATALOG.json, module rules and ADRs; retain inferred vs approved distinction.
- [ ] **S005** — Implement pae standards and onboarding CLI
  - Implement pae standards status/init/refresh/explain/check/export-instructions and pae onboarding status, --json/dry-run, CLI help and EN/PT-BR usage examples; exporting third-party instructions requires approval.
- [ ] **S006** — Test recognition, consent and security cases
  - Test JPA and monorepo recognition, declared-but-unused dependencies, consent persistence, CI/headless zero prompting, stale hash, malicious files, security and no fallback to unwanted study.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement one-time project onboarding, source-derived coding standards documentation and CLI

## Out of scope

- No unapproved target project modifications, network, external code disclosure, repeat broad research or duplicated orchestration.

## Expected files

- skill/plan-and-execute/scripts/project_onboarding.py
- skill/plan-and-execute/scripts/project_standards.py
- skill/plan-and-execute/scripts/standardsctl.py
- skill/plan-and-execute/references/PROJECT_STANDARDS.md
- test/optimization/standards_onboarding_self_test.py
- skill/plan-and-execute/references/PROJECT_ONBOARDING.md
- skill/plan-and-execute/SKILL.md
- bin/plan-and-execute.js
- test/cli.test.js
- docs/research/20261028-skill-optimization/implementation/127-receipt.json
- docs/research/20261028-skill-optimization/implementation/127-outcome.md

## Dependencies

- 025
- 120

## Allowed related task definitions

- None

## Implementation guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md when handling this task; apply complete architecture and adversarial acceptance A–T.
- Reuse existing CLI/routing, task_context_router, UX first-use (where applicable), security/performance 107/108 and test strategy 111/112.
- Prioritize deterministic inspection, narrow source reads and caching; broad project/code/web study only after approved first use or manual init/refresh.
- No unapproved edits, installs, secrets, paid providers or overwrites of agents' project instructions.
- Run real tests, record paths/hashes/permissions and source-specific receipt; no fabricated cost/success.

## Acceptance criteria

- P066 cases D, F, G, H-M, O, P, S and T pass with real tests: one-time consent, no repeated UX, discovery, safe exports that never overwrite manual agent files.
- No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.
- First-use consent, reusable source-backed agent docs, framework-consistent ORM/JDBC/exception detection and UX lazy activation are validated where applicable.
- Test/reviewer evidence exists for current code SHA; otherwise task remains pending.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_127`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_127`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
