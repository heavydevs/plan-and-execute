---
task_id: "100"
status: "pending"
requirements: "R052"
dependencies: "099"
allowed_related_task_reads: "none"
---

# 100 — Review and correct semantic progress and stall recovery

Objective: Independently review and correct semantic-progress instrumentation, honest percentage reporting and safe evidence-based stall recovery using actual runtime evidence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read actual implementation and evidence — Inspect task 099 code, test receipts, source hashes and limitations; never reuse unverified research as test evidence.
- [ ] **S002** Run independent maximum-qualified review — Have a genuine fresh qualified reviewer check semantics, percent math, route/permission guards and negative cases; record exact reviewed hashes.
- [ ] **S003** Fix critical and high defects — Correct confirmed findings inside the authorized scope or leave the review pending with a recorded blocker.
- [ ] **S004** Rerun mapped acceptance — Independently rerun the complete new test and affected progress/job/validate/routing regressions through resource monitoring.
- [ ] **S005** Record independent review evidence — Write task 100 review receipt/outcome with provider/model/effort, hashes, actual checks and unresolved findings.

## Scope

In: Independent review and correction of semantic progress/recovery and documented acceptance evidence.
Out: No second planning engine, duplicate watcher or every-tick LLM calls.; No unauthorized writes, provider login, destructive restart or ignoring host policy.
Files: `skill/plan-and-execute/scripts/progress_signal.py`, `skill/plan-and-execute/scripts/progress_watch.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/scripts/jobctl.py`, `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/validatectl.py`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/references/PROGRESS_TIMEOUTS.md`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `skill/plan-and-execute/references/VALIDATION_WORKLOADS.md`, `test/optimization/semantic_progress_recovery_self_test.py`, `docs/research/20261028-skill-optimization/implementation/100-receipt.json`, `docs/research/20261028-skill-optimization/implementation/100-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/099-semantic-progress-recovery.md and task 099's actual code/test receipts; never treat this prepared research as runtime evidence.
- Follow task 100 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json; dispatch a genuinely independent qualified reviewer and pin reviewed hashes.
- Validate semantic-vs-liveness behavior, truthful percentages, safe ownership and authorized provider routing; correct critical/high findings.
- Record actual review and tests in docs/research/20261028-skill-optimization/implementation/100-receipt.json and docs/research/20261028-skill-optimization/implementation/100-outcome.md; pending unless verified.

## Acceptance

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

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_100`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_100`
