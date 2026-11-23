---
task_id: "107"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R056"
dependencies: "013, 029, 049, 088, 092, 098, 100, 104, 106"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 107 — Implement risk-based security/performance architecture review and code-review lenses

## Objective

Add independent security and performance design review before implementation on material architecture, and both lenses to existing final code review, without default performance benchmarks.

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

- [ ] **S001** — Study baseline
  - Read P056 study, current run_isolated/planctl/artifact_contract and relevant 087/088 DIRECT code; pin expected behavior.
- [ ] **S002** — Classify material architecture
  - Define deterministic risk-based design admission, lightweight security/performance quality-attribute scenarios and justified N/A.
- [ ] **S003** — Implement pre-coding independent design gate
  - Reuse existing design lifecycle, distinct read-only qualified reviewer, actual hash-bound evidence, high/critical blocker, re-review and crash/resume safety.
- [ ] **S004** — Extend end-of-task code review
  - Include both security and performance with actionable findings in the existing fresh independent review and receipt; preserve correctness, no extra routine specialist calls.
- [ ] **S005** — Preserve permissions and compatibility
  - Maintain schemas1–4, DIRECT, provider/cost constraints, terse prompts and user-only opt-in for app performance/load/benchmark tests.
- [ ] **S006** — Implement functional tests
  - Test design/no-design, false reviewer, N/A, missing/stale hashes, high/critical, resume, final re-review, legacy and opt-in performance cases.
- [ ] **S007** — Record real outcomes
  - Run mapped validation; record source hashes, actual receipts and limitations without claiming any model review now.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Add independent security and performance design review before implementation on material architecture, and both lenses to existing final code review, without default performance benchmarks.

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
- docs/research/20261028-skill-optimization/implementation/107-receipt.json
- docs/research/20261028-skill-optimization/implementation/107-outcome.md

## Dependencies

- 013
- 029
- 049
- 088
- 092
- 098
- 100
- 104
- 106

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/107-architecture-security-performance-review.md and docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261112_ARCH_SECURITY_PERFORMANCE.md first.
- Inspect run_isolated.py design_prompt/run_design_phase and planctl.py design/reset plus artifact_contract.py and DIRECT 087/088.
- Reuse native orchestration/reviewer with distinct read-only approved hash-bound architecture gate; integrate security/performance in the existing final code review alongside correctness.
- Do not create automated application performance/load/stress/benchmark tests unless the task user explicitly asks; functional tests of review mechanics required.
- Run mapped functional regressions and record real receipts and current source hashes, not fabricated independent reviews.
- If direct_route.py is absent, use the DIRECT entry point named in the 087 receipt.

## Acceptance criteria

- Material formal design cannot launch implementation without a distinct genuine independent read-only security/performance design approval of current source/note fingerprints.
- Review checks applicable threats/trust boundaries and realistic scale/hot path/cost plus alternative mitigations and security-performance tradeoffs; justified N/A and unmeasured assumptions explicit.
- Unresolved critical/high architecture defects, absent reviewer, fake provider evidence or stale hashes block implementation; retry/resume require fresh bounded review.
- Existing final independent code-review pass evaluates security and performance separately, with severity/evidence or justified N/A, while preserving correctness and tests.
- Critical/high security/performance findings block final task acceptance until fixed and re-reviewed on current hashes; no fabricated performance impact.
- No automated performance/load/stress/benchmark tests required or generated absent explicit user request; functional tests of review mechanism remain mandatory.
- Legacy schemas1–4, DIRECT, permissions, routing/economics, distinct reviewer and compact context remain compatible.
- Mapped functional tests and negative fixtures pass with real implementation hashes/receipts; missing evidence leaves task pending.
- The design reviewer is read-only through the adapter-pinned read-only argv (fail-closed table in run_isolated.py) plus a before/after worktree fingerprint; provider sandbox/skip_permissions settings never reach it.
- The reviewer route follows Codex > Claude at strong/max; frontier only through task 105's approval.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_107`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_107`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
