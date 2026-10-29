---
task_id: "038"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,037"
allowed_related_task_reads: "none"
---

# 038 — Implement kimi Code CLI adapter

Objective: Make Kimi prompt-mode permission behavior an explicit versioned compatibility decision; reject unsupported safe-role invocations instead of silently deleting flags.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/038-kimi.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Version Kimi prompt and permission combinations; never repair an invocation by silently broadening permissions.
- [ ] **S003** Implement revised contract 2 — Bind any explicit resume to the exact task and repository, including saved permission state.
- [ ] **S004** Implement revised contract 3 — Disable advisory roles when a genuine read-only boundary cannot be established.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement kimi Code CLI adapter
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `test/optimization/kimi_self_test.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `docs/research/20261028-skill-optimization/implementation/038-receipt.json`, `docs/research/20261028-skill-optimization/implementation/038-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/038-kimi.md.
- Use only task 038 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/038-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Current fixtures reject --prompt combined with obsolete or mutually exclusive permission flags.
- Legacy fixtures keep their documented print-mode syntax instead of receiving current-only flags.
- A missing terminal report, malformed JSONL or interrupted stream cannot pass acceptance.
- Budget, transient and permanent errors are normalized only when the version contract establishes their meaning.
- Session identifiers and logs never introduce secrets into a shared handoff.
- Prompt plus obsolete permission flags yields a compatibility failure before model work.
- Fallback flag removal cannot change the authorized permission profile.
- Resume cannot inherit another task saved permissions.
- Native exit zero with missing completion schema is rejected.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_038`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_038`
