---
task_id: "099"
status: "pending"
requirements: "R052"
dependencies: "053,055,057,061,063,075,088,092"
allowed_related_task_reads: "none"
---

# 099 — Implement semantic progress and safe five-minute stall recovery

Objective: For validations expected or observed to exceed five minutes, emit verified progress signals and honest percentages; after 300 seconds without semantic progress, diagnose the cause and retry confirmed, authorized code defects with a stronger eligible model or effort.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read contract and actual code — Read the focused 099 study, existing 052/054/056/060/062/087/091 decisions and affected code; use fresh source evidence.
- [ ] **S002** Choose economical truthful instrumentation — Use existing source-owned counters/checkpoints; add minimal validated PROGRESS units for predicted >300-second work and flag runtime instrumentation gaps.
- [ ] **S003** Separate semantic progress from activity — Implement monotonic verified completed-work clock distinct from CPU/output/heartbeats and resource health; preserve independent explicit hard ceilings.
- [ ] **S004** Compute honest stage-local percentages — Validate done/total/seq, phase/retry identity, missing totals and weights; report stage percentages only when justified, never fabricated global completion.
- [ ] **S005** Diagnose and safely reroute confirmed stalls — At 300 seconds without trustworthy semantic progress classify cause, preserve evidence, use existing eligible stronger repair route only when authorized, clean owned processes and rerun validated code.
- [ ] **S006** Run targeted and adversarial tests — Implement and run semantic_progress_recovery_self_test.py, all mapped checks and regressions for DIRECT/ORCHESTRATED, quiet work, noisy logs and failures.
- [ ] **S007** Record reproducible implementation evidence — Write task 099 receipt/outcome with actual changed-file hashes, diagnostics, executed checks, limitations and costs; never fabricate an independent review.

## Scope

In: Architectural and runtime long-validation instrumentation, honest completed-work percentages, semantic-stall classification, guarded stronger repair and monitored rerun.
Out: No second planning engine, duplicate watcher or every-tick LLM calls.; No unauthorized writes, provider login, destructive restart or ignoring host policy.
Files: `skill/plan-and-execute/scripts/progress_signal.py`, `skill/plan-and-execute/scripts/progress_watch.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/VALIDATION_WORKLOADS.md`, `test/optimization/semantic_progress_recovery_self_test.py`, `docs/research/20261028-skill-optimization/implementation/099-receipt.json`, `docs/research/20261028-skill-optimization/implementation/099-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/099-semantic-progress-recovery.md; follow the task 099 catalog contract and current impacted code.
- Reuse existing progress_signal/progress_watch/resource_watch, service-map, run_isolated and routing ladders; don't add a second monitor.
- Diagnose a five-minute stall before escalating: silence or CPU alone is insufficient evidence of defective implementation; require authorized repairs.
- Record actual execution, checks, changed-file hashes and limits in docs/research/20261028-skill-optimization/implementation/099-receipt.json and docs/research/20261028-skill-optimization/implementation/099-outcome.md.

## Acceptance

- Design-anticipated validation >300s reuses an existing reliable counter/probe or adds minimal instrumentation before starting; short checks remain fast and untouched.
- Unexpected validation >300s without reliable progress raises a bounded instrumentation-gap diagnostic, never fabricated retrospective progress or uncontrolled edits to the running process.
- Semantic progress advances only for trusted increasing completed-work/stage checkpoints; timestamps, changing generic output, constant heartbeat, CPU busy loops and unrelated file activity cannot perpetually renew it.
- A valid long-running validation with increasing verified units/checkpoints continues beyond five minutes, limited only by a separate explicit hard ceiling or user cancellation.
- With a known stable per-stage total, percentage is correct and labeled to that stage; unknown totals remain indeterminate and a global percentage is never guessed or reaches 100 before success.
- At 300 seconds since last trusted semantic advancement, capture bounded redacted process/dependency/diagnostic evidence and distinguish semantic defect, environmental fault, explicit quiet window and unknown cause.
- A confirmed semantic code stall routes an authorized stronger eligible implementer, stops only owned processes, preserves completed checkpoints, changes code and reruns fresh mapped validation.
- Environmental, quota, auth, permission, unknown-owner, unknown-cause and configured hard-ceiling failures do not trigger stronger model execution or duplicate a live job.
- DIRECT validate-only remains read-only and plan-free; authorized DIRECT repair and ORCHESTRATED retries share the monitoring engine, attempts, source hashes, budgets and cancellation guards.
- Tests cover simulated 299/300/301-second boundaries, stage resets/replayed counters, process descendants, crash/restart, dependency health, safe probes, and no per-tick LLM cost.
- No existing task or independent review is considered complete until its own runtime and source-hash evidence exists.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_099`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_099`
