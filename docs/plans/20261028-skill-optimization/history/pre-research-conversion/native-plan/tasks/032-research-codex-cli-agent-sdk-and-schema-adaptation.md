---
task_id: "032"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "005"
allowed_related_task_reads: "none"
---

# 032 — Research Codex CLI, Agent SDK and schema adaptation

Objective: Produce an evidence-backed optimization decision for codex cli, agent sdk and schema adaptation, including alternatives, cost, quality risk and an executable evaluation.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Produce an evidence-backed optimization decision for codex cli, agent sdk and schema adaptation, including alternatives, cost, quality risk and an executable evaluation.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Research Codex CLI, Agent SDK and schema adaptation
Out: Do not change product runtime or installed copies.
Files: `docs/research/20261028-skill-optimization/outputs/032-codex.json`, `docs/research/20261028-skill-optimization/topics/032-codex.md`

## Guidance

- Verify ephemeral runs, exec resume/fork, required nullable fields and current sandbox flags.
- Compare native compaction with short artifact handoffs using pinned CLI evidence.
- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 032.

## Acceptance

- Check official documentation and code for version-sensitive behavior and include numbered sources with access dates.
- Compare the current design with at least one alternative; quantify or mark unknown costs without inventing savings.
- Classify each conclusion as verified or inference and specify deterministic tests for every proposed change.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_032`
