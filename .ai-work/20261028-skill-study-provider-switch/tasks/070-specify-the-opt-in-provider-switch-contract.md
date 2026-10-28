---
task_id: "070"
status: "pending"
requirements: "R006,R012,R013,R014,R015,R016,R017,R024,R025,R026,R027,R028,R030,R031,R037"
dependencies: "069,021,023,027,025"
allowed_related_task_reads: "none"
---

# 070 — Specify the opt-in provider-switch contract

Objective: Publish the reviewed provider-switch ADR, configuration schema, state transition table and tests before altering dispatch.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect assigned inputs — Record decisive source evidence without loading unrelated task history.
- [ ] **S002** Produce the bounded deliverable — Publish the reviewed provider-switch ADR, configuration schema, state transition table and tests before altering dispatch.
- [ ] **S003** Validate and checkpoint — Pass the mapped packet check and retain exact validation evidence.

## Scope

In: Specify the opt-in provider-switch contract
Out: Do not implement unrelated optimization backlog items.
Files: `docs/research/20261028-skill-optimization/outputs/070-switch-contract.json`, `docs/research/20261028-skill-optimization/topics/070-switch-contract.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/PROTOCOL.md and only the input paths listed in docs/plans/20261028-skill-optimization/TASK_INPUTS.json for task 070.

## Acceptance

- Decide declared versus effective chain, entry rung, class-specific retries and budget behavior for each phase.
- Choose handoff modes with a cost/risk matrix; new configuration defaults off and rejects unknown subkeys.
- Present the decision summary to the user before implementation; no confirmation is needed for reversible local edits.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_070`
