---
task_id: "077"
status: "pending"
requirements: "R004,R006,R017,R018,R019,R020,R021,R023,R029,R034,R039,R042"
dependencies: "076"
allowed_related_task_reads: "none"
---

# 077 — Review and correct bounded deterministic handoff and sanitation

Objective: Independently review, correct and revalidate the preceding provider-switch change against report068 and its assigned acceptance cases.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Obtain actual independent max-capability review evidence for the current diff.
- [ ] **S003** Implement change 2 — Correct blocking findings and rerun all assigned checks.
- [ ] **S004** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S005** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct bounded deterministic handoff and sanitation
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/assistant_triage.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `test/optimization/provider_switch_076_self_test.py`, `skill/plan-and-execute/scripts/provider_handoff.py`, `docs/research/20261028-skill-optimization/implementation/077-receipt.json`, `docs/research/20261028-skill-optimization/implementation/077-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Use only task 077 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/077-receipt.json.
- Dispatch an actual fresh maximum-qualified reviewer; record its real route and input hashes, then correct and revalidate every blocking finding.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance

- The reviewed implementation meets its original acceptance cases.
- Current input hashes, actual reviewer metadata and correction validation are preserved.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_077`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_077`
