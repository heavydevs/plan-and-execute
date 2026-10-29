---
task_id: "072"
status: "pending"
requirements: "R006,R012,R014,R016,R024,R030,R034"
dependencies: "071"
allowed_related_task_reads: "none"
---

# 072 — Implement effective rungs and provider-top detection

Objective: Normalize actual model and effort after config, snapshot and profile resolution and detect non-changing rungs without changing the default path.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Normalize actual model and effort after config, snapshot and profile resolution and detect non-changing rungs without changing the default path.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Implement effective rungs and provider-top detection
Out: Do not implement unrelated optimization backlog items.
Files: `docs/research/20261028-skill-optimization/outputs/072-effective-provider-top.json`, `docs/research/20261028-skill-optimization/topics/072-effective-provider-top.md`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/workload_routing.py`, `skill/plan-and-execute/scripts/model_routing_self_test.py`, `skill/plan-and-execute/scripts/workload_routing_self_test.py`, `skill/plan-and-execute/scripts/snapshot_runner_self_test.py`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 072.
- Expected runtime paths are candidate ownership boundaries, not a mandate to edit every file; the approved ADR controls the minimal diff.

## Acceptance

- Antigravity embedded-effort slugs and equal Claude strong/max model dispatches are covered by deterministic no-op tests.
- Empty tiers lift upward or record a skip; effective identity is derived from configuration, not vendor constants.
- Disabled-mode route sequences and argv goldens remain unchanged.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_072`
