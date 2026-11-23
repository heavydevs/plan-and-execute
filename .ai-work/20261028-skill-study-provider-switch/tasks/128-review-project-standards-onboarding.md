---
task_id: "128"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R069, R070, R072"
dependencies: "127"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 128 — Independently review coding-standard discovery, consent, documentation and CLI safety

## Objective

Independently review coding-standard discovery, consent, documentation and CLI safety. Implement pre-decided P066 architecture; all actual implementation/review pending.

## Requirements covered

- R069
- R070
- R072

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation change or independent final-hash correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One reviewer context holds the final 127 code, tests and consent invariants needed to judge and correct them together.
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

- [ ] **S001** — Read final 127 evidence
  - Read P066 and only actual final 127 code/tests/receipts and review their SHA hashes.
- [ ] **S002** — Dispatch a fresh max-qualified review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 128` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: UX/standards consent, source evidence, quality, privacy, token use.
- [ ] **S003** — Run adversarial safety probes
  - Adversarial tests for worktree identity, repeat consent, no-TTY CI, secrets, prompt injection, symlinks, stale code, hidden remote calls and overwritten agent files.
- [ ] **S004** — Fix blockers and record the review
  - Fix or reopen owner for blocking defects, rerun focused tests; record genuine reviewer route, source hash and decisions.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independently review coding-standard discovery, consent, documentation and CLI safety

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
- docs/research/20261028-skill-optimization/implementation/128-receipt.json
- docs/research/20261028-skill-optimization/implementation/128-outcome.md

## Dependencies

- 127

## Allowed related task definitions

- None

## Implementation guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/127-project-coding-standards-and-first-use-research.md when handling this task; apply complete architecture and adversarial acceptance A–T.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Prioritize deterministic inspection, narrow source reads and caching; broad project/code/web study only after approved first use or manual init/refresh.
- No unapproved edits, installs, secrets, paid providers or overwrites of agents' project instructions.
- Run real tests, record paths/hashes/permissions and source-specific receipt; no fabricated cost/success.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- A real fresh max-qualified reviewer approves the final 127 source/test/receipt hashes with dispatch provenance.
- The S003 adversarial probes pass: worktree identity, repeat consent, no-TTY CI, secrets, prompt injection, symlinks, stale code, hidden remote calls and overwritten agent files.
- High/critical findings are fixed and re-reviewed on the final hashes.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 127 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_128`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_128`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
