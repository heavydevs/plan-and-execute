---
task_id: "090"
status: "pending"
requirements: "R047"
dependencies: "089"
allowed_related_task_reads: "none"
---

# 090 — Review and correct avoid skill loading for routine commands and trivial changes

Objective: Independently review and correct avoid skill loading for routine commands and trivial changes using actual implementation and validation evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read implementation — Review the actual code, test results and receipt from task 089, not a previous conversation.
- [ ] **S002** Independent review — Dispatch a real fresh maximum-qualified reviewer and preserve provider, model, effort and reviewed hashes.
- [ ] **S003** Correct high-risk defects — Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** Rerun regressions — Run test/optimization/skill_activation_negatives_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** Record review — Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/090-receipt.json and docs/research/20261028-skill-optimization/implementation/090-outcome.md.

## Scope

In: Review and correct avoid skill loading for routine commands and trivial changes
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/agents/openai.yaml`, `skill/plan-and-execute/references/ROUTING.md`, `skill/validate-or-fix/SKILL.md`, `skill/plan-and-execute/references/routing-evals.json`, `test/optimization/skill_activation_negatives_self_test.py`, `docs/research/20261028-skill-optimization/implementation/090-receipt.json`, `docs/research/20261028-skill-optimization/implementation/090-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 090 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Use an actual fresh independent maximum-qualified reviewer; never fabricate model execution.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/090-receipt.json and docs/research/20261028-skill-optimization/implementation/090-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: Simple shell commands, one-file reads and trivial edits do not implicitly load the full skill.
- Verify: Explicit plan/lifecycle commands and genuine multi-workstream jobs still activate.
- Verify: Tiny discoverable metadata cost is acknowledged; there is no claim of zero skill-related tokens.
- Verify: Held-out host evaluations measure false positives/negatives and token impact, not keyword assertions alone.
- No unresolved critical/high finding or missing required reviewer may be marked complete.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_090`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_090`
