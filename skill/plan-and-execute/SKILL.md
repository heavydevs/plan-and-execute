---
name: plan-and-execute
description: Deeply study a large software request and the relevant repository before creating a requirements-traceable execution plan, then execute it as small, isolated, resumable TODOs with one definition file per task, deterministic validation, Claude Code/Codex model routing, escalation after technical failures, low-cost final summarization, and safe cleanup. Use for long implementations, migrations, refactors, multi-workstream features, architecture-sensitive changes, test-heavy work, or any request that must be decomposed carefully without losing requirements or polluting worker context. Also use when invoked without arguments to collect a detailed request in an editor, or when invoked with a requirements file path.
---

# Plan and Execute

Collect or resolve the complete request, study it and the repository deeply, build a traceable and independently reviewed plan, then execute one isolated, verifiable TODO at a time.

## Resolve the request before planning

Treat invocation input in this order.

### 1. No arguments: create an editable request draft

When the skill is invoked with no request text or file path:

1. Run from the repository root:

```bash
python <skill-dir>/scripts/requestctl.py create --repo-root . --json
```

2. Preserve the returned absolute `path` in the current orchestrator context.
3. Tell the user that the file was created and opened. If VS Code is detected, the helper opens it in the active VS Code window; otherwise it tries the configured or platform editor.
4. Present an easy confirmation action using the returned `confirmation_label`:
   - prefer the client-native choice/button UI when available;
   - otherwise show **Continue — I finished writing the request** and **Reopen the request file** as the only two obvious choices.
5. End the turn. Do not inspect the repository, plan, or execute yet.

When the user confirms completion:

1. Validate the preserved path:

```bash
python <skill-dir>/scripts/requestctl.py validate --file "<request-path>" --json
```

2. If validation reports incomplete content, reopen it and ask the user to finish it:

```bash
python <skill-dir>/scripts/requestctl.py reopen --file "<request-path>" --json
```

3. If the path was lost after a resumed session, recover the newest draft:

```bash
python <skill-dir>/scripts/requestctl.py latest --repo-root . --json
```

4. Extract only the user-authored body and use it as the complete request:

```bash
python <skill-dir>/scripts/requestctl.py extract --file "<request-path>"
```

5. After analysis and plan-spec creation, import the generated draft with move semantics so it becomes `.ai-work/<plan-id>/REQUEST.md` and leaves the intake folder:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json \
  --request-file "<request-path>" \
  --move-request
```

Read [references/INTAKE.md](references/INTAKE.md) for editor detection, recovery, language, validation, and safety details.

### 2. One existing file path: use it as the request

When the entire invocation argument, after normal quote handling, resolves to an existing regular file:

1. Treat it as the authoritative requirements/task-description file.
2. Validate and extract it with `requestctl.py`.
3. Study every requirement in that file; do not reduce it to disconnected snippets.
4. Import it when creating the plan, but preserve the caller-owned source by omitting `--move-request`:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json \
  --request-file "<provided-file>"
```

Reject symlinks, directories, missing files, and files without meaningful instructions. Do not silently fall back to treating a path-like argument as inline prose when the user clearly intended a file.

### 3. Any other non-empty arguments: use inline request text

Treat the full argument text as the request. Preserve all details, examples, constraints, test expectations, and referenced paths. Continue with the planning contract below.

## Non-negotiable planning contract

- Read the complete request before drafting any TODO.
- Inventory every distinct requested outcome, constraint, activity, test expectation, compatibility need, migration, risk, and non-goal as a stable request part such as `P001`.
- Inspect relevant repository instructions, architecture, implementation, tests, build files, schemas, interfaces, and CI commands before choosing task boundaries.
- Research unfamiliar, current, version-sensitive, or security-sensitive behavior with authoritative sources when materially needed. Record why research was or was not needed.
- Map every request-part id to at least one stable requirement id.
- Map every requirement id to at least one executable TODO.
- Map every TODO back to one or more requirement ids.
- Recursively split work until each executable TODO has one coherent outcome and an independent validation path.
- Reject an executable TODO rated `extreme`; split it further.
- Require a substantive atomicity rationale for every `high` complexity TODO.
- Review the draft plan in a fresh subagent or process whenever supported. Revise until coverage, atomicity, dependencies, and validations all pass.
- Do not autostart until `planctl.py validate` and `planctl.py audit` both succeed.

Read [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md) before planning. It defines the mandatory study, recursive decomposition, traceability, reviewer, and quality-gate procedure.

## Plan deeply

1. Parse the complete request into stable request parts such as `P001`.
2. Inspect the repository and record concrete findings.
3. Decide whether external research is needed and record findings or the reason it is unnecessary.
4. Create stable requirements such as `R001`; map every user-sourced requirement to its originating `request_part_ids`.
5. Group requirements into workstreams, then recursively split each workstream into executable leaf TODOs.
6. Give every TODO one objective, mapped requirements, complexity, atomicity rationale, scope boundaries, dependencies, expected files, acceptance criteria, validation commands, provider preference, logical model tier, and reasoning effort.
7. Start a fresh plan reviewer with the request, compact analysis, requirements, and draft task graph, but no implementation assignment.
8. Revise until review passes with no unresolved findings.
9. Write a JSON plan spec following [references/PLAN_SPEC.md](references/PLAN_SPEC.md).
10. Create the plan using the correct request-file mode from the input rules above.
11. Run both quality gates:

```bash
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

12. Start execution immediately after both pass unless a genuine safety gate requires explicit approval.

Do not replace analysis with a shallow checklist. Do not use generic TODOs such as “implement everything” or “finish migration.” Split by independently failing outcomes and validation boundaries without creating artificial file-by-file microtasks.

## Keep `TODO.md` intentionally terse

`TODO.md` is a status index, not a task specification.

- Render exactly one line per task: `- [ ] **001** — Task title`.
- Allow only a short `(in progress)` or `(blocked)` suffix when needed.
- Do not include model, provider, reasoning effort, complexity, requirement ids, dependencies, attempt counts, validation commands, or task-definition paths in `TODO.md`.
- Keep all of those details inside the corresponding file under `tasks/` and in `manifest.json`.
- Update TODO status only through `planctl.py`; do not hand-edit it.

## Non-negotiable execution contract

- Store state under `.ai-work/<plan-id>/`; never mix planning files with implementation files.
- Create `REQUEST.md` when input came from a file, plus `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, and one task definition per TODO.
- Treat `manifest.json` as the source of truth and update state only through `scripts/planctl.py`.
- Give an implementation worker exactly one task-definition path. Do not paste the parent chat, whole plan, analysis files, or future task definitions.
- Permit workers to read repository source, tests, build files, and runtime output relevant to their assigned task.
- Permit another task definition only when allowlisted and required by a dependency, ambiguity, or validation conflict; record the reason.
- Validate every task with deterministic commands outside the worker before marking it complete.
- Execute write-heavy tasks sequentially. Parallelize only read-only tasks or tasks isolated in separate worktrees.
- Count implementation or validation failures as technical failures. Do not count rate limits, exhausted credits, or temporary capacity as technical failures.
- Escalate effort first, then model tier, then provider when allowed. Never claim a route the runtime could not honor.
- Summarize with an economy-tier model after every task passes.
- Delete only the verified plan directory. Never delete source changes, tests, commits, or unrelated repository content.

## Choose execution mode

### Native subagent mode

Use inside an active Claude Code or Codex IDE/CLI chat.

1. Keep planning, review, and state management in the orchestrator thread.
2. Dispatch one fresh native worker for the next runnable task.
3. Pass only task-definition path, task id, repository root, isolation rules, and completion-report contract.
4. Route model tier and reasoning effort when supported.
5. Receive the bounded completion report.
6. Re-run validation in the orchestrator, then update state.

Do not recursively launch the same CLI from inside itself when nested sessions are prohibited.

### Strict external-runner mode

Use `scripts/run_isolated.py` from an external terminal when process-level fresh sessions, automatic rate-limit waiting, or exact CLI routing are required:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

Read [references/WORKFLOW.md](references/WORKFLOW.md) for both execution procedures and commands. Read [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) before choosing or escalating routes.

## Execute the task loop

1. Get the next runnable task with `planctl.py next --json`.
2. Select and record the actual route.
3. Claim the task.
4. Spawn a fresh worker with only its definition.
5. Require a report matching `references/completion-report.schema.json`.
6. Re-run every validation command from the repository root.
7. Mark success only after deterministic validation passes.
8. On technical failure, record evidence and retry with the next escalation route.
9. On rate or usage limits, preserve state and resume without increasing technical-failure count.
10. If execution reveals missing scope, wrong dependencies, or an oversized TODO, stop downstream work and replan through the complete protocol.
11. Continue until every task completes or a task becomes blocked at its configured limit.

Do not stop after merely writing a plan when `autostart` is true.

## Finish and clean up

1. Confirm every task is completed and validated.
2. Use a fresh economy-tier summarizer to produce the user-facing handoff in the user's language.
3. Include outcomes, important files, validation results, remaining risks, and follow-ups without claiming unrecorded tests.
4. Mark the summary generated.
5. Return the summary before cleanup.
6. Run guarded cleanup:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```

If completion or summarization fails, retain the plan for diagnosis and resume from disk later.

## Reference map

- Request-file/editor workflow: [references/INTAKE.md](references/INTAKE.md)
- Deep study and decomposition: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Plan schema and examples: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Native and strict execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Model routing and escalation: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Installation: [references/INSTALLATION.md](references/INSTALLATION.md)
