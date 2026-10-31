---
task_id: "094"
status: "pending"
requirements: "R049"
dependencies: "093"
allowed_related_task_reads: "none"
---

# 094 — Review and correct verify authorized unsandboxed access for implementing agents

Objective: Independently review and correct verify authorized unsandboxed access for implementing agents using actual implementation and validation evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read implementation — Review the actual code, test results and receipt from task 093, not a previous conversation.
- [ ] **S002** Independent review — Dispatch a real fresh maximum-qualified reviewer and preserve provider, model, effort and reviewed hashes.
- [ ] **S003** Correct high-risk defects — Correct critical/high findings or leave the task pending with evidence.
- [ ] **S004** Rerun regressions — Run test/optimization/full_access_delegation_self_test.py and all feature acceptance and negative cases through mapped validation.
- [ ] **S005** Record review — Record actual review/validation results in docs/research/20261028-skill-optimization/implementation/094-receipt.json and docs/research/20261028-skill-optimization/implementation/094-outcome.md.

## Scope

In: Review and correct verify authorized unsandboxed access for implementing agents
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/configure.py`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/references/DELEGATION.md`, `skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md`, `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md`, `skill/plan-and-execute/references/ASSISTANTS.md`, `test/optimization/full_access_delegation_self_test.py`, `docs/research/20261028-skill-optimization/implementation/094-receipt.json`, `docs/research/20261028-skill-optimization/implementation/094-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 094 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Use an actual fresh independent maximum-qualified reviewer; never fabricate model execution.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/094-receipt.json and docs/research/20261028-skill-optimization/implementation/094-outcome.md; do not mark a pending task done without validation.

## Acceptance

- Record a real fresh independent reviewer route and exact reviewed input hashes.
- Verify: An authorized delegated implementer can access permitted loopback services and required paths.
- Verify: Provider flags are version-qualified, and effective permission is actually verified.
- Verify: Host-enforced restrictions cause an actionable pause, not an unsafe bypass or false success.
- Verify: Observers remain genuinely read-only or tool-less, rather than gaining source writes.
- Verify: Threats from unrestricted commands are documented, with consent and no credential leakage.
- No unresolved critical/high finding or missing required reviewer may be marked complete.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_094`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_094`
