---
task_id: "132"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R073"
dependencies: "131"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 132 — Independently review manager-tier delegation for plan supervision

## Objective

Independently review and correct manager-tier supervisory delegation: event floors, read-only boundary, availability exclusion, dedup budget, frontier rules and legacy compatibility on the final 131 hashes.

## Requirements covered

- R073

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One independent final-hash correction gate for the 131 supervisory-decision contract.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One reviewer context holds the final 131 decision gate, block record and tests needed to judge and correct them together.
- Context that is genuinely shared by all subtasks:
- Assigned P067 research note, final 131 code, tests and receipts only.
- Concerns deliberately isolated into other TODOs:
- Other task files, complete repo scans, historic chat and unrelated sources.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read final 131 evidence
  - Read P067 research and only the actual final 131 code, tests and receipts; review their SHA hashes.
- [ ] **S002** — Dispatch a fresh max-qualified review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 132` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** — Run adversarial supervision probes
  - Probe root model switch, availability as capability, duplicate fingerprints, budget exhaustion, frontier without repeated failure, write-capable diagnosis argv, auto manifest edits and legacy plans.
- [ ] **S004** — Fix blockers and record the review
  - Fix or reopen 131 for blocking defects, rerun focused tests; record the genuine reviewer route, source hashes and decisions.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independently review manager-tier delegation, read-only diagnosis, availability exclusion and legacy compatibility

## Out of scope

- No root model switch, automatic manifest edit or resolution, automatic frontier dispatch, second router or watchdog, or live model call in tests.

## Expected files

- skill/plan-and-execute/scripts/routingctl.py
- skill/plan-and-execute/scripts/routing_config.py
- skill/plan-and-execute/scripts/watchdogctl.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/keepalivectl.py
- skill/plan-and-execute/scripts/routing_telemetry.py
- skill/plan-and-execute/references/DELEGATION.md
- skill/plan-and-execute/references/WATCHDOG.md
- skill/plan-and-execute/references/MODEL_ROUTING.md
- skill/plan-and-execute/references/ROUTING_CONFIG.md
- test/optimization/manager_delegation_self_test.py
- docs/research/20261028-skill-optimization/implementation/132-receipt.json
- docs/research/20261028-skill-optimization/implementation/132-outcome.md

## Dependencies

- 131

## Allowed related task definitions

- None

## Implementation guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/131-manager-tier-delegation.md for this task; it fixes the event table, schemas and negative cases.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Review order Codex > Claude (Sol 6.2 xhigh, then Opus 5.5 xhigh); Codex credit exhaustion is availability and skips to Claude without escalation.
- Use only task 132 inputs, checks and write scope in TASK_INPUTS.json; record actual receipts/outcomes and leave the task pending until verified.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- A real fresh max-qualified reviewer approves the final 131 source/test/receipt hashes with dispatch provenance.
- The S003 probes pass: root model switch, availability as capability, duplicate fingerprints, budget exhaustion, frontier without repeated failure, write-capable diagnosis argv, auto manifest edits, legacy plans.
- High/critical findings are fixed and re-reviewed on the final hashes.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every acceptance criterion of task 131 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_132`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_132`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
