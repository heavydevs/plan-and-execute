---
task_id: "102"
status: "pending"
requirements: "R053"
dependencies: "101"
allowed_related_task_reads: "none"
---

# 102 — Review and correct plan-scoped sleep inhibition

Objective: Independently review/correct the complete host power lease, OS limits and overnight readiness.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read actual evidence — Pin task 101 code, hashes, tests and platform limitations.
- [ ] **S002** Independent high-capability review — Use real fresh qualified reviewer with provider/model/effort and reviewed hashes.
- [ ] **S003** Correct defects — Fix critical/high native lifecycle, leak, concurrency, policy or cross-host defects.
- [ ] **S004** Retest and record — Rerun mapped tests and record real independent review outcomes and unknown cases.

## Scope

In: Independent review/correction, real OS tests and safety evidence.
Out: No global OS power edits, fake input, hidden lid override, privilege escalation, sandbox bypass or unbounded model calls.
Files: `skill/plan-and-execute/scripts/power_inhibit.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/run_concise.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/process_tree.py`, `skill/plan-and-execute/references/LIFECYCLE.md`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `test/optimization/plan_sleep_inhibition_self_test.py`, `.github/workflows/ci.yml`, `tools/run-repo-checks.js`, `docs/research/20261028-skill-optimization/implementation/102-receipt.json`, `docs/research/20261028-skill-optimization/implementation/102-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/101-plan-scoped-sleep-inhibition.md and actual task101 code/receipts; never count research as implementation.
- Use docs/plans/20261028-skill-optimization/TASK_INPUTS.json and real max-qualified reviewer; preserve reviewed hashes.
- Verify Windows/macOS/Linux/WSL, concurrent leases, release, 310s validation and readiness; correct blocking issues.
- Write real task 102 review receipt/outcome and leave incomplete if unavailable.

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

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_102`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_102`
