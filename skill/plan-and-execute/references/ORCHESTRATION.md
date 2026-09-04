# Full orchestration workflow

Read only after the entrypoint has selected ORCHESTRATED, including a late promotion. This reference preserves the durable plan-and-execute contract while keeping routine direct work outside the harness.

## 1. Resolve the request

Treat input in this order:

1. Exact lifecycle commands were already routed before this reference.
2. No arguments: inspect lifecycle state. Resume the unique unfinished implementation first; create guided intake only when idle. See `INTAKE.md` and `LIFECYCLE.md`.
3. One existing regular file: validate/extract it with `requestctl.py` and use it as authoritative request evidence.
4. Otherwise use the complete inline request.

For a promoted request, the `promotectl.py render` output is the authoritative request file. Completed work in that handoff is current-state evidence; only `remaining_outcomes` becomes executable work.

Preserve the user's original request/request file. Before producing derived study, requirement, plan, TODO, context, learning, or handoff text, read `ARTIFACT_WRITING.md`; its one-field/one-job, bounded, concrete, observable writing contract remains mandatory. Compress only derived artifacts.

## 2. Pass adaptive study before planning

Read `ADAPTIVE_STUDY.md`. Classify study depth based on uncertainty that can change architecture, compatibility, task boundaries, risk, or validation.

- skip broad study when direct evidence already makes the remaining work fully scoped;
- search/filter before opening repository files broadly;
- use focused external research only when authoritative current facts materially affect the plan;
- use broad project/external study for genuinely complex architecture, migration, security, compatibility, or user-requested research.

Validate study state with `studyctl_concise.py`. Do not manufacture evidence merely to satisfy a planning template.

A late promotion does not automatically require broad research: study only the remaining work and the current repository state.

## 3. Build requirements-traceable TODOs

Read `PLANNING_PROTOCOL.md`, `EXECUTION_CONTEXT.md`, and `PLAN_SPEC.md` only when drafting the plan.

Inventory stable request parts (`P...`) and requirements (`R...`) for every **remaining** independently testable user outcome/constraint. Map each request part -> requirement -> at least one executable TODO, and map every TODO back to requirements.

Recursively split until every TODO has:

- one coherent outcome;
- one independent validation boundary;
- a context surface whose retained reasoning is useful throughout that TODO;
- explicit scope in/out and expected files;
- dependencies;
- acceptance criteria and deterministic validation commands;
- resumable subtasks/checkpoints;
- `context_boundary` evidence;
- optional sparse directional `learning_targets`;
- `provider`, `model_tier`, and `reasoning_effort`.

Split unrelated domains even when they use the same framework pattern. Do not split mechanically per file: tightly coupled controller/service/entity/migration/tests may remain together when they implement one invariant and benefit from one worker context.

Reject executable `extreme` TODOs; split further. Justify retained `high` leaves.

For promoted work, never create retroactive TODOs solely to represent completed implementation. Record completed state in `REQUEST.md`; only remaining outcomes are planned.

## 4. Keep execution context minimal

Default to no shared `CONTEXT.md`.

- global context only for non-obvious facts required by every TODO;
- scoped `contexts/<topic>.md` only when the same fact is needed by at least two but fewer than all TODOs;
- single-task information stays in that task definition;
- runtime discoveries cross task boundaries only through predeclared, validated learning targets.

Review must approve `contexts_minimal` and `context_boundaries_sound`.

## 5. Preserve task-level model routing

Read `MODEL_ROUTING.md` only when choosing or escalating execution routes.

Each TODO stores logical capability instead of binding unnecessarily to one model:

- `economy`: mechanical/narrow work and cheap summarization;
- `standard`: normal bounded repository implementation/debugging/tests;
- `strong`: architecture-sensitive, security, concurrency, transaction, compatibility/migration, or difficult evidence-heavy work;
- `max`: only after concrete unresolved lower-tier failure evidence.

Use the lowest tier plausibly able to satisfy the leaf acceptance criteria. A large plan does not make every TODO `strong`.

Keep `provider: auto` when equivalent providers may execute the task. Pin a provider only when the task genuinely depends on it. Record the actual execution route separately in lifecycle/task state; the recommendation remains portable for another compatible AI.

Escalate from technical evidence: effort -> model tier -> provider. Rate/quota exhaustion, temporary capacity, or host interruption are not technical failures and must not consume the functional failure budget.

## 6. Review and create the durable plan

Use a fresh reviewer for complex plans when supported. Revise until coverage, atomicity, dependencies, validations, context minimality, and context boundaries all pass with no unresolved material findings.

Create/gate using concise controllers:

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json [--request-file <file>]
python <skill-dir>/scripts/studyctl_concise.py attach --spec /tmp/study-spec.json --plan .ai-work/<plan-id>
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py audit --plan .ai-work/<plan-id>
python <skill-dir>/scripts/lifecyclectl_concise.py activate --plan .ai-work/<plan-id> --json
```

Use the request-file copy/move semantics defined by `INTAKE.md`. For late promotion, copy the rendered `/tmp` request so the compact handoff becomes `.ai-work/<plan-id>/REQUEST.md`.

Autostart after all gates unless a genuine safety/authorization gate blocks execution.

## 7. Persist the checklist and task definitions

`TODO.md` is intentionally terse: exactly one line per parent task, plus short in-progress/blocked suffix when applicable. Detailed metadata belongs in `manifest.json` and one definition file per TODO.

`manifest.json` is authoritative. Never hand-edit task status, subtask status, retries, or routing state.

Every task definition must remain sufficient for a fresh compatible worker to execute without the parent chat transcript. It includes objective, assigned execution context/learnings, resumable subtasks, scope, non-obvious guidance, acceptance, deterministic validation, and logical route recommendation.

## 8. Execute one isolated TODO at a time

Read `WORKFLOW.md` when execution begins.

For every runnable TODO:

1. reload authoritative state from disk;
2. recover stale/interrupted `in_progress` state when needed;
3. claim the next runnable TODO through `planctl_concise.py`;
4. select/record the actual provider/model/effort route;
5. compile the task definition plus assigned context/learnings into one immutable provenance-stamped packet and start a fresh worker with that single path;
6. never pass parent chat, whole plan, future task definitions, raw reports, or logs;
7. checkpoint subtasks only through the controller;
8. require the bounded completion report with exact context/learning read lists and completed subtask ids; do not ask the worker to self-report changed files or validation results;
9. compute the per-attempt repository delta and rerun every deterministic validation command outside the worker;
10. mark success only after validation passes;
11. materialize only predeclared, validated, target-specific reusable learnings;
12. continue until all tasks complete or one blocks at its configured limit.

Write-heavy tasks are sequential unless repository isolation/worktrees remove reconciliation risk.

## 9. Resume across quota/session/provider failure

Lifecycle state exists specifically so implementation survives lost credits, process termination, host restart, or provider switching.

On resume:

- discover the unique active/actionable plan;
- acquire/recover the runner lease;
- return only orphaned `in_progress` task/subtask state to a runnable state;
- preserve completed parent tasks and completed subtasks;
- preserve partial repository changes;
- classify availability, environment, completion-contract, capability, validation, and planning-invalidation failures separately;
- defer quota/rate/capacity retries without consuming functional failures and release the lease while waiting;
- dispatch a fresh compatible worker using persisted task/context state, not prior chat history.

Strict external execution uses:

```bash
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id>
```

or `pae resume`.

## 10. Replan only when evidence invalidates the plan

If execution reveals a material unknown, contradictory contract, new version/security/migration risk, invalid dependency, or wrong context boundary, stop downstream execution and re-enter the necessary study/planning gates.

Do not replan merely because a worker used many tokens or a provider hit quota.

## 11. Finish and clean planning state

After every TODO and final deterministic validation pass:

1. build final-summary input from compact authoritative task state, validations, and bounded repository-change evidence — never concatenate raw worker reports;
2. generate the user-facing handoff with an economy route when available;
3. mark summary generated;
4. deactivate lifecycle state;
5. run guarded plan cleanup.

```bash
python <skill-dir>/scripts/lifecyclectl_concise.py deactivate --plan .ai-work/<plan-id> --json
python <skill-dir>/scripts/planctl_concise.py cleanup --plan .ai-work/<plan-id>
```

Delete only the verified planning/control workspace. Preserve implementation changes, tests, generated product artifacts, commits, and unrelated repository content. Retain plan state when completion, validation, or summary generation fails so diagnosis/resume remains possible.
