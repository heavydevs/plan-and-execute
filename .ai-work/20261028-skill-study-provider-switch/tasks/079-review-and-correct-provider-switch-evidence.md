---
task_id: "079"
status: "pending"
requirements: "R004,R006,R012,R019,R022,R023,R024,R030,R031,R034,R039,R042"
dependencies: "078"
allowed_related_task_reads: "none"
---

# 079 — Review and correct provider-switch evidence

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

In: Review and correct provider-switch evidence
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/pattern_runner_contract.py`, `test/optimization/provider_switch_078_self_test.py`, `skill/plan-and-execute/scripts/routing_telemetry.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `docs/research/20261028-skill-optimization/implementation/079-receipt.json`, `docs/research/20261028-skill-optimization/implementation/079-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Use only task 079 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/079-receipt.json.
- Dispatch an actual fresh maximum-qualified reviewer; record its real route and input hashes, then correct and revalidate every blocking finding.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance

- The reviewed implementation meets its original acceptance cases.
- Current input hashes, actual reviewer metadata and correction validation are preserved.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_079`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_079`
