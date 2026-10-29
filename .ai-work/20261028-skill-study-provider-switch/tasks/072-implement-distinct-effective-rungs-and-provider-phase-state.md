---
task_id: "072"
status: "pending"
requirements: "R006,R012,R014,R016,R024,R030,R034"
dependencies: "019,021,055,071"
allowed_related_task_reads: "none"
---

# 072 — Implement distinct effective rungs and provider-phase state

Objective: Implement the assigned provider-switch contract from report068 and the original twelve-case acceptance matrix.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md, docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Implement change 1 — Collapse model/native-effort no-ops after profile/snapshot resolution.
- [ ] **S003** Implement change 2 — Record provider-local evidence and actual-dispatch identity before outcomes.
- [ ] **S004** Implement change 3 — Add regression tests for the corresponding original acceptance cases and preserve legacy behavior.
- [ ] **S005** Apply revised runtime contract 1 — Persist provider/phase-local functional evidence only after pinning the actual effective dispatch identity.
- [ ] **S006** Apply revised runtime contract 2 — Derive useful rungs after snapshot, profile, alias and native-effort resolution; no-op labels are not stronger routes.
- [ ] **S007** Apply revised runtime contract 3 — Define reset as explicit new evidence generation with retained audit history; do not inherit another provider's failures.
- [ ] **S008** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S009** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Implement distinct effective rungs and provider-phase state
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `test/optimization/provider_switch_072_self_test.py`, `skill/plan-and-execute/scripts/planctl.py`, `docs/research/20261028-skill-optimization/implementation/072-receipt.json`, `docs/research/20261028-skill-optimization/implementation/072-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Read docs/plans/20261028-skill-optimization/ACCEPTANCE_MATRIX.md.
- Use only task 072 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/072-receipt.json.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Use the normative blueprint in report068 for exact entry-rung, repeat, reset, byte-bound and budget semantics; record deviations before changing that contract.

## Acceptance

- Collapse model/native-effort no-ops after profile/snapshot resolution.
- Record provider-local evidence and actual-dispatch identity before outcomes.
- The targeted contract is validated through the production run_concise composition.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.
- Persist provider/phase-local functional evidence only after pinning the actual effective dispatch identity.
- Derive useful rungs after snapshot, profile, alias and native-effort resolution; no-op labels are not stronger routes.
- Define reset as explicit new evidence generation with retained audit history; do not inherit another provider's failures.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_072`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_072`
