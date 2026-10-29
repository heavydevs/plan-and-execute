---
task_id: "032"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,031"
allowed_related_task_reads: "none"
---

# 032 — Implement codex CLI, Agent SDK and schema adaptation

Objective: Separate Codex event-stream parsing from final-schema validation, retain explicit sandbox/approval contracts and make session reuse an opt-in same-provider operation.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/032-codex.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Parse bounded JSONL events independently from the final completion schema; reject truncated or missing terminal reports.
- [ ] **S003** Implement revised contract 2 — Bind optional session reuse to exact provider, repository and task identity; preserve ephemeral default.
- [ ] **S004** Implement revised contract 3 — Remove universal no-cache-write-cost assumptions from planned economics and use model-versioned reported usage.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement codex CLI, Agent SDK and schema adaptation
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `test/optimization/codex_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md`, `docs/research/20261028-skill-optimization/implementation/032-receipt.json`, `docs/research/20261028-skill-optimization/implementation/032-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/032-codex.md.
- Use only task 032 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/032-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Schema fixtures remain accepted by the adapter without weakening additionalProperties checks.
- Ephemeral default argv and composed static prefix remain stable.
- Malformed events, partial final JSON, a nonzero exit and a valid blocked report remain distinguishable.
- An unsupported sandbox/effort flag fails preflight instead of falling back to unrestricted execution.
- Cache and cost records distinguish reported usage from estimates and do not import outdated no-write-cost assumptions.
- A successful progress event followed by malformed final JSON cannot complete a task.
- A resume request cannot attach another repository session.
- Sandbox mismatch is an environmental or policy block, not a model capability escalation.
- Cache-write usage remains distinct from uncached input and cache reads.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_032`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_032`
