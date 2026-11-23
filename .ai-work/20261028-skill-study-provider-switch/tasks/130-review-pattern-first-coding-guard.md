---
task_id: "130"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R069, R071, R072"
dependencies: "129"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 130 — Independently review source-backed pattern enforcement, safe exceptions and token economy

## Objective

Independently review source-backed pattern enforcement, safe exceptions and token economy. Implement pre-decided P066 architecture; all actual implementation/review pending.

## Requirements covered

- R069
- R071
- R072

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation change or independent final-hash correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One reviewer context holds the final 129 guard code, tests and exception rules needed to judge and correct them together.
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

- [ ] **S001** — Review final 129 with a fresh max reviewer
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 130` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: P066 and final 129 source/tests/receipt.
- [ ] **S002** — Probe standards, exceptions and isolation
  - Probe approved versus inferred standards, ORM/JDBC exceptions, stale files, monorepo cross-talk, prompt injection, security/performance and context bounds.
- [ ] **S003** — Correct defects and require final sign-off
  - Correct implementation owner defects and rerun tests, require true final SHA independent sign-off.
- [ ] **S004** — Record honest provider and cost evidence
  - Record honest provider/model/effort/real cost or unknown and integration evidence; do not simulate completion.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independently review source-backed pattern enforcement, safe exceptions and token economy

## Out of scope

- No unapproved target project modifications, network, external code disclosure, repeat broad research or duplicated orchestration.

## Expected files

- skill/plan-and-execute/scripts/standards_guard.py
- skill/plan-and-execute/scripts/task_context_router.py
- skill/plan-and-execute/scripts/runner_contract.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/references/PROJECT_STANDARDS_GATES.md
- test/optimization/standards_guard_self_test.py
- docs/research/20261028-skill-optimization/implementation/130-receipt.json
- docs/research/20261028-skill-optimization/implementation/130-outcome.md

## Dependencies

- 129

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

- A real fresh max-qualified reviewer approves the final 129 source/test/receipt hashes with dispatch provenance.
- The S002 adversarial probes pass: approved vs inferred standards, ORM/JDBC exceptions, stale files, monorepo cross-talk, prompt injection, security/performance and context bounds.
- High/critical findings are fixed and re-reviewed on the final hashes.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 129 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_130`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_130`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
