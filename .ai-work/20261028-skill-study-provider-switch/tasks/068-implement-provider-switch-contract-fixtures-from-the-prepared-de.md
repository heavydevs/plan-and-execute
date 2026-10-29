---
task_id: "068"
status: "pending"
requirements: "R002,R003,R004,R005,R006,R007,R012,R013,R014,R015,R016,R017,R018,R019,R020,R021,R022,R023,R024,R025,R026,R027,R028,R029,R030,R031,R032,R034,R037,R038,R039,R042,R044"
dependencies: "001,021,023,027,049,061,065"
allowed_related_task_reads: "none"
---

# 068 — Implement provider-switch contract fixtures from the prepared decision

Objective: Encode the prepared provider-switch decision as reusable configuration fixtures, baseline replay and expected outcomes; runtime changes belong to tasks070-080.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Encode all twelve original acceptance cases as fixtures with separate legacy behavior and expected opt-in results.
- [ ] **S003** Implement revised contract 2 — Cover no-op aliases, unavailable providers, phase state, insufficient budgets and attempt-bound sanitized capsules in the fake-provider inputs.
- [ ] **S004** Implement revised contract 3 — Assign runtime expectations to owners070-080 and verify that this fixture task makes no runner or configuration implementation claim.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement provider-switch contract fixtures from the prepared decision
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `test/optimization/provider_switch_handoff_self_test.py`, `docs/research/20261028-skill-optimization/implementation/068-receipt.json`, `docs/research/20261028-skill-optimization/implementation/068-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/068-provider-switch-handoff.md.
- Use only task 068 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/068-receipt.json.
- Task068 owns contract fixtures only. Tasks070-080 implement runtime behavior; do not duplicate their changes here.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 068 encodes the decision below as twelve-case fixtures and compatibility expectations only. Runtime/config/state/prompt changes are owned by 070, 072, 074, 076, 078 and 080, each with its following independent review.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- All twelve provider-switch acceptance cases have explicit inputs and expected outputs.
- Fixtures distinguish provider/phase identity, unavailable candidates, duplicate dispatches and bounded attempt reservation.
- Legacy replay remains separate from expected opt-in behavior; no runtime implementation is claimed by this fixture task.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_068`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_068`
