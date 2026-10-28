---
task_id: "060"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "005"
allowed_related_task_reads: "none"
---

# 060 — Research Read-only observer and diagnostic assistant

Objective: Produce an evidence-backed optimization decision for read-only observer and diagnostic assistant, including alternatives, cost, quality risk and an executable evaluation.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Produce an evidence-backed optimization decision for read-only observer and diagnostic assistant, including alternatives, cost, quality risk and an executable evaluation.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Research Read-only observer and diagnostic assistant
Out: Do not change product runtime or installed copies.
Files: `docs/research/20261028-skill-optimization/outputs/060-advisory-observer.json`, `docs/research/20261028-skill-optimization/topics/060-advisory-observer.md`

## Guidance

- Verify least-privilege tool restrictions, schema validation and untrusted advice boundaries.
- Compare deterministic monitoring with event-triggered model diagnosis and cheap fallback chains.
- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 060.

## Acceptance

- Check official documentation and code for version-sensitive behavior and include numbered sources with access dates.
- Compare the current design with at least one alternative; quantify or mark unknown costs without inventing savings.
- Classify each conclusion as verified or inference and specify deterministic tests for every proposed change.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_060`
