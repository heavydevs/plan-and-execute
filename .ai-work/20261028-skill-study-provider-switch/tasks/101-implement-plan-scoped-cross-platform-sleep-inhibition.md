---
task_id: "101"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R053"
dependencies: "019, 055, 057, 067, 094, 100"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 101 — Implement plan-scoped cross-platform sleep inhibition

## Objective

Implement a host-owned OS-native sleep inhibitor for the complete local RUNNING ORCHESTRATED plan.

## Requirements covered

- R053

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One verifiable continuous power-lease contract across many workers and tests.

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

- [ ] **S001** — Inspect baseline
  - Read P053 and only relevant current lifecycle/job/runner code and 099/100 interfaces.
- [ ] **S002** — Implement native lease
  - Add host-owned Windows/macOS/Linux inhibitor and WSL/container boundary with checked acquire/status/release.
- [ ] **S003** — Own full plan lifecycle
  - Hold across worker/provider changes, and release on all terminal/pause paths; resume with new lease.
- [ ] **S004** — Implement night-readiness
  - Local auto-on, opt-out, strict require-awake, honest battery/permissions/credential warnings.
- [ ] **S005** — Test and document
  - Run mapped mocks/safe platform probes, update bilingual docs and record source hashes/real outcomes.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Native host power guard, supervisor lifecycle, strict unattended preflight, docs and CI.

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
- docs/research/20261028-skill-optimization/implementation/101-receipt.json
- docs/research/20261028-skill-optimization/implementation/101-outcome.md

## Dependencies

- 019
- 055
- 057
- 067
- 094
- 100

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/101-plan-scoped-sleep-inhibition.md, reuse lifecycle/job/watchdog/progress features already planned; do not duplicate them.
- Implement one native host-owned lease across the entire local RUNNING plan; keep display sleep and OS safety.
- Offer auto-on, opt-out, strict overnight require-awake and honest unsupported/policy/status diagnostics.
- Implement safe platform/CI tests and record real source/test hashes in task 101 receipt/outcome.

## Acceptance criteria

- Verified host-owned OS-native idle-sleep inhibitor is acquired before first RUNNING worker and stays active gaplessly across multiple TODOs/providers/reviews/validations over 300 seconds.
- Windows checked native thread or handle requests with correct lifetime, cleanup and screen-off allowance; account for Modern Standby DC and system policy.
- macOS caffeinate/IOKit assertion with correct release and documented lid/manual/battery limits.
- Linux logind/systemd inhibitor acquired/held/released; DBus absence and LidSwitchIgnoreInhibited default handled with no hidden lid override.
- WSL guest-only inhibitor never represents Windows-host protection; container/remote host ownership and sandbox restrictions reported accurately.
- Cancellation, reset, SIGTERM, SIGINT, success, failure, explicit pause and forced death release owned request; concurrent plans cannot cross-release.
- Resume after crash/reboot verifies fresh host and lease before dispatch and ignores stale PID/orphan status.
- Local ORCHESTRATED default-on and explicit opt-out; strict require-awake blocks before paid provider when unsupported and normal auto mode warns.
- No persistent OS power-setting changes, fake input, admin elevation, screen forcing, sandbox bypass or battery/thermal policy override.
- Preflight treats power, runner session survival, credentials, approvals, quota, network and durable resume as distinct readiness checks.
- Deterministic OS mocks, two-provider 310-second semantic validation, lifecycle regression and safe available CI/native smoke tests record actual hashes; no per-tick model calls.
- Real independent qualified reviewer corrects high/critical issues before 082; no invented execution evidence.
- A detached jobctl supervisor holds its own job-scoped OS request until the job exits; runner death during supervised validation leaves no sleep gap.
- Each sleep request is released only by its owner.
- On Windows the request is held on a dedicated thread in the long-lived runner (run_concise), not in a helper that exits.
- A keepalive relaunch acquires a fresh request before dispatching.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_101`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_101`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
