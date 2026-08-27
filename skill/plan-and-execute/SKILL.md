---
name: plan-and-execute
description: Adaptively triage software-request complexity, spend repository and internet study only where it can materially improve the implementation, create a requirements-traceable plan whose TODO boundaries isolate unrelated AI context, persist resumable subtasks, transfer only validated target-specific learnings, and execute fresh workers with deterministic validation and optional Claude Code, Codex, Gemini CLI, Qwen Code, Kimi Code CLI, or Trae Agent routing. Use for implementations, migrations, refactors, multi-workstream or test-heavy changes, resuming unfinished work, cancelling/resetting plan state, guided request intake, or a requirements file path.
---

# Plan and Execute

Resolve the complete request, classify how much study is worth paying for, gather only the internal or external evidence that can materially improve the implementation, build and review a traceable plan, then execute one isolated verifiable TODO at a time. Treat persisted lifecycle state as authoritative so an interrupted implementation can resume without prior chat context.

## Route lifecycle commands before request interpretation

When the complete invocation argument is exactly one of these commands, handle it before file-path or inline-request rules:

- `current` or `status`: run `lifecyclectl.py current --repo-root . --json` and report the active implementation.
- `resume` or `continue`: discover, recover, validate, and continue the active implementation. Prefer native fresh workers when nested provider sessions are prohibited; otherwise `pae resume` or `lifecyclectl.py resume` provides strict process isolation.
- `cancel`: run `lifecyclectl.py cancel --repo-root . --json`. This deletes the active plan, task definitions, logs, results, intake draft, and lifecycle status while preserving repository implementation changes.
- `reset`: run `lifecyclectl.py reset --repo-root . --json` to remove every recognized plan-and-execute artifact in this workspace while preserving repository implementation changes.

Do not reinterpret these exact commands as software requirements. Read [references/LIFECYCLE.md](references/LIFECYCLE.md) before resume, cancellation, or reset operations.

## Resolve the request before study or planning

Treat invocation input in this order.

### 1. No arguments: resume an implementation or create a request

When invoked with no request text or file path, inspect lifecycle state before creating anything:

```bash
python <skill-dir>/scripts/lifecyclectl.py current --repo-root . --json
```

- When the result has `action: resume`, reload the plan and manifest from the returned path, recover stale `in_progress` tasks, rerun the study and plan gates, and continue from the next runnable TODO. Do not create another request.
- When the result has `action: already_running`, report the live runner and do not start a duplicate worker.
- When discovery reports multiple unfinished plans, stop and identify the ambiguity; never choose silently.
- Only when the result has `action: create_request`, use the guided intake steps below.

For native resume, run `lifecyclectl.py recover --plan <active-plan> --json` before loading the next TODO. For strict process-isolated resume, run `pae resume` or:

```bash
python <skill-dir>/scripts/lifecyclectl.py resume --repo-root .
```

When no implementation is active, create the request draft from the repository root:

1. Run:

```bash
python <skill-dir>/scripts/requestctl.py create --repo-root . --json
```

2. Preserve the returned absolute `path` in the orchestrator context.
3. Tell the user that the file was created and opened. If VS Code is detected, the helper reuses the active window; otherwise it tries the configured or platform editor.
4. Present the returned confirmation action. Prefer native choice UI; otherwise show only:
   - **Continue - I finished writing the request**
   - **Reopen the request file**
5. End the turn. Do not study, plan, or execute yet.

When the user confirms completion:

1. Validate the preserved path:

```bash
python <skill-dir>/scripts/requestctl.py validate --file "<request-path>" --json
```

2. If incomplete, reopen it and ask the user to finish it:

```bash
python <skill-dir>/scripts/requestctl.py reopen --file "<request-path>" --json
```

3. If a resumed session lost the path, recover the newest draft:

```bash
python <skill-dir>/scripts/requestctl.py latest --repo-root . --json
```

4. Extract only the user-authored body:

```bash
python <skill-dir>/scripts/requestctl.py extract --file "<request-path>"
```

5. Later, create the plan with move semantics so the draft becomes `.ai-work/<plan-id>/REQUEST.md`:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json \
  --request-file "<request-path>" \
  --move-request
```

Read [references/INTAKE.md](references/INTAKE.md) for editor detection, recovery, validation, localization, and safety.

### 2. One existing file path: use it as the request

When the complete invocation argument resolves to an existing regular file:

1. Treat it as the authoritative request.
2. Validate and extract it with `requestctl.py`.
3. Read every requirement in the file; do not reduce it to disconnected snippets.
4. Create the plan with copy semantics by omitting `--move-request`:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json \
  --request-file "<provided-file>"
```

Reject symlinks, directories, missing files, and files without meaningful instructions. Do not silently treat an intended path as inline prose.

### 3. Any other non-empty arguments: use inline request text

Treat the complete argument text as the request. Preserve every detail, example, constraint, test expectation, referenced path, and definition of done.

## Non-negotiable study and planning contract

- Read the complete request before collecting broad evidence or drafting TODOs.
- Inventory every distinct outcome, constraint, activity, test expectation, compatibility need, migration, risk, and non-goal as a stable request part such as `P001`.
- Classify the request as `simple`, `medium`, or `complex` before broad repository inspection. Quantity alone is never a reason to classify a request as complex.
- Use the least expensive study depth that can still change architecture, compatibility, task boundaries, risk, or validation.
- For `simple`, skip pre-plan repository and internet study when the request is direct, low-risk, fully scoped, and independent of external facts. Record the skip decision instead of manufacturing evidence.
- For `medium`, do not ask the user about study depth. Automatically use `related_packages` or `workspace_keywords`, prefer search/filter tools before opening files, and use focused external research only when a material trigger exists.
- For `complex`, ask the user both fixed-choice study questions before broad exploration unless the request already contains those choices. Do not silently broaden the selected scope.
- Do not draft requirements or executable TODOs until the adaptive study decision/spec passes `studyctl.py validate`; a simple fast-path spec may legitimately contain zero repository sources and zero external sources.
- Map every request-part id to at least one requirement id, every requirement to at least one executable TODO, and every TODO back to requirements.
- Recursively split work until each TODO has one coherent outcome, one independent validation path, and one context surface whose retained reasoning is useful across the whole TODO.
- Split unrelated domains even when they use the same architectural pattern. For example, independent person and store CRUDs normally become separate TODOs when their controllers, services, entities, rules, and tests do not share an invariant or failure boundary.
- Do not split mechanically by file or class. Keep a domain controller, service, entity, and focused tests together when they implement one rule set and benefit from the same worker context.
- Reject executable `extreme` work and split it further.
- Require a substantive atomicity rationale for every `high` complexity TODO.
- Require every schema-v4 TODO to declare a `context_boundary`, a stable resumable `subtasks` checklist, and any directional `learning_targets` whose future workers could benefit from concise validated findings.
- Evaluate progressive execution context only after the draft TODO graph exists: create `CONTEXT.md` only for universal indispensable information, create scoped files only for at least two but not all TODOs, keep single-task information in that task definition, and otherwise omit shared context.
- Ground every context item in evidence, keep it one-line and operational, and reject duplication or prose summaries.
- Match review cost to study cost: concise self-check for a simple fast path, separate review for medium only when uncertainty/risk warrants it, and a fresh reviewer for complex requests whenever supported.
- Require `plan_review.contexts_minimal` and `plan_review.context_boundaries_sound` to be true for schema v4.
- Do not autostart until `studyctl.py validate-plan`, `planctl.py validate`, and `planctl.py audit` all succeed.

Read [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md) before collecting evidence. Then read [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md) before drafting the plan and [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md) before deciding shared worker context.

## Pass the adaptive study gate before planning

1. Read the request and classify complexity before broad repository exploration:
   - `simple`: direct, routine, low-risk, no material architectural/external uncertainty;
   - `medium`: bounded change that benefits from package-local or keyword-filtered discovery;
   - `complex`: cross-cutting architecture, migration, compatibility, security, data-integrity, ownership, provider, or high-risk uncertainty.
2. Treat quantity separately from complexity. Many independent direct edits may remain `simple`.
3. For `simple`, set internal and external depth to `none`, record why study was skipped, and proceed without opening unrelated repository context.
4. For `medium`, choose internal depth automatically:
   - `related_packages` when the owning module is already clear;
   - `workspace_keywords` when ownership/symbols/tests must be located. Search first; open only high-signal matches and expand narrowly.
5. For `complex`, ask both questions in one chat turn and end the turn before broad study. Use exactly these fixed choices:
   - Internal: **Pacotes relacionados** / **Busca por palavras-chave em todo o workspace** / **Projeto completo**.
   - External: **Sem estudo externo** / **Pesquisa focalizada** / **Pesquisa ampla**.
   Record `selection_source: user`. If the request already specifies one of the fixed choices, reuse it instead of asking again.
6. Evaluate external triggers. Medium requests automatically use `focused` research when a trigger is material. Complex requests honor the user's external choice. Never invent an external fact when the user chose no external study; block on unresolved high-impact facts when necessary.
7. Resolve only material questions whose answers can change the plan. A simple fast path may have zero material questions.
8. Write `/tmp/study-spec.json` using study schema v2 and [references/study-spec.example.json](references/study-spec.example.json). Existing schema-v1 study attachments remain supported.
9. Validate before drafting requirements or TODOs:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

If the study is blocked or not ready, resolve the gap, record a bounded low-risk assumption, or request user input only when a high-impact decision cannot be inferred safely. Do not escalate from the selected study depth silently; re-enter the triage gate when broader context is genuinely necessary.

## Build the traceable plan

1. Copy `internal_study.plan_finding` exactly into `request_analysis.repository_findings` for study schema v2. This is the auditable skip/selection decision even when no repository source was opened.
2. Also copy every actual internal study `finding` exactly into `request_analysis.repository_findings`.
3. Copy every external source `finding` exactly into `request_analysis.research_findings`.
4. Record the external decision, selected depth, and rationale in `request_analysis.research_decision`.
5. Copy every synthesized risk exactly into `request_analysis.risks`.
6. Copy every synthesized planning constraint exactly into `global_constraints`.
7. Create stable requirements such as `R001`; copy every synthesized derived requirement exactly as requirement text.
8. Group requirements into workstreams and recursively split each into executable leaf TODOs. For every candidate grouping, ask whether a fresh worker would materially benefit from retaining the same decisions, invariants, files, debugging evidence, and validation history. Split when the answer is no.
9. Include every synthesized validation implication in at least one task acceptance criterion, implementation note, or validation command.
10. Give every TODO one objective, mapped requirements, complexity, atomicity rationale, scope boundaries, dependencies, expected files, acceptance criteria, validation commands, provider preference, model tier, reasoning effort, `context_boundary`, and one or more stable resumable subtasks.
11. Predeclare `learning_targets` only when a later TODO is sufficiently similar to reuse a difficult validated procedure, decision, code reference, pitfall, or validation technique. Make every relationship directional and name the narrow topics that may cross the boundary. Do not transfer chat transcripts, broad history, or speculative advice.
12. Evaluate progressive execution context using [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md):
    - explicitly choose `create` or `omit` for global `CONTEXT.md`;
    - place only information needed by every TODO in global context;
    - create a scoped `contexts/<topic>.md` only when the same information is needed by at least two and fewer than all TODOs;
    - keep information for a single TODO inside its task definition;
    - include concise `necessity` and grounded `source_refs` for every context item.
13. Start a fresh plan reviewer with the request, compact evidence, requirements, draft graph, context-boundary rationales, subtask checkpoints, learning relationships, and execution-context proposal, but no implementation assignment.
14. Revise until coverage, atomicity, dependencies, validation, `contexts_minimal`, and `context_boundaries_sound` all pass with no unresolved findings.
15. Write `/tmp/plan-spec.json` following [references/PLAN_SPEC.md](references/PLAN_SPEC.md).
16. Create the plan with the correct request-file mode from the input rules.
17. Attach the validated study and prove that its findings affected the plan:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>
```

18. Run all quality gates:

```bash
python <skill-dir>/scripts/studyctl.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

19. Register the validated plan as the active implementation:

```bash
python <skill-dir>/scripts/lifecyclectl.py activate   --plan .ai-work/<plan-id> --json
```

20. Start execution immediately after all gates pass unless a genuine safety gate requires approval.

Do not replace analysis with a shallow checklist. Do not use generic TODOs such as "implement everything" or "finish migration." Split by independently failing outcomes and validation boundaries, not by arbitrary file count.

## Keep `TODO.md` intentionally terse

`TODO.md` is a status index, not a task specification.

- Render exactly one line per task: `- [ ] **001** - Task title`.
- Allow only a short `(in progress)` or `(blocked)` suffix.
- Do not include model, provider, effort, complexity, requirement ids, dependencies, attempts, validation commands, or task-definition paths.
- Keep detailed metadata in task files and `manifest.json`.
- Update status only through `planctl.py`; never hand-edit `TODO.md`.

## Resumable subtask checklist

Every schema-v4 task definition contains a controller-rendered checklist of stable subtasks. The manifest is authoritative: start, complete, or reset a checkpoint only through `planctl.py subtask-start`, `subtask-complete`, or `subtask-reset`. A parent TODO may complete only after every required subtask is complete. After process, host, or power interruption, preserve completed checkpoints and return only the interrupted `in_progress` subtask to `pending`, so a fresh worker can continue without the previous chat history.

## Non-negotiable execution contract

- Store planning state only under `.ai-work/<plan-id>/`.
- Preserve `study.json`, `STUDY.md`, `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, optional `CONTEXT.md`, optional scoped files under `contexts/`, validated target-specific files under `learnings/`, and one definition per TODO; include `REQUEST.md` when input came from a file.
- Treat `manifest.json` as the source of truth and update task state only through `planctl.py`.
- Treat `.ai-work/.active-plan.json` only as a discoverable pointer; `manifest.json` remains authoritative.
- Persist every transition before dispatching another worker so a new invocation can resume without chat history.
- Recover an orphaned `in_progress` task to `pending` without incrementing technical failures; preserve completed subtask checkpoints, return only an interrupted subtask to `pending`, and preserve partial source changes for the next worker and deterministic validation.
- Never start a native worker while a live external runner lease exists.
- Give each implementation worker exactly one task-definition path plus only the files listed under `Assigned execution context` and `Assigned validated learnings` in that task definition. Do not pass the parent chat, whole plan, study files, analysis files, future task definitions, result reports, worker logs, or unassigned context/learning files.
- Require the worker to report the exact assigned paths in `context_files_read` and `learning_files_read`; reject missing or extra reads.
- Treat context artifacts as immutable planning files.
- Treat learning artifacts as immutable orchestrator-generated projections. Create them only after source-task deterministic validation, only for predeclared untouched future TODOs, and validate their content against manifest state rather than trusting a hash alone.
- Persist subtask transitions through `planctl.py subtask-start`, `subtask-complete`, and `subtask-reset`; never let workers hand-edit task checklists or `manifest.json`.
- Do not complete a parent TODO until every required subtask is complete.
- Permit workers to read repository source, tests, build files, and runtime output relevant to their task.
- Permit another task definition only when allowlisted and needed for a dependency, ambiguity, or validation conflict; record the reason.
- Re-run every deterministic validation command outside the worker before marking success.
- Execute write-heavy tasks sequentially. Parallelize only read-only tasks or tasks isolated in separate worktrees.
- Count implementation and validation failures as technical failures. Do not count rate limits, exhausted credits, or temporary capacity.
- Escalate effort, then model tier, then provider only when evidence justifies it. Never claim unsupported routing.
- Re-enter the adaptive study gate when execution reveals a material unknown, contradictory contract, different version, new security or migration risk, or invalid task boundary.
- Summarize with an economy-tier model after all tasks pass.
- Delete only the verified plan directory. Never delete implementation changes, tests, commits, or unrelated content.

## Choose execution mode

### Native subagent mode

Use inside an active Claude Code or Codex IDE/CLI chat.

1. Rediscover the active plan and reload `manifest.json` from disk on every invocation; do not rely on prior chat context for execution state.
2. Keep study, planning, review, and state management in the orchestrator thread.
3. Dispatch one fresh native worker for the next runnable task.
4. Pass only the task-definition path, task id, repository root, isolation rules, completion-report contract, and the context assignments already referenced by the task definition.
5. Require the fresh worker to read every assigned context file and no unassigned context file.
6. Route model tier and reasoning effort when supported.
7. Receive the bounded completion report.
8. Re-run validation in the orchestrator and update state.

Do not recursively launch the same CLI when nested sessions are prohibited.

### Strict external-runner mode

Use the lifecycle-aware wrapper from an external terminal when fresh processes, automatic interruption recovery, an atomic runner lease, automatic rate-limit waiting, or exact CLI routing are required:

```bash
pae resume
# or
python <skill-dir>/scripts/lifecyclectl.py resume --repo-root .
```

The wrapper discovers the active plan, replaces only a stale lease, returns orphaned `in_progress` tasks to `pending` without counting a technical failure, and then delegates to `run_isolated.py`.

Read [references/WORKFLOW.md](references/WORKFLOW.md) for both modes and [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) before routing or escalation.

## Execute the task loop

1. Validate the attached study after every resume with `studyctl.py validate-plan`.
2. Get the next runnable task with `planctl.py next --json`.
3. Select and record the actual route.
4. Claim the task.
5. Spawn a fresh worker with only its definition and the exact context and validated-learning files assigned there.
6. Require a report matching `references/completion-report.schema.json`, including exact `context_files_read`, exact `learning_files_read`, completed subtask ids, and only predeclared reusable learnings.
7. Reject the report when assigned and reported reads differ or required subtasks remain incomplete, then re-run every validation command from the repository root.
8. Mark success only after deterministic validation passes.
9. On technical failure, record evidence and retry with the next escalation route.
10. On usage or rate limits, preserve state and resume without increasing technical-failure count.
11. If execution disproves the study or plan, stop downstream work and repeat study, planning, review, attachment, and all quality gates.
12. Continue until every task completes or one becomes blocked at its configured limit.

Do not stop after merely writing a plan when `autostart` is true.

## Finish and clean up

1. Confirm every task is complete and validated.
2. Use a fresh economy-tier summarizer for the user-facing handoff in the user's language.
3. Include outcomes, important files, validation evidence, remaining risks, and follow-ups without claiming unrecorded tests.
4. Mark the summary generated.
5. Return the summary before cleanup.
6. Clear active lifecycle state as soon as the final summary is durably marked generated:

```bash
python <skill-dir>/scripts/lifecyclectl.py deactivate   --plan .ai-work/<plan-id> --json
```

7. Run guarded cleanup:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```

If cleanup is interrupted after summary generation, the next default invocation must clear the terminal pointer and allow a new request. A retained completed plan is history, not active work.

Retain the plan for diagnosis if completion, validation, or summarization fails.

## Reference map

- Request-file and editor workflow: [references/INTAKE.md](references/INTAKE.md)
- Resumable lifecycle, default resume, leases, cancellation, and reset: [references/LIFECYCLE.md](references/LIFECYCLE.md)
- Adaptive internal and external study gate: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Study-spec example: [references/study-spec.example.json](references/study-spec.example.json)
- Deep planning and decomposition: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Minimal global and task-scoped worker context: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Plan schema and example: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Native and strict execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Model routing and escalation: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Installation: [references/INSTALLATION.md](references/INSTALLATION.md)
