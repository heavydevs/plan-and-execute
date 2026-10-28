---
task_id: "078"
status: "pending"
requirements: "R006,R012,R019,R022,R023,R024,R030,R031,R034"
dependencies: "075,077"
allowed_related_task_reads: "none"
---

# 078 — Integrate handoff into both worker prompt paths

Objective: Append only the current handoff after deterministic failure evidence in raw and concise runners while preserving static-prefix identity.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Append only the current handoff after deterministic failure evidence in raw and concise runners while preserving static-prefix identity.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Integrate handoff into both worker prompt paths
Out: Do not implement unrelated optimization backlog items.
Files: `docs/research/20261028-skill-optimization/outputs/078-handoff-prompt-integration.json`, `docs/research/20261028-skill-optimization/topics/078-handoff-prompt-integration.md`, `skill/plan-and-execute/scripts/runner_contract.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/provider_self_test.py`, `skill/plan-and-execute/scripts/progress_runner_self_test.py`, `skill/plan-and-execute/scripts/artifact_concision_self_test.py`, `skill/plan-and-execute/references/completion-report.schema.json`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 078.
- Expected runtime paths are candidate ownership boundaries, not a mandate to edit every file; the approved ADR controls the minimal diff.

## Acceptance

- Pass plan_dir into failure_context or record an explicit justified deferral; evidence paths reach the next worker.
- A handoff applies to one next attempt only; stale capsules cannot alter class, route or status.
- Codex strict schemas, Antigravity schema conversion, design notes and pattern hooks retain their existing contracts.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_078`
