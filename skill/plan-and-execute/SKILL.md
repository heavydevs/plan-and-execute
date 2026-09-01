---
name: plan-and-execute
description: Plan and execute software changes with adaptive study, requirements-traceable TODOs, fresh isolated workers, resumable checkpoints, selective cross-task learnings, deterministic validation, model/provider escalation, and safe lifecycle cleanup. Use for implementations, migrations, refactors, multi-workstream or test-heavy changes, resuming/cancelling/resetting plan state, guided request intake, or a requirements file path.
---

# Plan and Execute

Treat context as a budget. Persist authoritative state on disk, give each model only the smallest evidence surface needed for its current decision, and move deterministic work to scripts. Never trade away requirement coverage, validation, recovery, or safety merely to save tokens.

## 1. Route lifecycle commands first

When the complete invocation is exactly `current`/`status`, `resume`/`continue`, `cancel`, or `reset`, handle it before interpreting a software request.

- `current` / `status`: run `lifecyclectl.py current --repo-root . --json`.
- `resume` / `continue`: recover and continue the unique active plan; use fresh workers, never the old chat transcript.
- `cancel`: remove the active plan/lifecycle artifacts while preserving repository implementation changes.
- `reset`: remove every recognized plan-and-execute artifact while preserving repository implementation changes.

Read [references/LIFECYCLE.md](references/LIFECYCLE.md) only for lifecycle operations.

## 2. Resolve the request without preloading unrelated guidance

- No arguments: run `lifecyclectl.py current --repo-root . --json`. Resume when active; otherwise use the guided request flow in [references/INTAKE.md](references/INTAKE.md).
- One existing regular file path: validate/extract it with `requestctl.py` and preserve it as planning evidence.
- Any other non-empty input: treat the complete text as authoritative inline requirements.

Read the complete request once. Preserve every requested outcome, constraint, example, test expectation, compatibility need, risk, and non-goal. Do not load planning, provider, or execution references until their phase begins.

## 3. Pass the adaptive study gate

Classify before broad repository exploration:

- `simple`: direct, low-risk, fully scoped; internal and external study may both be `none`.
- `medium`: bounded discovery is useful; automatically use `related_packages` or `workspace_keywords`, search before opening files, and use focused external research only for a material trigger.
- `complex`: architecture, migration, security, compatibility, data integrity, ownership, provider choice, or another high-impact uncertainty can change the plan. Ask the fixed study choices unless the request already selected them:
  - Internal: **Pacotes relacionados** / **Busca por palavras-chave em todo o workspace** / **Projeto completo**.
  - External: **Sem estudo externo** / **Pesquisa focalizada** / **Pesquisa ampla**.

For complex requests, a user request for broad/deep repository and internet study counts as `Projeto completo` + `Pesquisa ampla`.

Read [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md) when entering this phase. Write and validate study schema v2 before drafting executable TODOs. Record findings, not raw source dumps. Stop when more evidence is unlikely to change architecture, compatibility, task boundaries, risk, or validation.

## 4. Build a traceable, context-cohesive plan

Read [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md), then [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md). Read [references/PLAN_SPEC.md](references/PLAN_SPEC.md) only when producing the plan spec.

Required plan properties:

- Stable request parts (`P...`) and requirements (`R...`) with complete bidirectional coverage.
- Every executable TODO has one coherent outcome, one independent validation path, explicit dependencies/scope, bounded expected files, acceptance criteria, validation commands, routing, `context_boundary`, and stable resumable subtasks.
- Split unrelated domains even when they share a framework pattern. Keep tightly coupled layers together when they implement one invariant and benefit from the same worker context.
- No executable `extreme` TODO; `high` TODOs need a substantive atomicity rationale.
- Shared execution context is omitted by default. `CONTEXT.md` is only for indispensable facts needed by every TODO; scoped context files are only for strict multi-task subsets; single-task facts stay in the task definition.
- `learning_targets` are sparse, directional, predeclared, target-specific, and limited to expensive validated knowledge that a later similar TODO would otherwise need to rediscover.
- Review must approve coverage, atomicity, dependencies, validation, `contexts_minimal`, and `context_boundaries_sound`.

Create/attach the plan only after study validation, then require all gates:

```bash
python <skill-dir>/scripts/studyctl.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl.py audit --plan .ai-work/<plan-id>
python <skill-dir>/scripts/lifecyclectl.py activate --plan .ai-work/<plan-id> --json
```

Autostart after the gates unless a genuine safety gate blocks execution.

## 5. Execute one isolated TODO at a time

Read [references/WORKFLOW.md](references/WORKFLOW.md) when execution begins and [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) only when choosing/escalating a route.

For every TODO:

1. Reload authoritative state from disk; do not rely on prior chat history.
2. Claim only the next runnable TODO.
3. Start a fresh worker with exactly one task-definition path plus only its assigned context/validated-learning files. Do not pass the parent chat, whole plan, study files, future task files, logs, or previous raw reports.
4. Let the worker read repository source/tests/build/runtime output relevant to the TODO.
5. Persist subtask checkpoints only through `planctl.py`.
6. Require the bounded completion report, including exact assigned read lists and completed subtask ids.
7. Re-run every deterministic validation command outside the worker before marking success.
8. Materialize only predeclared, concise, validated target-specific learnings.
9. On technical failure, preserve evidence and escalate effort/model/provider only as justified. Rate/usage limits do not count as technical failures.
10. If execution disproves a material study/plan assumption, stop downstream work and re-enter the study/planning gates.

Write-heavy TODOs are sequential unless isolated in separate worktrees. Fresh-worker isolation is preferred over retaining conversational history.

## 6. Apply the token-efficiency contract throughout

Read [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md) when optimizing prompts/context, reviewing the plan for token cost, or changing the harness. Core rules always apply:

- Prefer paths/ids over embedding file contents.
- Search/filter before opening; open only high-signal ranges/files.
- Persist compact structured state; never preserve chat transcripts as execution memory.
- Put stable instructions before task-specific dynamic data when the provider can benefit from prompt caching.
- Keep tool/source output bounded and promote only validated conclusions into future context.
- Use deterministic code for filtering, aggregation, validation, status transitions, and cleanup; spend model tokens on judgment.
- Prefer the cheapest route likely to succeed and escalate from evidence, not fear.
- Do not compress away contracts, acceptance criteria, invariants, failure evidence needed for the current task, or deterministic validation.

## 7. Finish, hand off, and delete only planning state

After the final TODO and final deterministic verification both pass:

1. Generate a concise final handoff from authoritative completed-task state and validation evidence; use an economy-tier summarizer when supported.
2. Mark the summary generated.
3. Clear the active lifecycle pointer.
4. Run guarded cleanup:

```bash
python <skill-dir>/scripts/lifecyclectl.py deactivate --plan .ai-work/<plan-id> --json
python <skill-dir>/scripts/planctl.py cleanup --plan .ai-work/<plan-id>
```

Cleanup is mandatory on successful completion unless the user explicitly requested plan retention. Delete only the verified `.ai-work/<plan-id>/` planning/control workspace (and an empty work-root when safe). Preserve all implementation changes, tests, generated product artifacts, commits, and unrelated repository files. If completion, final validation, or summary generation fails, retain the plan for diagnosis/resume.

## Reference map

Load references just in time, not all at invocation:

- Intake: [references/INTAKE.md](references/INTAKE.md)
- Lifecycle/resume/cancel/reset: [references/LIFECYCLE.md](references/LIFECYCLE.md)
- Study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Planning/decomposition: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context/learnings: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution modes: [references/WORKFLOW.md](references/WORKFLOW.md)
- Routing/escalation: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Token/context economics: [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md)
- Installation: [references/INSTALLATION.md](references/INSTALLATION.md)
