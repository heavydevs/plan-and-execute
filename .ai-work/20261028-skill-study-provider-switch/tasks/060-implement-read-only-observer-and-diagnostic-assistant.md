---
task_id: "060"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,049,059"
allowed_related_task_reads: "none"
---

# 060 — Implement read-only observer and diagnostic assistant

Objective: Keep observation deterministic by default and invoke one bounded, genuinely read-only advisory pass only for novel ambiguity; treat its output as expiring untrusted data.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/060-advisory-observer.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Invoke advice only for a new unresolved anomaly and cap attempts, input/output size and permitted tools.
- [ ] **S003** Implement revised contract 2 — Redact before truncation and bind suggestions to evidence generation; consume once as unverified data.
- [ ] **S004** Implement revised contract 3 — Skip advisory routes lacking proven read-only enforcement while preserving deterministic monitoring.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement read-only observer and diagnostic assistant
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/observer.py`, `skill/plan-and-execute/scripts/assistant_triage.py`, `test/optimization/advisory_observer_self_test.py`, `skill/plan-and-execute/references/ASSISTANTS.md`, `docs/research/20261028-skill-optimization/implementation/060-receipt.json`, `docs/research/20261028-skill-optimization/implementation/060-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/060-advisory-observer.md.
- Use only task 060 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/060-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Clear deterministic errors invoke no advisory model.
- A planted Authorization header or long secret split at a prior slice boundary is redacted before prompt construction.
- Unknown evidence IDs, extra JSON fields, non-finite confidence and oversized hypotheses are rejected.
- Unavailable cheap observer falls back only to another allowed restricted observer, otherwise skips.
- Advice cannot mutate route/status and expires after its intended attempt.
- A healthy run and repeated identical anomaly trigger no extra model calls.
- A token spanning excerpt boundaries is removed before serialization.
- A suggestion that requests commands, writes or status changes is rejected as data outside its role.
- An old-generation suggestion cannot affect a new attempt.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_060`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_060`
