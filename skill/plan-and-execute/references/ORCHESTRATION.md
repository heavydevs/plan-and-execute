# Full orchestration workflow

Read only after the entrypoint has selected ORCHESTRATED, including a late promotion. This reference preserves the durable plan-and-execute contract while keeping routine direct work outside the harness.

## 1. Resolve the request

Treat input in this order:

1. Exact lifecycle commands were already routed before this reference.
2. No arguments: inspect lifecycle state. Resume the unique unfinished implementation first; create guided intake only when idle. See `INTAKE.md` and `LIFECYCLE.md`.
3. One existing regular file: validate/extract it with `requestctl.py` and use it as authoritative request evidence.
4. Otherwise use the complete inline request.

For a promoted request, the `promotectl.py render` output is the authoritative request file. Completed work in that handoff is current-state evidence; only `remaining_outcomes` becomes executable work.

Preserve the user's original request/request file. Before producing derived study, requirement, plan, TODO, context, learning, or handoff text, read `ARTIFACT_WRITING.md`; its bounded, concrete, observable writing contract remains mandatory.

## 2. Pass adaptive study before planning

Read `ADAPTIVE_STUDY.md`. Classify study depth based on uncertainty that can change architecture, compatibility, task boundaries, risk, or validation.

Search/filter before broad reads. Use focused external research only when authoritative current facts materially affect the plan. A late promotion studies only remaining work and current repository state.

Validate study state with `studyctl_concise.py`. Do not manufacture evidence merely to satisfy a planning template.

## 3. Build requirements-traceable TODOs

Read `PLANNING_PROTOCOL.md`, `EXECUTION_CONTEXT.md`, `PLAN_SPEC.md`, `MODEL_ROUTING.md`, and `PORTABLE_MODEL_ROUTING.md` when drafting the plan.

Inventory stable request parts (`P...`) and requirements (`R...`) for every remaining independently testable outcome/constraint. Map each request part -> requirement -> executable TODO, and every TODO back to requirements.

Recursively split until every TODO has:

- one coherent outcome and one independent validation boundary;
- a context surface whose retained reasoning is useful throughout the TODO;
- explicit scope in/out and expected files;
- dependencies, acceptance criteria, deterministic validation commands, and resumable subtasks/checkpoints;
- `context_boundary` evidence and optional sparse `learning_targets`;
- portable `model_family` (`F1`-`F4`) and `model_level` (`L1`-`L5`).

A new TODO must not contain `provider`, `model_tier`, `reasoning_effort`, or a concrete model id. Those fields are legacy-plan compatibility only.

Split unrelated domains even when they share a framework pattern. Do not split mechanically per file. Reject executable `extreme` TODOs; split further. Justify retained `high` leaves.

## 4. Keep execution context minimal

Default to no shared `CONTEXT.md`.

- global context only for non-obvious facts required by every TODO;
- scoped `contexts/<topic>.md` only when the same fact is needed by at least two but fewer than all TODOs;
- single-task information stays in that task definition;
- runtime discoveries cross task boundaries only through predeclared, validated learning targets.

Review must approve `contexts_minimal` and `context_boundaries_sound`.

## 5. Build the live provider compatibility table

The plan graph uses only F/L, but execution needs a current concrete binding. During planning, before plan creation:

1. use `PORTABLE_MODEL_ROUTING.md` to inspect current local CLI/model information and current authoritative provider documentation;
2. cover Codex, Claude Code, Gemini CLI, Qwen Code, and Muse Code/Muse Spark;
3. map every provider's current concrete models to F1-F4 and every family to L1-L5 native effort values;
4. repeat/clamp adjacent L values when a provider exposes fewer native levels; never invent unsupported controls;
5. record current `checked_at` and sources in top-level `model_compatibility` in the plan spec.

The controller writes the canonical `MODEL_COMPATIBILITY.json` plus human-readable `MODEL_COMPATIBILITY.md`. Concrete model names belong there, not in TODOs.

Use the lowest credible F/L for each leaf. Verifiability and blast radius matter more than overall request size. Raise L when evidence shows insufficient reasoning depth within a suitable family; raise F when evidence shows a model-capability gap.

Provider quota/rate/capacity failure does not raise F/L. Resolve the same F/L on another provider. Refresh the compatibility table when changing provider or when a recorded model/effort is unavailable, rejected, retired, or uncertain.

## 6. Review and create the durable plan

Use a fresh reviewer for complex plans when supported. Revise until coverage, atomicity, dependencies, validations, context minimality, context boundaries, F/L choices, and compatibility-table evidence pass with no unresolved material findings.

Create/gate using concise controllers:

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json [--request-file <file>]
python <skill-dir>/scripts/studyctl_concise.py attach --spec /tmp/study-spec.json --plan .ai-work/<plan-id>
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py audit --plan .ai-work/<plan-id>
python <skill-dir>/scripts/lifecyclectl_concise.py activate --plan .ai-work/<plan-id> --json
```

New portable plan creation fails if `model_compatibility` is missing/incomplete. The generated `PLAN.md` and every task definition reference `MODEL_COMPATIBILITY.md`.

Use request-file semantics in `INTAKE.md`. For late promotion, copy the rendered `/tmp` request so the compact handoff becomes `.ai-work/<plan-id>/REQUEST.md`. Autostart after gates unless a genuine safety/authorization gate blocks execution.

## 7. Persist checklist and task definitions

`TODO.md` is terse: exactly one line per parent task, plus short in-progress/blocked suffix when applicable. Detailed metadata belongs in `manifest.json` and one definition file per TODO.

`manifest.json` is authoritative. Never hand-edit task/subtask status, retries, or execution-route state.

Every portable task definition must be sufficient for a fresh compatible worker without the parent chat transcript. It includes objective, assigned context/learnings, resumable subtasks, scope, guidance, acceptance, validation, `model_family`, `model_level`, and an explicit reference to `MODEL_COMPATIBILITY.md`. It does not pin a provider/model.

## 8. Execute one isolated TODO at a time

Read `WORKFLOW.md` when execution begins. For every runnable TODO:

1. reload authoritative state from disk;
2. recover stale/interrupted `in_progress` state when needed;
3. read/refresh `MODEL_COMPATIBILITY.json` when the provider/model mapping is uncertain or changing;
4. resolve the TODO's F/L to the concrete route for the chosen available provider;
5. claim the TODO through `planctl_concise.py`, recording the resolved provider/model/effort as execution history only;
6. start a fresh worker with exactly one task-definition path plus assigned context/learning files;
7. never pass parent chat, whole plan, future task definitions, raw reports, or logs;
8. checkpoint subtasks only through the controller;
9. require the bounded completion report with exact context/learning read lists and completed subtask ids;
10. rerun every deterministic validation command outside the worker;
11. mark success only after validation passes;
12. materialize only predeclared, validated, target-specific reusable learnings;
13. continue until all tasks complete or one blocks at its configured limit.

Write-heavy tasks are sequential unless repository isolation/worktrees remove reconciliation risk.

## 9. Resume across quota/session/provider failure

Lifecycle state exists so implementation survives lost credits, process termination, host restart, or provider switching.

On resume, preserve completed tasks/subtasks and partial repository changes, recover orphaned `in_progress` state, and dispatch a fresh compatible worker from persisted task/context state. When the provider changes, refresh/resolve the compatibility table and keep the same F/L. Do not reconstruct the TODO solely because the provider/model changed.

Strict external execution uses:

```bash
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id>
```

or `pae resume`.

## 10. Replan only when evidence invalidates the plan

If execution reveals a material unknown, contradictory contract, new version/security/migration risk, invalid dependency, wrong context boundary, or an actual capability requirement different from the recorded F/L, stop downstream execution and re-enter the necessary study/planning gates.

Do not replan merely because a provider/model changed, a worker used many tokens, or a provider hit quota.

## 11. Finish and clean planning state

After every TODO and final deterministic validation pass:

1. build final-summary input from compact authoritative task state, validations, and bounded repository-change evidence;
2. generate the user-facing handoff with a low-cost compatible route when available;
3. mark summary generated;
4. deactivate lifecycle state;
5. run guarded plan cleanup.

```bash
python <skill-dir>/scripts/lifecyclectl_concise.py deactivate --plan .ai-work/<plan-id> --json
python <skill-dir>/scripts/planctl_concise.py cleanup --plan .ai-work/<plan-id>
```

Delete only the verified planning/control workspace. Preserve implementation changes, tests, generated product artifacts, commits, and unrelated repository content. Retain plan state when completion, validation, or summary generation fails so diagnosis/resume remains possible.
