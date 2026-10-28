---
task_id: "002"
status: "pending"
requirements: "R002,R007,R008,R009,R032,R035,R038,R040"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 002 — Audit every skill mechanism and baseline

Objective: Trace entrypoints, scripts, references, state, tests and adapters; produce a code-evidence map and reproducible baseline without changing behavior.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Trace entrypoints, scripts, references, state, tests and adapters; produce a code-evidence map and reproducible baseline without changing behavior.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Audit every skill mechanism and baseline
Out: Do not change product runtime or installed copies.
Files: `docs/research/20261028-skill-optimization/outputs/002-whole-skill-audit.json`, `docs/research/20261028-skill-optimization/topics/002-whole-skill-audit.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 002.

## Acceptance

- Every tracked source file is read or has a justified classification and a symbol-level evidence entry.
- Baseline tests and routing simulations separate existing failures, environment limits and verified behavior.
- Run source fixture replay without user-global configuration.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_002`
