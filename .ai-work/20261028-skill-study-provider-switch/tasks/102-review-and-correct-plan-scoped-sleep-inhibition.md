---
task_id: "102"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "max"
reasoning_effort: "xhigh"
complexity: "high"
requirements: "R053"
dependencies: "101"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 102 — Review and correct plan-scoped sleep inhibition

## Objective

Independently review/correct the complete host power lease, OS limits and overnight readiness.

## Requirements covered

- R053

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: Independent acceptance boundary for one OS lifecycle feature.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: One continuous host lease is the feature boundary.
- Context that is genuinely shared by all subtasks:
- P053 research, relevant current host/coordinator code and actual prerequisite receipts.
- Concerns deliberately isolated into other TODOs:
- No unrelated task transcripts, global power configs or second plan.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read actual evidence
  - Pin task 101 code, hashes, tests and platform limitations.
- [ ] **S002** — Independent high-capability review
  - Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 102` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** — Correct defects
  - Fix critical/high native lifecycle, leak, concurrency, policy or cross-host defects.
- [ ] **S004** — Retest and record
  - Rerun mapped tests and record real independent review outcomes and unknown cases.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Independent review/correction, real OS tests and safety evidence.

## Out of scope

- No global OS power edits, fake input, hidden lid override, privilege escalation, sandbox bypass or unbounded model calls.

## Expected files

- skill/plan-and-execute/scripts/power_inhibit.py
- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/run_concise.py
- skill/plan-and-execute/scripts/lifecyclectl.py
- skill/plan-and-execute/scripts/jobctl.py
- skill/plan-and-execute/scripts/process_tree.py
- skill/plan-and-execute/references/LIFECYCLE.md
- skill/plan-and-execute/references/INSTALLATION.md
- skill/plan-and-execute/references/INSTALLATION.pt-BR.md
- test/optimization/plan_sleep_inhibition_self_test.py
- .github/workflows/ci.yml
- tools/run-repo-checks.js
- docs/research/20261028-skill-optimization/implementation/102-receipt.json
- docs/research/20261028-skill-optimization/implementation/102-outcome.md

## Dependencies

- 101

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/101-plan-scoped-sleep-inhibition.md and actual task101 code/receipts; never count research as implementation.
- Use docs/plans/20261028-skill-optimization/TASK_INPUTS.json and real max-qualified reviewer; preserve reviewed hashes.
- Verify Windows/macOS/Linux/WSL, concurrent leases, release, 310s validation and readiness; correct blocking issues.
- Write real task 102 review receipt/outcome and leave incomplete if unavailable.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance criteria

- Record genuine independent reviewer/provider/model/effort and reviewed hashes.
- Verify: Verified host-owned OS-native idle-sleep inhibitor is acquired before first RUNNING worker and stays active gaplessly across multiple TODOs/providers/reviews/validations over 300 seconds.
- Verify: Windows checked native thread or handle requests with correct lifetime, cleanup and screen-off allowance; account for Modern Standby DC and system policy.
- Verify: macOS caffeinate/IOKit assertion with correct release and documented lid/manual/battery limits.
- Verify: Linux logind/systemd inhibitor acquired/held/released; DBus absence and LidSwitchIgnoreInhibited default handled with no hidden lid override.
- Verify: WSL guest-only inhibitor never represents Windows-host protection; container/remote host ownership and sandbox restrictions reported accurately.
- Verify: Cancellation, reset, SIGTERM, SIGINT, success, failure, explicit pause and forced death release owned request; concurrent plans cannot cross-release.
- Verify: Resume after crash/reboot verifies fresh host and lease before dispatch and ignores stale PID/orphan status.
- Verify: Local ORCHESTRATED default-on and explicit opt-out; strict require-awake blocks before paid provider when unsupported and normal auto mode warns.
- Verify: No persistent OS power-setting changes, fake input, admin elevation, screen forcing, sandbox bypass or battery/thermal policy override.
- Verify: Preflight treats power, runner session survival, credentials, approvals, quota, network and durable resume as distinct readiness checks.
- Verify: Deterministic OS mocks, two-provider 310-second semantic validation, lifecycle regression and safe available CI/native smoke tests record actual hashes; no per-tick model calls.
- Verify: Real independent qualified reviewer corrects high/critical issues before 082; no invented execution evidence.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 101 has actual test evidence on the final reviewed hashes.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_102`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_102`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
