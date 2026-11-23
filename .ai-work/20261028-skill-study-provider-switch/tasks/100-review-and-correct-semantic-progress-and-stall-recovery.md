---
task_id: "100"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R052"
dependencies: "099"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 100 — Review and correct semantic progress and stall recovery

## Objective

Independently review and correct semantic-progress instrumentation, honest percentage reporting and safe evidence-based stall recovery using actual runtime evidence.

## Requirements covered

- R052

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: Independent acceptance and correction for one end-to-end implementation seam.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One vertical end-to-end progress-and-repair outcome, followed by independently verified correction.
- Context that is genuinely shared by all subtasks:
- Only the P052 contract, current source and relevant validated evidence.
- Concerns deliberately isolated into other TODOs:
- Do not duplicate preceding monitoring work or import past unrelated task transcripts.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read actual implementation and evidence
  - Inspect task 099 code, test receipts, source hashes and limitations; never reuse unverified research as test evidence.
- [ ] **S002** — Run independent maximum-qualified review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 100` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings. Focus: semantics, percent math, route/permission guards, negative cases.
- [ ] **S003** — Fix critical and high defects
  - Correct confirmed findings inside the authorized scope or leave the review pending with a recorded blocker.
- [ ] **S004** — Rerun mapped acceptance
  - Independently rerun the complete new test and affected progress/job/validate/routing regressions through resource monitoring.
- [ ] **S005** — Record independent review evidence
  - Write task 100 review receipt/outcome with provider/model/effort, hashes, actual checks and unresolved findings.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independent review and correction of semantic progress/recovery and documented acceptance evidence.

## Out of scope

- No second planning engine, duplicate watcher or every-tick LLM calls.
- No unauthorized writes, provider login, destructive restart or ignoring host policy.

## Expected files

- skill/plan-and-execute/scripts/progress_signal.py
- skill/plan-and-execute/scripts/progress_watch.py
- skill/plan-and-execute/scripts/resource_watch.py
- skill/plan-and-execute/scripts/service_map.py
- skill/plan-and-execute/scripts/jobctl.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/validatectl.py
- skill/plan-and-execute/scripts/routingctl.py
- skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md
- skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md
- skill/plan-and-execute/references/VALIDATION_WORKLOADS.md
- test/optimization/semantic_progress_recovery_self_test.py
- docs/research/20261028-skill-optimization/implementation/100-receipt.json
- docs/research/20261028-skill-optimization/implementation/100-outcome.md

## Dependencies

- 099

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/099-semantic-progress-recovery.md and task 099's actual code/test receipts; never treat this prepared research as runtime evidence.
- Follow task 100 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json; dispatch a genuinely independent qualified reviewer and pin reviewed hashes.
- Validate semantic-vs-liveness behavior, truthful percentages, safe ownership and authorized provider routing; correct critical/high findings.
- Record actual review and tests in docs/research/20261028-skill-optimization/implementation/100-receipt.json and docs/research/20261028-skill-optimization/implementation/100-outcome.md; pending unless verified.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Record a fresh independent maximum-qualified reviewer, effort/provider and exact reviewed source hashes.
- Verify: Design-anticipated validation >300s reuses an existing reliable counter/probe or adds minimal instrumentation before starting; short checks remain fast and untouched.
- Verify: Unexpected validation >300s without reliable progress raises a bounded instrumentation-gap diagnostic, never fabricated retrospective progress or uncontrolled edits to the running process.
- Verify: Semantic progress advances only for trusted increasing completed-work/stage checkpoints; timestamps, changing generic output, constant heartbeat, CPU busy loops and unrelated file activity cannot perpetually renew it.
- Verify: A valid long-running validation with increasing verified units/checkpoints continues beyond five minutes, limited only by a separate explicit hard ceiling or user cancellation.
- Verify: With a known stable per-stage total, percentage is correct and labeled to that stage; unknown totals remain indeterminate and a global percentage is never guessed or reaches 100 before success.
- Verify: At 300 seconds since last trusted semantic advancement, capture bounded redacted process/dependency/diagnostic evidence and distinguish semantic defect, environmental fault, explicit quiet window and unknown cause.
- Verify: A confirmed semantic code stall routes an authorized stronger eligible implementer, stops only owned processes, preserves completed checkpoints, changes code and reruns fresh mapped validation.
- Verify: Environmental, quota, auth, permission, unknown-owner, unknown-cause and configured hard-ceiling failures do not trigger stronger model execution or duplicate a live job.
- Verify: DIRECT validate-only remains read-only and plan-free; authorized DIRECT repair and ORCHESTRATED retries share the monitoring engine, attempts, source hashes, budgets and cancellation guards.
- Verify: Tests cover simulated 299/300/301-second boundaries, stage resets/replayed counters, process descendants, crash/restart, dependency health, safe probes, and no per-tick LLM cost.
- No unresolved critical/high finding or missing mapped test evidence may be marked complete.
- Verify: A confirmed stall raises effort first on the same eligible route, then the next tier up to max; frontier is never chosen for implementation repair.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 099 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_100`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_100`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
