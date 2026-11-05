---
task_id: "101"
status: "pending"
requirements: "R053"
dependencies: "019,055,057,067,094,100"
allowed_related_task_reads: "none"
---

# 101 — Implement plan-scoped cross-platform sleep inhibition

Objective: Implement a host-owned OS-native sleep inhibitor for the complete local RUNNING ORCHESTRATED plan.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Inspect baseline — Read P053 and only relevant current lifecycle/job/runner code and 099/100 interfaces.
- [ ] **S002** Implement native lease — Add host-owned Windows/macOS/Linux inhibitor and WSL/container boundary with checked acquire/status/release.
- [ ] **S003** Own full plan lifecycle — Hold across worker/provider changes, and release on all terminal/pause paths; resume with new lease.
- [ ] **S004** Implement night-readiness — Local auto-on, opt-out, strict require-awake, honest battery/permissions/credential warnings.
- [ ] **S005** Test and document — Run mapped mocks/safe platform probes, update bilingual docs and record source hashes/real outcomes.

## Scope

In: Native host power guard, supervisor lifecycle, strict unattended preflight, docs and CI.
Out: No global OS power edits, fake input, hidden lid override, privilege escalation, sandbox bypass or unbounded model calls.
Files: `skill/plan-and-execute/scripts/power_inhibit.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/run_concise.py`, `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/process_tree.py`, `skill/plan-and-execute/references/LIFECYCLE.md`, `skill/plan-and-execute/references/INSTALLATION.md`, `skill/plan-and-execute/references/INSTALLATION.pt-BR.md`, `test/optimization/plan_sleep_inhibition_self_test.py`, `.github/workflows/ci.yml`, `tools/run-repo-checks.js`, `docs/research/20261028-skill-optimization/implementation/101-receipt.json`, `docs/research/20261028-skill-optimization/implementation/101-outcome.md`

## Guidance

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

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_101`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_101`
