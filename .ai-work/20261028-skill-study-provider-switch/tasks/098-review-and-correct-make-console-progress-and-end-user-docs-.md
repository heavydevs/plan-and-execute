---
task_id: "098"
status: "pending"
requirements: "R051"
dependencies: "097"
allowed_related_task_reads: "none"
---

# 098 — Review and correct make console, progress and end-user docs concise and precise

Objective: Independently review and correct make console, progress and end-user docs concise and precise using actual implementation and validation evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read implementation — Review the actual code, test results and receipt from task 097, not a previous conversation.
- [ ] **S002** Independent review — Dispatch a real fresh maximum-qualified reviewer and preserve provider, model, effort and reviewed hashes.
- [ ] **S003** Correct high-risk defects — Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** Rerun regressions — Run test/optimization/concise_communication_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** Record review — Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/098-receipt.json and docs/research/20261028-skill-optimization/implementation/098-outcome.md.

## Scope

In: Review and correct make console, progress and end-user docs concise and precise
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/references/USER_COMMUNICATION.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `skill/plan-and-execute/references/ARTIFACT_WRITING.md`, `skill/plan-and-execute/scripts/process_io.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `skill/validate-or-fix/references/OPERATIONS.md`, `test/optimization/concise_communication_self_test.py`, `test/optimization/concise_communication_self_test.py`, `docs/research/20261028-skill-optimization/implementation/098-receipt.json`, `docs/research/20261028-skill-optimization/implementation/098-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 098 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Use an actual fresh independent maximum-qualified reviewer; never fabricate model execution.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/098-receipt.json and docs/research/20261028-skill-optimization/implementation/098-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: A one-step command returns the result and necessary next action, not a verbose status essay.
- Verify: Technical answers lead with a precise answer and retain commands, constraints, risk and error explanation when material.
- Verify: Do not restate earlier concepts unless necessary for the present decision, apparent confusion or explicit user request.
- Verify: User-facing bytes/tokens fall without losing correct steps, safety warnings, machine output or diagnostic evidence.
- Verify: The tone respects adult autistic users, avoids overgeneralization and supports individual preference and detail expansion.
- Verify: Independent test and human feedback verify non-inferior comprehension, accuracy and completeness, not word count alone.
- No unresolved critical/high finding or missing required reviewer may be marked complete.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_098`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_098`
