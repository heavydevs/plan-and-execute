---
task_id: "048"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,015,027,029,043"
allowed_related_task_reads: "none"
---

# 048 — Implement independent validation, evidence packets and failure classification

Objective: Bind validation evidence to exact code, task contract and executed argv; keep deterministic acceptance authoritative and make failure packets available to both production prompt paths.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/048-validation-evidence.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Bind check receipts to task contract, executed argv, source inputs and map/toolchain evidence; distinguish historical validity from current applicability.
- [ ] **S003** Implement revised contract 2 — Add negative tests proving each behavioral criterion fails without its implementation.
- [ ] **S004** Implement revised contract 3 — Pass the evidence packet through both legacy and composed prompt paths without changing the static prefix.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement independent validation, evidence packets and failure classification
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `test/optimization/validation_evidence_self_test.py`, `skill/plan-and-execute/references/WORKFLOW.md`, `docs/research/20261028-skill-optimization/implementation/048-receipt.json`, `docs/research/20261028-skill-optimization/implementation/048-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/048-validation-evidence.md.
- Use only task 048 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/048-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 048 owns independent-validation evidence and the missing evidence-packet prompt pointer. The optional cross-provider capsule itself belongs to 076/078.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- The composed prompt contains a valid evidence-packet pointer after a failed validation.
- A changed source/map/command invalidates a previously successful receipt.
- A valid success JSON with failing tests cannot complete the task.
- A repeated failure fingerprint is stable under timestamps/PIDs but changes for a genuinely different failure.
- A resumed completed worker checkpoint validates without unnecessary model redispatch.
- A log from another code digest or substituted command cannot satisfy acceptance.
- A forged completed report with no runner validation remains incomplete.
- Both prompt builders include only the assigned current evidence packet.
- A diagnostic suggestion cannot set failure class or completion state.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_048`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_048`
