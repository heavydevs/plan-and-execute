---
task_id: "040"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,039"
allowed_related_task_reads: "none"
---

# 040 — Implement trae Agent adapter

Objective: Preserve TRAE Agent as a distinct adapter with pinned CLI/tool contracts and owned trajectory artifacts; do not interpret the trajectory or IDE identity as a completion guarantee.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/040-trae.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Pin TRAE Agent identity and version separately from IDE products and backend model configuration.
- [ ] **S003** Implement revised contract 2 — Allocate owned per-attempt trajectory paths; redact before export and never scan unrelated user sessions.
- [ ] **S004** Implement revised contract 3 — Distinguish runner-created containers from attached user containers before cancellation or cleanup.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement trae Agent adapter
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `test/optimization/trae_self_test.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `docs/research/20261028-skill-optimization/implementation/040-receipt.json`, `docs/research/20261028-skill-optimization/implementation/040-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/040-trae.md.
- Use only task 040 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/040-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Golden command fixtures distinguish Trae Agent from unrelated executables.
- An invalid or missing terminal output cannot be replaced by a plausible trajectory message.
- A seeded credential in a trajectory is not included in model-facing evidence or publication artifacts.
- Quota failures are keyed to the configured backend/profile, not every Trae execution.
- Cleanup preserves active trajectory evidence and removes only registered stale artifacts.
- A stale trajectory from another attempt cannot satisfy completion.
- Cleanup refuses to destroy an attached user-owned container.
- Credential-like text in trajectory snippets is redacted before truncation.
- Missing backend configuration fails preflight without a semantic escalation.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_040`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_040`
