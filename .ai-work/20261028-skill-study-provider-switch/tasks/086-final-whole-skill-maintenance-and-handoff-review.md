---
task_id: "086"
status: "pending"
requirements: "R001,R004,R006,R008,R011,R012,R033,R034,R035,R036,R039,R040,R041,R042,R043,R045"
dependencies: "085"
allowed_related_task_reads: "none"
---

# 086 — Final whole-skill maintenance and handoff review

Objective: Review the complete Plan 1 diff and Plan 2 handoff at maximum capability, record real test limits and publish the Brazilian Portuguese completion report.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Review the complete Plan 1 diff and Plan 2 handoff at maximum capability, record real test limits and publish the Brazilian Portuguese completion report.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Final whole-skill maintenance and handoff review
Out: Do not change product runtime or installed copies.
Files: `docs/research/20261028-skill-optimization/outputs/086-final-whole-skill-review.json`, `docs/research/20261028-skill-optimization/reviews/086-final-whole-skill-review.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 086.

## Acceptance

- Trace every changed flow, schema, route, cleanup path and reference; resolve all blocking findings.
- Revalidate Plan 2 after source changes, report Windows and real-provider limits, and leave commit/push/publication awaiting confirmation.
- This is the last Plan 1 TODO; its report does not claim unfinished research or authenticated validation.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_086`
