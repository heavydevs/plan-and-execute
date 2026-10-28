---
task_id: "084"
status: "pending"
requirements: "R001,R003,R004,R005,R033,R034,R039,R041,R042,R043,R044"
dependencies: "083"
allowed_related_task_reads: "none"
---

# 084 — Generate and validate the implementation Plan 2

Objective: Create a native resumable Plan 2 from the reviewed remaining backlog, with bounded TODOs, source traceability, routes and mapped acceptance tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Create a native resumable Plan 2 from the reviewed remaining backlog, with bounded TODOs, source traceability, routes and mapped acceptance tests.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Generate and validate the implementation Plan 2
Out: Do not change product runtime or installed copies.
Files: `docs/research/20261028-skill-optimization/outputs/084-final-implementation-plan.json`, `docs/research/20261028-skill-optimization/topics/084-final-implementation-plan.md`, `docs/plans/20261028-skill-optimization/PLAN2_SPEC.json`, `docs/plans/20261028-skill-optimization/FINAL_PLAN_INPUT.md`, `docs/plans/20261028-skill-optimization/PLAN2_MATERIALIZATION.json`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 084.
- The worker writes the durable spec and handoff; the orchestrator materializes and audits Plan 2 outside the worker before accepting this task.

## Acceptance

- Plan 2 passes planctl, studyctl and service-map audits against the post-Plan-1 code fingerprint.
- Keep Plan 2 inactive until handoff; preserve its evidence outside disposable Plan 1 directories.
- Each Plan 2 implementation task has a maximum-capability review gate; no completed Plan 1 work becomes a new TODO.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_084`
