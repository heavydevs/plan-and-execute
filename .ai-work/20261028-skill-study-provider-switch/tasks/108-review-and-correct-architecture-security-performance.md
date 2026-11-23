---
task_id: "108"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R056"
dependencies: "107"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 108 — Independently review and correct architecture security/performance gates

## Objective

Independently audit and correct the actual design security/performance gate and final review lenses, source-hash/provenance controls, cost and compatibility.

## Requirements covered

- R056

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: A single context-cohesive implementation or genuinely independent correction boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One review lifecycle contract and one validation boundary.
- Context that is genuinely shared by all subtasks:
- P056 research and current task-relevant source.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated plans, chats, historical logs.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read actual implementation
  - Inspect latest 107 code/tests and real source hashes, outcome/receipt and prepared research.
- [ ] **S002** — Dispatch genuine independent reviewer
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 108` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** — Audit security/performance and bypass risks
  - Challenge architecture assumptions, stale approval, crash/resume, forged reviewer, read-only limits, DIRECT/legacy, false positives, provider budget and benchmark-default ban.
- [ ] **S004** — Fix blockers and revalidate
  - Correct critical/high defects, rerun mapped checks and re-review final changed hashes; otherwise stay pending.
- [ ] **S005** — Record review receipt
  - Write genuine 108 receipt/outcome and precise limitations/unknown costs, no invented benchmarks.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independently audit and correct the actual design security/performance gate and final review lenses, source-hash/provenance controls, cost and compatibility.

## Out of scope

- No second orchestrator, forced benchmark, unauthorized model/permission changes.

## Expected files

- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/artifact_contract.py
- skill/plan-and-execute/scripts/direct_route.py
- skill/plan-and-execute/references/PLANNING_PROTOCOL.md
- skill/plan-and-execute/references/WORKFLOW.md
- skill/plan-and-execute/references/PLAN_SPEC.md
- skill/plan-and-execute/references/DELEGATION.md
- skill/plan-and-execute/references/MODEL_ROUTING.md
- skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md
- test/optimization/architecture_security_performance_review_self_test.py
- docs/research/20261028-skill-optimization/implementation/108-receipt.json
- docs/research/20261028-skill-optimization/implementation/108-outcome.md

## Dependencies

- 107

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/107-architecture-security-performance-review.md and docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261112_ARCH_SECURITY_PERFORMANCE.md first.
- Inspect run_isolated.py design_prompt/run_design_phase and planctl.py design/reset plus artifact_contract.py and DIRECT 087/088.
- Reuse native orchestration/reviewer with distinct read-only approved hash-bound architecture gate; integrate security/performance in the existing final code review alongside correctness.
- Do not create automated application performance/load/stress/benchmark tests unless the task user explicitly asks; functional tests of review mechanics required.
- Run mapped functional regressions and record real receipts and current source hashes, not fabricated independent reviews.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Genuine fresh independent maximum-qualified reviewer evidence includes provider/model/effort/session, dispatch and pinned final 107 code/test/receipt hashes.
- Both security and performance are audited before implementation for material design and in the existing final code review alongside correctness.
- Critical/high bypass, stale/replayed review, fake provenance, permission expansion, legacy and DIRECT issues are corrected or block acceptance.
- No default automated performance/load/stress/benchmark tests; functional workflow tests remain, and ordinary final reviewer does not spawn two routine specialists.
- Actual mapped regressions and final-hash re-review pass with no unresolved critical/high; if not, task remains pending.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 107 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_108`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_108`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
