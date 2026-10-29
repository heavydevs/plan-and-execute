---
task_id: "031"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "030"
allowed_related_task_reads: "none"
---

# 031 — Review and correct claude Code and Claude Agent SDK adapter

Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/030-claude.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Use a real fresh maximum-qualified code reviewer with the changed diff, report and acceptance evidence; do not send unrelated task histories.
- [ ] **S003** Implement change 2 — Correct every blocking finding or leave the gate incomplete with a recorded reason.
- [ ] **S004** Implement change 3 — Re-run declared checks after corrections and pin the final reviewed source state.
- [ ] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct claude Code and Claude Agent SDK adapter
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `test/optimization/claude_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md`, `docs/research/20261028-skill-optimization/implementation/031-receipt.json`, `docs/research/20261028-skill-optimization/implementation/031-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/030-claude.md.
- Use only task 031 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/031-receipt.json.
- Dispatch an actual fresh maximum-qualified reviewer; record its real route and input hashes, then correct and revalidate every blocking finding.
- Review the revision-2 alternatives, scope boundary and negative tests against the actual changed code; report unsupported cost/quality claims.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.

## Acceptance

- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_031`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_031`
