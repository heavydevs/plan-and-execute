---
task_id: "080"
status: "pending"
requirements: "R005,R006,R012,R028,R029,R031,R033,R034,R035,R037,R045"
dependencies: "065,079"
allowed_related_task_reads: "none"
---

# 080 — Complete provider-switch documentation, replay and cost evidence

Objective: Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md, docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Run all twelve original acceptance cases and preserve disabled-mode compatibility.
- [ ] **S003** Implement change 2 — Report reachability and duplicate dispatches separately from unmeasured live quality/cost.
- [ ] **S004** Implement change 3 — Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** Apply revised runtime contract 1 — Compare counterfactual dispatch counts on the original twelve cases; do not present replay as measured model quality or dollar savings.
- [ ] **S006** Apply revised runtime contract 2 — Document account-dependent quota, conditional effort capabilities, fallback-disabled behavior and unverified platforms.
- [ ] **S007** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S008** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Complete provider-switch documentation, replay and cost evidence
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routing_telemetry.py`, `tools/skill_benchmark.py`, `test/optimization/provider_switch_080_self_test.py`, `skill/plan-and-execute/references/ROUTING_CONFIG.md`, `skill/plan-and-execute/references/MODEL_ROUTING.md`, `skill/plan-and-execute/references/WORKFLOW.md`, `skill/plan-and-execute/references/PLAN_SPEC.md`, `README.md`, `README.pt-BR.md`, `CHANGELOG.md`, `docs/research/20261028-skill-optimization/implementation/080-receipt.json`, `docs/research/20261028-skill-optimization/implementation/080-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 080 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/080-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.

## Acceptance

- Run all twelve original acceptance cases and preserve disabled-mode compatibility.
- Report reachability and duplicate dispatches separately from unmeasured live quality/cost.
- The targeted contract is validated through the production run_concise composition.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.
- Compare counterfactual dispatch counts on the original twelve cases; do not present replay as measured model quality or dollar savings.
- Document account-dependent quota, conditional effort capabilities, fallback-disabled behavior and unverified platforms.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_080`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_080`
