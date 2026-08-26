---
name: plan-and-execute
description: Deeply study a large software request and its repository, pass an adaptive evidence gate before planning, create a requirements-traceable execution plan, and execute it as small isolated resumable TODOs with deterministic validation, Claude Code/Codex routing, evidence-based escalation, economical summarization, and safe cleanup. Use for long implementations, migrations, refactors, multi-workstream features, architecture-sensitive or test-heavy changes, and requests that must be decomposed without losing requirements or polluting worker context. Also use without arguments for guided request capture or with a requirements file path.
---

# Plan and Execute

Resolve the complete request, study internal and conditionally external evidence, prove that the evidence is sufficient before drafting requirements or TODOs, build and review a traceable plan, then execute one isolated verifiable TODO at a time.

## Resolve the request before study or planning

Treat invocation input in this order.

### 1. No arguments: create an editable request draft

When invoked with no request text or file path:

1. Run from the repository root:

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

- Read the complete request before collecting evidence or drafting TODOs.
- Inventory every distinct outcome, constraint, activity, test expectation, compatibility need, migration, risk, and non-goal as a stable request part such as `P001`.
- Identify material questions that can change architecture, compatibility, risk, task boundaries, or validation.
- Always inspect relevant internal repository evidence before planning: instructions, architecture, implementation, tests, build files, schemas, interfaces, CI, and explanatory history.
- Evaluate every external-research trigger explicitly after the first internal scan.
- Research authoritative external sources only when one or more triggers are true, including explicit user request, unfamiliar domain, version-sensitive or current behavior, security sensitivity, repository gaps, conflicting evidence, technology selection, or high risk.
- Record a substantive reason when external research is unnecessary. Never make web research mandatory for a fully repository-local change with sufficient internal evidence.
- Do not draft requirements or executable TODOs until `studyctl.py validate` passes.
- Translate study findings exactly into plan constraints, derived requirements, risks, and validation implications.
- Map every request-part id to at least one requirement id, every requirement to at least one executable TODO, and every TODO back to requirements.
- Recursively split work until each TODO has one coherent outcome and an independent validation path.
- Reject executable `extreme` work and split it further.
- Require a substantive atomicity rationale for every `high` complexity TODO.
- Review the study and the plan in fresh contexts whenever supported.
- Do not autostart until `studyctl.py validate-plan`, `planctl.py validate`, and `planctl.py audit` all succeed.

Read [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md) before collecting evidence. Then read [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md) before drafting the plan.

## Pass the adaptive study gate before planning

1. Parse the request into stable request parts and material questions.
2. Inspect repository sources and record each concrete location, finding, and planning impact.
3. Evaluate all external-research triggers only after the initial repository scan.
4. When triggered, research primary authoritative sources matching the repository's exact version or date whenever possible.
5. Resolve high-impact questions, reconcile contradictions, and synthesize exact planning constraints, derived requirements, risks, and validation implications.
6. Review evidence sufficiency and record why further research is unlikely to change the plan materially.
7. Write `/tmp/study-spec.json` following [references/study-spec.example.json](references/study-spec.example.json).
8. Validate it before drafting requirements or TODOs:

```bash
python <skill-dir>/scripts/studyctl.py validate \
  --spec /tmp/study-spec.json
```

If the study is blocked or not ready, do not plan. Resolve the gap, record a bounded low-risk assumption, or request user input only when a high-impact decision cannot be inferred safely.

## Build the traceable plan

1. Copy every internal study `finding` exactly into `request_analysis.repository_findings`.
2. Copy every external source `finding` exactly into `request_analysis.research_findings`.
3. Record the external decision and rationale in `request_analysis.research_decision`.
4. Copy every synthesized risk exactly into `request_analysis.risks`.
5. Copy every synthesized planning constraint exactly into `global_constraints`.
6. Create stable requirements such as `R001`; copy every synthesized derived requirement exactly as requirement text.
7. Group requirements into workstreams and recursively split each into executable leaf TODOs.
8. Include every synthesized validation implication in at least one task acceptance criterion, implementation note, or validation command.
9. Give every TODO one objective, mapped requirements, complexity, atomicity rationale, scope boundaries, dependencies, expected files, acceptance criteria, validation commands, provider preference, model tier, and reasoning effort.
10. Start a fresh plan reviewer with the request, compact evidence, requirements, and draft graph, but no implementation assignment.
11. Revise until coverage, atomicity, dependencies, and validation all pass with no unresolved findings.
12. Write `/tmp/plan-spec.json` following [references/PLAN_SPEC.md](references/PLAN_SPEC.md).
13. Create the plan with the correct request-file mode from the input rules.
14. Attach the validated study and prove that its findings affected the plan:

```bash
python <skill-dir>/scripts/studyctl.py attach \
  --spec /tmp/study-spec.json \
  --plan .ai-work/<plan-id>
```

15. Run all quality gates:

```bash
python <skill-dir>/scripts/studyctl.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
```

16. Start execution immediately after all gates pass unless a genuine safety gate requires approval.

Do not replace analysis with a shallow checklist. Do not use generic TODOs such as "implement everything" or "finish migration." Split by independently failing outcomes and validation boundaries, not by arbitrary file count.

## Keep `TODO.md` intentionally terse

`TODO.md` is a status index, not a task specification.

- Render exactly one line per task: `- [ ] **001** - Task title`.
- Allow only a short `(in progress)` or `(blocked)` suffix.
- Do not include model, provider, effort, complexity, requirement ids, dependencies, attempts, validation commands, or task-definition paths.
- Keep detailed metadata in task files and `manifest.json`.
- Update status only through `planctl.py`; never hand-edit `TODO.md`.

## Non-negotiable execution contract

- Store planning state only under `.ai-work/<plan-id>/`.
- Preserve `study.json`, `STUDY.md`, `ANALYSIS.md`, `PLAN.md`, `PLAN_REVIEW.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, and one definition per TODO; include `REQUEST.md` when input came from a file.
- Treat `manifest.json` as the source of truth and update task state only through `planctl.py`.
- Give each implementation worker exactly one task-definition path. Do not pass the parent chat, whole plan, study files, analysis files, or future task definitions.
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

1. Keep study, planning, review, and state management in the orchestrator thread.
2. Dispatch one fresh native worker for the next runnable task.
3. Pass only the task-definition path, task id, repository root, isolation rules, and completion-report contract.
4. Route model tier and reasoning effort when supported.
5. Receive the bounded completion report.
6. Re-run validation in the orchestrator and update state.

Do not recursively launch the same CLI when nested sessions are prohibited.

### Strict external-runner mode

Use `scripts/run_isolated.py` from an external terminal when fresh processes, automatic rate-limit waiting, or exact CLI routing are required:

```bash
python <skill-dir>/scripts/run_isolated.py --plan .ai-work/<plan-id>
```

Read [references/WORKFLOW.md](references/WORKFLOW.md) for both modes and [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) before routing or escalation.

## Execute the task loop

1. Validate the attached study after every resume with `studyctl.py validate-plan`.
2. Get the next runnable task with `planctl.py next --json`.
3. Select and record the actual route.
4. Claim the task.
5. Spawn a fresh worker with only its definition.
6. Require a report matching `references/completion-report.schema.json`.
7. Re-run every validation command from the repository root.
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
6. Run guarded cleanup:

```bash
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```

Retain the plan for diagnosis if completion, validation, or summarization fails.

## Reference map

- Request-file and editor workflow: [references/INTAKE.md](references/INTAKE.md)
- Adaptive internal and external study gate: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Study-spec example: [references/study-spec.example.json](references/study-spec.example.json)
- Deep planning and decomposition: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Plan schema and example: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Native and strict execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Model routing and escalation: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Installation: [references/INSTALLATION.md](references/INSTALLATION.md)
