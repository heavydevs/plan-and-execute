---
name: plan-and-execute
description: Deeply study a large software request and the relevant repository before creating a requirements-traceable execution plan, then execute it as small, isolated, resumable TODOs with one definition file per task, deterministic validation, Claude Code/Codex model routing, escalation after technical failures, low-cost final summarization, and safe cleanup. Use for long implementations, migrations, refactors, multi-workstream features, architecture-sensitive changes, test-heavy work, or any request that must be decomposed carefully without losing requirements or polluting worker context.
---

# Plan and Execute

Study the full request first. Build a complete requirements inventory, inspect the relevant repository and subject matter, recursively decompose the work into independently verifiable TODOs, review the plan in a fresh context, pass deterministic quality gates, and only then execute.

## Non-negotiable planning contract

- Read the entire request before drafting any TODO.
- Inventory every distinct requested outcome, constraint, test expectation, compatibility need, risk, and non-goal as a stable request part such as `P001`.
- Inspect the relevant repository instructions, architecture, implementation, tests, build files, schemas, interfaces, and CI commands before selecting task boundaries.
- Research unfamiliar, current, version-sensitive, or security-sensitive behavior with authoritative sources when materially needed. Record why research was or was not needed.
- Map every request-part id to at least one stable requirement id.
- Map every requirement id to at least one executable TODO.
- Map every TODO back to one or more requirement ids.
- Recursively split work until each TODO has one coherent outcome and an independent validation path.
- Never accept an executable TODO rated `extreme`; split it further.
- Require a substantive atomicity rationale for every `high` complexity TODO.
- Review the draft plan in a fresh subagent or process whenever supported. Revise until coverage, atomicity, dependencies, and validations all pass.
- Do not autostart until `planctl.py validate` and `planctl.py audit` both succeed.

Read [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md) before planning a new request. It defines the mandatory study, recursive decomposition, traceability, reviewer, and quality-gate procedure.

## Non-negotiable execution contract

- Store plan state under `.ai-work/<plan-id>/`; never mix planning files with implementation files.
- Create `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, and one Markdown definition under `tasks/` for every TODO.
- Treat `manifest.json` as the state source of truth and update it through `scripts/planctl.py`; do not hand-edit task status.
- Give an implementation worker exactly one task-definition path. Do not paste the parent chat, whole plan, analysis files, or future task definitions into its prompt.
- Permit workers to read source code, tests, build files, and runtime output relevant to their assigned task.
- Permit another task definition only when explicitly allowlisted and required by a dependency, ambiguity, or validation conflict. Record the reason.
- Validate every task with deterministic commands outside the worker before marking it complete.
- Execute write-heavy tasks sequentially. Parallelize only read-only tasks or tasks isolated in separate worktrees.
- Count implementation or validation failures as technical failures. Do not count rate limits, exhausted credits, or temporary capacity as technical failures.
- Escalate effort first, then model tier, then provider when allowed. Never claim a route was used when the runtime could not honor it.
- Summarize with an economy-tier model after every task passes.
- Delete only the verified plan directory. Never delete source changes, tests, commits, or other repository content.

## Plan the work deeply

1. Parse the complete request into distinct request parts with stable ids such as `P001`.
2. Inspect the repository and record concrete findings.
3. Decide whether external research is needed and record findings or the reason it is unnecessary.
4. Create a complete requirement inventory with ids such as `R001`, and map each user-sourced requirement to its originating `request_part_ids`.
5. Verify every request part is represented by one or more requirements; then group requirements into workstreams and recursively split each workstream into executable leaf TODOs.
6. Assign each TODO:
   - one exact objective;
   - mapped `requirement_ids`;
   - `low`, `medium`, or `high` complexity;
   - an `atomicity_rationale`;
   - in-scope and out-of-scope boundaries;
   - dependencies and expected files;
   - observable acceptance criteria;
   - deterministic validation commands;
   - provider preference, logical model tier, and reasoning effort.
7. Start a fresh plan reviewer. Give it the full request, compact analysis, requirements, and draft task graph, but no implementation assignment.
8. Revise until the reviewer approves requirement coverage, task atomicity, dependencies, and validation sufficiency with no unresolved findings.
9. Write a JSON plan spec following [references/PLAN_SPEC.md](references/PLAN_SPEC.md).
10. Create and inspect the plan:

```bash
python <skill-dir>/scripts/planctl.py create --repo-root . --spec /tmp/plan-spec.json
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

11. Start execution immediately after both quality gates pass unless the request contains an unapproved destructive action, production deployment, credential change, irreversible migration, or another genuine safety gate.

Do not replace analysis with a shallow checklist. Do not use generic TODOs such as “implement all changes,” “finish the migration,” or “update backend and frontend.” Split by independently failing outcomes and validation boundaries, while avoiding artificial file-by-file microtasks.

## Choose the execution mode

### Native subagent mode

Use this mode inside an active Claude Code or Codex IDE/CLI chat.

1. Keep planning, plan review, and state management in the current orchestrator thread.
2. Dispatch one fresh native subagent/thread for the next runnable task.
3. Pass only the task-definition path, task id, repository root, isolation rules, and completion-report contract.
4. Select the task's requested provider-equivalent model tier and reasoning effort when the native API supports per-agent routing.
5. Receive only the bounded completion report; keep raw logs in the worker thread.
6. Re-run the task's validation commands in the orchestrator thread, then update state.

Do not recursively launch the same CLI from inside itself when the client prohibits nested sessions. Use the optional strict runner from an external terminal instead.

### Strict external-runner mode

Use `scripts/run_isolated.py` from a VS Code terminal, CI job, or other shell outside an active nested provider session when process-level fresh sessions, automatic rate-limit waiting, and exact CLI model routing are required.

The runner starts each attempt with a new non-persistent provider process, persists state before every attempt, validates commands itself, escalates on functional failure, retries usage limits without escalation, generates a final economy-model summary, and performs sentinel-protected cleanup.

Read [references/WORKFLOW.md](references/WORKFLOW.md) for both execution procedures and command examples.

## Execute the task loop

For native mode, repeat this sequence:

1. Get the next runnable task:

```bash
python <skill-dir>/scripts/planctl.py next --plan .ai-work/<plan-id> --json
```

2. Select the route using [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md).
3. Claim the task with the actual route.
4. Spawn a fresh worker and pass only the assigned definition plus the isolation contract.
5. Require a completion report matching `references/completion-report.schema.json`.
6. Re-run every `validation_commands` entry from the repository root.
7. On success, save the report under the plan's `results/` directory and mark the task complete.
8. On implementation or validation failure, record the concrete error, return the task to pending, and retry using the next escalation route.
9. On rate or usage limit, preserve pending state and wait or resume later without increasing the technical-failure count.
10. If evidence shows that a task is oversized or the plan missed material scope, stop downstream dispatch, revise through the full planning protocol, and resume only after validation and audit pass again.
11. Continue until every task is completed or a task reaches its configured failure limit and becomes blocked.

For strict mode, run:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

Do not stop after merely writing a plan when `autostart` is true.

## Finish and clean up

1. Confirm every task is `completed` and all deterministic validations passed.
2. Use a fresh economy-tier summarizer to read the prepared plan/results summary and produce the chat handoff in the user's language.
3. Include outcome, completed tasks, important files, validation results, remaining risks, and follow-ups. Do not claim unrecorded tests.
4. Mark the summary generated.
5. Print or return the summary before cleanup.
6. Run guarded cleanup only after the summary exists:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```

If completion or summarization fails, retain the plan for diagnosis and resume from disk later.

## Resume behavior

- Load the existing plan instead of rebuilding it.
- Reset an abandoned `in_progress` task to pending only after confirming no worker is still active.
- Continue from the first runnable pending task.
- Preserve completed implementation and validation evidence.
- When the external runner remains open, let it wait and retry rate/usage limits according to `orchestrator.config.json`.
- When the host process was closed, rerun the same runner command; disk state provides the resume point.
- Continue legacy schema-v1 plans, but require schema-v2 analysis, traceability, and review for every newly created plan.

## Resources

- [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md): mandatory request study, repository research, recursive decomposition, traceability, and independent review.
- [references/PLAN_SPEC.md](references/PLAN_SPEC.md): schema-v2 plan JSON, request-part and requirement traceability, task complexity, review fields, and complete example.
- [references/WORKFLOW.md](references/WORKFLOW.md): native and strict execution details, state commands, validation, summary, and cleanup.
- [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md): planning and worker tiers, provider defaults, escalation, and cost discipline.
- [references/INSTALLATION.md](references/INSTALLATION.md): Claude Code and Codex installation and VS Code usage.
- `scripts/planctl.py`: deterministic plan creation, quality validation, traceability audit, state transitions, summary fallback, and safe cleanup.
- `scripts/run_isolated.py`: optional fresh-process executor with rate-limit waiting and provider/model escalation.
- `scripts/self_test.py`: representative plan-quality, state-machine, and end-to-end runner tests.
