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

Validate study state with `studyctl_concise.py`. Do not manufacture evidence merely to satisfy a planning template. A late promotion studies only remaining work and current repository state.

## 3. Build requirements-traceable TODOs

Read `PLANNING_PROTOCOL.md`, `EXECUTION_CONTEXT.md`, and `PLAN_SPEC.md` only when drafting the plan.

Inventory stable request parts (`P...`) and requirements (`R...`) for every **remaining** independently testable outcome/constraint. Map each request part -> requirement -> executable TODO, and every TODO back to requirements.

Recursively split until every TODO has:

- one coherent outcome and one independent validation boundary;
- a context surface whose retained reasoning is useful throughout the TODO;
- explicit scope in/out and expected files;
- dependencies, acceptance criteria, and deterministic validation commands;
- resumable subtasks/checkpoints;
- `context_boundary` evidence and optional sparse `learning_targets`;
- `provider`, `model_tier`, and `reasoning_effort`.

Split unrelated domains even when they share a framework pattern. Do not split mechanically per file: tightly coupled controller/service/entity/migration/tests may remain together when they implement one invariant and benefit from one worker context.

Reject executable `extreme` TODOs; split further. Justify retained `high` leaves. For promoted work, never create retroactive TODOs for completed implementation; only remaining outcomes are planned.

## 4. Keep execution context minimal

Default to no shared `CONTEXT.md`.

- global context only for non-obvious facts required by every TODO;
- scoped `contexts/<topic>.md` only when the same fact is needed by at least two but fewer than all TODOs;
- single-task information stays in that task definition;
- runtime discoveries cross task boundaries only through predeclared, validated learning targets.

Review must approve `contexts_minimal` and `context_boundaries_sound`.

## 5. Preserve adaptive task-level model routing

Read `MODEL_ROUTING.md` only when choosing or escalating routes. It defines provider-independent semantics. When a concrete provider/model must be chosen, read **only** that provider's reference: `MODEL_ROUTING_CODEX.md` for Codex or `MODEL_ROUTING_CLAUDE.md` for Claude Code. Do not load both; a fallback provider loads its file only if fallback occurs.

Each TODO stores logical capability instead of binding unnecessarily to one concrete model:

- `economy`: exploration, mechanical/narrow work, cheap summarization;
- `standard`: normal bounded implementation/debugging/tests;
- `strong`: subtle/high-risk/weakly verifiable or difficult evidence-heavy work;
- `max`: frontier/long-horizon work when semantic need or concrete lower-route failure justifies it.

Use the lowest credible capability for the leaf. Verifiability and blast radius matter more than overall request size. A newer frontier family at low/medium effort may be a cheaper strong route than an older model at high effort; provider references own that calibration.

Keep `provider: auto` when equivalent providers may execute the task. Pin only when the task genuinely depends on a provider. Record the actual execution route separately so another compatible AI can resume.

Escalate from technical evidence. Rate/quota exhaustion, temporary capacity, unavailable models, or host interruption are not technical failures and must not consume the functional failure budget.

## 6. Review and create the durable plan

Use a fresh reviewer for complex plans when supported. Revise until coverage, atomicity, dependencies, validations, context minimality, and context boundaries pass with no unresolved material findings.

Create/gate using concise controllers:

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json [--request-file <file>]
python <skill-dir>/scripts/studyctl_concise.py attach --spec /tmp/study-spec.json --plan .ai-work/<plan-id>
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py audit --plan .ai-work/<plan-id>
python <skill-dir>/scripts/lifecyclectl_concise.py activate --plan .ai-work/<plan-id> --json
```

Use the request-file semantics in `INTAKE.md`. For late promotion, copy the rendered `/tmp` request so the compact handoff becomes `.ai-work/<plan-id>/REQUEST.md`. Autostart after gates unless a genuine safety/authorization gate blocks execution.

## 7. Persist checklist and task definitions

`TODO.md` is terse: exactly one line per parent task, plus short in-progress/blocked suffix when applicable. Detailed metadata belongs in `manifest.json` and one definition file per TODO.

`manifest.json` is authoritative. Never hand-edit task/subtask status, retries, or routing state.

Every task definition must be sufficient for a fresh compatible worker without the parent chat transcript. It includes objective, assigned execution context/learnings, resumable subtasks, scope, non-obvious guidance, acceptance, deterministic validation, and logical route recommendation.

## 8. Execute one isolated TODO at a time

Read `WORKFLOW.md` when execution begins. For every runnable TODO:

1. reload authoritative state from disk;
2. recover stale/interrupted `in_progress` state when needed;
3. claim the next runnable TODO through `planctl_concise.py`;
4. select/record the actual provider/model/effort route;
5. start a fresh worker with exactly one task-definition path plus assigned context/learning files;
6. never pass parent chat, whole plan, future task definitions, raw reports, or logs;
7. checkpoint subtasks only through the controller;
8. require the bounded completion report with exact context/learning read lists and completed subtask ids;
9. rerun every deterministic validation command outside the worker;
10. mark success only after validation passes;
11. materialize only predeclared, validated, target-specific reusable learnings;
12. continue until all tasks complete or one blocks at its configured limit.

Write-heavy tasks are sequential unless repository isolation/worktrees remove reconciliation risk.

## 9. Resume across quota/session/provider failure

Lifecycle state exists so implementation survives lost credits, process termination, host restart, or provider switching.

On resume:

- discover the unique active/actionable plan;
- acquire/recover the runner lease;
- return only orphaned `in_progress` task/subtask state to runnable state;
- preserve completed tasks/subtasks and partial repository changes;
- do not count quota/rate/capacity interruption as technical failure;
- dispatch a fresh compatible worker from persisted task/context state, not prior chat history.

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
