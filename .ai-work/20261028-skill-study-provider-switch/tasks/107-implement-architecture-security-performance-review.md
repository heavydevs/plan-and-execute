---
task_id: "107"
status: "pending"
requirements: "R056"
dependencies: "013,029,049,088,092,098,100,104,106"
allowed_related_task_reads: "none"
---

# 107 — Implement risk-based security/performance architecture review and code-review lenses

Objective: Add independent security and performance design review before implementation on material architecture, and both lenses to existing final code review, without default performance benchmarks.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Study baseline — Read P056 study, current run_isolated/planctl/artifact_contract and relevant 087/088 DIRECT code; pin expected behavior.
- [ ] **S002** Classify material architecture — Define deterministic risk-based design admission, lightweight security/performance quality-attribute scenarios and justified N/A.
- [ ] **S003** Implement pre-coding independent design gate — Reuse existing design lifecycle, distinct read-only qualified reviewer, actual hash-bound evidence, high/critical blocker, re-review and crash/resume safety.
- [ ] **S004** Extend end-of-task code review — Include both security and performance with actionable findings in the existing fresh independent review and receipt; preserve correctness, no extra routine specialist calls.
- [ ] **S005** Preserve permissions and compatibility — Maintain schemas1–4, DIRECT, provider/cost constraints, terse prompts and user-only opt-in for app performance/load/benchmark tests.
- [ ] **S006** Implement functional tests — Test design/no-design, false reviewer, N/A, missing/stale hashes, high/critical, resume, final re-review, legacy and opt-in performance cases.
- [ ] **S007** Record real outcomes — Run mapped validation; record source hashes, actual receipts and limitations without claiming any model review now.

## Scope

In: Add independent security and performance design review before implementation on material architecture, and both lenses to existing final code review, without default performance benchmarks.
Out: No mandatory performance benchmarks, second orchestrator, duplicated routine reviewer, unapproved provider execution or user-global edits.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `skill/plan-and-execute/scripts/direct_route.py`, `skill/plan-and-execute/references/PLANNING_PROTOCOL.md`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/DELEGATION.md`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md`, `test/optimization/architecture_security_performance_review_self_test.py`, `docs/research/20261028-skill-optimization/implementation/107-receipt.json`, `docs/research/20261028-skill-optimization/implementation/107-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/107-architecture-security-performance-review.md and docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261112_ARCH_SECURITY_PERFORMANCE.md first.
- Inspect run_isolated.py design_prompt/run_design_phase and planctl.py design/reset plus artifact_contract.py and DIRECT 087/088.
- Reuse native orchestration/reviewer with distinct read-only approved hash-bound architecture gate; integrate security/performance in the existing final code review alongside correctness.
- Do not create automated application performance/load/stress/benchmark tests unless the task user explicitly asks; functional tests of review mechanics required.
- Run mapped functional regressions and record real receipts and current source hashes, not fabricated independent reviews.

## Acceptance

- Material formal design cannot launch implementation without a distinct genuine independent read-only security/performance design approval of current source/note fingerprints.
- Review checks applicable threats/trust boundaries and realistic scale/hot path/cost plus alternative mitigations and security-performance tradeoffs; justified N/A and unmeasured assumptions explicit.
- Unresolved critical/high architecture defects, absent reviewer, fake provider evidence or stale hashes block implementation; retry/resume require fresh bounded review.
- Existing final independent code-review pass evaluates security and performance separately, with severity/evidence or justified N/A, while preserving correctness and tests.
- Critical/high security/performance findings block final task acceptance until fixed and re-reviewed on current hashes; no fabricated performance impact.
- No automated performance/load/stress/benchmark tests required or generated absent explicit user request; functional tests of review mechanism remain mandatory.
- Legacy schemas1–4, DIRECT, permissions, routing/economics, distinct reviewer and compact context remain compatible.
- Mapped functional tests and negative fixtures pass with real implementation hashes/receipts; missing evidence leaves task pending.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_107`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_107`
