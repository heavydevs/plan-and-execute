---
task_id: "108"
status: "pending"
requirements: "R056"
dependencies: "107"
allowed_related_task_reads: "none"
---

# 108 — Independently review and correct architecture security/performance gates

Objective: Independently audit and correct the actual design security/performance gate and final review lenses, source-hash/provenance controls, cost and compatibility.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read actual implementation — Inspect latest 107 code/tests and real source hashes, outcome/receipt and prepared research.
- [ ] **S002** Dispatch genuine independent reviewer — Use fresh authorized max-qualified reviewer; record provider/model/effort/session and exact reviewed hashes/provenance.
- [ ] **S003** Audit security/performance and bypass risks — Challenge architecture assumptions, stale approval, crash/resume, forged reviewer, read-only limits, DIRECT/legacy, false positives, provider budget and benchmark-default ban.
- [ ] **S004** Fix blockers and revalidate — Correct critical/high defects, rerun mapped checks and re-review final changed hashes; otherwise stay pending.
- [ ] **S005** Record review receipt — Write genuine 108 receipt/outcome and precise limitations/unknown costs, no invented benchmarks.

## Scope

In: Independently audit and correct the actual design security/performance gate and final review lenses, source-hash/provenance controls, cost and compatibility.
Out: No mandatory performance benchmarks, second orchestrator, duplicated routine reviewer, unapproved provider execution or user-global edits.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `skill/plan-and-execute/scripts/direct_route.py`, `skill/plan-and-execute/references/PLANNING_PROTOCOL.md`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `skill/plan-and-execute/references/DELEGATION.md`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md`, `test/optimization/architecture_security_performance_review_self_test.py`, `docs/research/20261028-skill-optimization/implementation/108-receipt.json`, `docs/research/20261028-skill-optimization/implementation/108-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/107-architecture-security-performance-review.md and docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261112_ARCH_SECURITY_PERFORMANCE.md first.
- Inspect run_isolated.py design_prompt/run_design_phase and planctl.py design/reset plus artifact_contract.py and DIRECT 087/088.
- Reuse native orchestration/reviewer with distinct read-only approved hash-bound architecture gate; integrate security/performance in the existing final code review alongside correctness.
- Do not create automated application performance/load/stress/benchmark tests unless the task user explicitly asks; functional tests of review mechanics required.
- Run mapped functional regressions and record real receipts and current source hashes, not fabricated independent reviews.

## Acceptance

- Genuine fresh independent maximum-qualified reviewer evidence includes provider/model/effort/session, dispatch and pinned final 107 code/test/receipt hashes.
- Both security and performance are audited before implementation for material design and in the existing final code review alongside correctness.
- Critical/high bypass, stale/replayed review, fake provenance, permission expansion, legacy and DIRECT issues are corrected or block acceptance.
- No default automated performance/load/stress/benchmark tests; functional workflow tests remain, and ordinary final reviewer does not spawn two routine specialists.
- Actual mapped regressions and final-hash re-review pass with no unresolved critical/high; if not, task remains pending.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_108`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_108`
