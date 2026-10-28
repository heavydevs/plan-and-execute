---
task_id: "085"
status: "pending"
requirements: "R001,R003,R004,R005,R033,R034,R039,R041,R042,R043,R044"
dependencies: "084"
allowed_related_task_reads: "none"
---

# 085 — Review Generate and validate the implementation Plan 2

Objective: Independently challenge the preceding deliverable at the highest available model capability; approve only after every blocking finding is resolved.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Independently challenge the preceding deliverable at the highest available model capability; approve only after every blocking finding is resolved.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Review Generate and validate the implementation Plan 2
Out: Do not change product runtime or installed copies.
Files: `docs/research/20261028-skill-optimization/outputs/085-final-implementation-plan-review.json`, `docs/research/20261028-skill-optimization/reviews/085-final-implementation-plan-review.md`

## Guidance

- Resolve the strongest available concrete model from authenticated discovery; do not assume an alias or lower the review tier to save quota.
- Write findings and evidence only; the original author handles corrective edits before re-review.
- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 085.

## Acceptance

- The reviewer is a fresh real worker at max tier with the strongest supported effort and records its actual route.
- Input hashes match the reviewed files; no unresolved critical or high findings remain.
- An unavailable max reviewer pauses the gate; a lower model or simulated review cannot satisfy it.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_085`
