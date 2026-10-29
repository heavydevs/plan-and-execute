---
task_id: "076"
status: "pending"
requirements: "R006,R017,R018,R019,R020,R021,R023,R029,R034"
dependencies: "071,049,061"
allowed_related_task_reads: "none"
---

# 076 — Implement validated, redacted handoff generation

Objective: Generate bounded unverified handoff from checked evidence and optional worker data, with a deterministic fallback when the prior provider cannot respond.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Generate bounded unverified handoff from checked evidence and optional worker data, with a deterministic fallback when the prior provider cannot respond.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Implement validated, redacted handoff generation
Out: Do not implement unrelated optimization backlog items.
Files: `docs/research/20261028-skill-optimization/outputs/076-handoff-generation.json`, `docs/research/20261028-skill-optimization/topics/076-handoff-generation.md`, `skill/plan-and-execute/scripts/provider_handoff.py`, `skill/plan-and-execute/scripts/provider_handoff_self_test.py`, `skill/plan-and-execute/scripts/assistant_triage.py`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 076.
- Expected runtime paths are candidate ownership boundaries, not a mandate to edit every file; the approved ADR controls the minimal diff.

## Acceptance

- Redact sk-token and Authorization fixtures before truncation; reject ungrounded paths, commands and subtask IDs.
- Handle crash, timeout, invalid report and exhausted quota without another required provider call.
- The selected a/b/c/d alternative is implemented with its reviewed size, expiry and privacy contract.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_076`
