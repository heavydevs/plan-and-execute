---
task_id: "036"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,033,035"
allowed_related_task_reads: "none"
---

# 036 — Implement qwen Code headless adapter

Objective: Add a versioned Qwen headless contract with explicit security and total-run budgets, and prevent native goal/retry loops from bypassing the orchestrator policy.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/036-qwen.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Do not treat Qwen safe-mode or max-tool-calls zero as a read-only or schema-free mode.
- [ ] **S003** Implement revised contract 2 — Bound or disable inherited unattended retries and native goal continuation under the managed runner.
- [ ] **S004** Implement revised contract 3 — Classify native wall/tool/turn budget exits separately from semantic, permission and environment failures.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement qwen Code headless adapter
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `test/optimization/qwen_self_test.py`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `docs/research/20261028-skill-optimization/implementation/036-receipt.json`, `docs/research/20261028-skill-optimization/implementation/036-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/036-qwen.md.
- Use only task 036 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/036-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Replay JSON and JSONL fixtures with interleaved tool messages, malformed records and missing terminal results.
- Budget/turn exhaustion is recorded separately from semantic failure and transient availability.
- A read-only fake/qualified command cannot select shell/write/edit tools outside the allowlist.
- Large output is drained without deadlock; cancellation stops owned descendants.
- Unsupported schema or sandbox flags fail closed with an actionable version reason.
- Safe-mode cannot silently disable the required sandbox and still pass preflight.
- An inherited indefinite-retry opt-in is removed or rejected under bounded runner policy.
- Budget exit 55 and turn-cap exit 53 are fixture-versioned, not generic semantic failures.
- Truncated streaming output cannot become a successful completion report.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_036`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_036`
