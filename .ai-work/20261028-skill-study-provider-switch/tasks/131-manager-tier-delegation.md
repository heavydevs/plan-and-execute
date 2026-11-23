---
task_id: "131"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R073"
dependencies: "088, 092, 100, 104, 106, 108, 116, 120, 130"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 131 — Implement manager-tier delegation for plan supervision decisions

## Objective

When the plan manager is below the floor of a supervisory decision (blocked task, plan/gate defect, replan, review conflict, manifest mutation), route it to a fresh qualified read-only worker without switching the root model or auto-editing the manifest.

## Requirements covered

- R073

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One supervisory-decision contract (config, decision gate, block record, surfacing, accounting) verified by one self-test; splitting it would duplicate the event-to-floor table.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Manager tier, supervisory decision gate, block record and diagnostic accounting share one event-to-floor contract verified by one self-test.
- Context that is genuinely shared by all subtasks:
- Assigned P067 research note, accepted 088/092/100/106 receipts and the affected routing, runner and watchdog sources only.
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

- [ ] **S001** — Read P067 research and accepted evidence
  - Read docs/research/20261028-skill-optimization/prepared-research/131-manager-tier-delegation.md and accepted 088/092/100/106 receipts; inspect only routingctl delegate, the run_isolated blocked path, watchdogctl and keepalivectl.
- [ ] **S002** — Add the configurable manager tier
  - Add routing_policy.manager_tier (auto|economy|standard|advanced|strong|max; auto = standard), validated in routing_config.py, kept by the catalog refresh, recorded in decisions and telemetry; never switch the root model.
- [ ] **S003** — Implement the supervisory decision entry point
  - Add routingctl.py supervise on top of delegate_decision mapping the seven events to leaf signals and floors; return decision, phase provider chain, minimal read-only brief and the compact result schema.
- [ ] **S004** — Write and surface diagnosis-request records
  - On a functional block write results/<task>-diagnosis-request.json once per blocker fingerprint; watchdogctl/keepalivectl surface it as diagnosis_requested and never dispatch, edit the manifest or resolve.
- [ ] **S005** — Keep availability and frontier out of diagnosis
  - Quota, credits, auth, environment, budget, timeout and unknown blocks write no record and spend nothing; frontier only by the two owner rules, never auto-dispatched; Codex credit exhaustion skips to Claude.
- [ ] **S006** — Enforce read-only dispatch and diagnostic accounting
  - Dispatch diagnoses only through the adapter-pinned read-only argv (skip providers without one) and account them as kind diagnostic in routing_telemetry rollups and delegation budgets.
- [ ] **S007** — Test, document and record evidence
  - Write test/optimization/manager_delegation_self_test.py with the nine P067 cases, update DELEGATION/WATCHDOG/MODEL_ROUTING/ROUTING_CONFIG.md, run the declared checks and record the 131 receipt and outcome.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Manager-tier config, routingctl supervise decision, diagnosis-request record, watchdog/keepalive surfacing and diagnostic accounting

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
- docs/research/20261028-skill-optimization/implementation/131-receipt.json
- docs/research/20261028-skill-optimization/implementation/131-outcome.md

## Dependencies

- 088
- 092
- 100
- 104
- 106
- 108
- 116
- 120
- 130

## Allowed related task definitions

- None

## Implementation guidance

- Only read docs/research/20261028-skill-optimization/prepared-research/131-manager-tier-delegation.md for this task; it fixes the event table, schemas and negative cases.
- Build on routingctl delegate_decision, select_route, frontier_policy, the availability classes and check_worker_result; add no second router, selector, watchdog or availability classifier.
- Diagnosis chain Codex > Claude (Sol 6.2 / Opus 5.5); implementation repair Antigravity > Codex > Claude only through task 091; unavailable providers are skipped without lowering the floor.
- Touch run_isolated.py only to write the diagnosis-request record on the blocked path and keepalivectl.py only to surface it; neither dispatches, edits the manifest or resolves a blocker.
- Run after the accepted writers of the shared files (088, 092, 100, 104, 106, 108, 116, 120, 130); rebase on their versions and run every self-test that imports a changed module.
- Use only task 131 inputs, checks and write scope in TASK_INPUTS.json; record actual receipts/outcomes and leave the task pending until verified.

## Acceptance criteria

- Sonnet 5.5 manager (standard) with a semantic blocked_task: supervise returns delegate to a read-only Opus 5.5 / Sol 6.2 analyst at strong/high with a failure-capsule brief and no root model switch.
- A Haiku 5.5 manager (economy) delegates every event above its tier; a manager at or above the event floor gets keep_root.
- With Codex credits exhausted the diagnosis chain skips Codex as availability and routes to Claude Opus 5.5; no escalation or capability failure is recorded.
- Quota, credits, auth, environment, budget, timeout and unknown-cause blocks return report_only: no diagnosis-request record, no diagnostic dispatch and no escalation.
- A repeated blocker fingerprint gives one record and one diagnosis, later calls return duplicate, and the per-task and per-plan diagnosis budget is bounded.
- Frontier (Fable 5.2 / Astra 6.2) is chosen for diagnosis only for extreme_architecture_review or after min_top_failures functional max/xhigh failures, and is never auto-dispatched.
- Runner, watchdog and keepalive never edit the manifest, resolve a blocker or dispatch a worker; resolution goes through task 091's lease-safe graph mutation.
- Diagnoses dispatch only through the adapter-pinned read-only argv; a provider without a proven read-only mode is skipped with a reason, although implementers run full-access.
- routing_policy.manager_tier accepts auto|economy|standard|advanced|strong|max (auto = standard), survives the catalog refresh, and the effective tier is recorded in decision, record and telemetry.
- Each diagnosis is accounted as kind diagnostic in routing_telemetry rollups and charged against the delegation token budget.
- A plan without routing_policy.manager_tier keeps runner, watchdog and keepalive output and exit codes byte-identical to the legacy behavior.
- test/optimization/manager_delegation_self_test.py covers these cases offline with no model call, network access or user-global configuration write.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_131`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_131`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
