---
name: plan-and-execute
description: Plan and execute software changes with adaptive study, requirements-traceable TODOs, fresh isolated workers, resumable checkpoints, selective cross-task learnings, deterministic validation, model/provider escalation, and safe lifecycle cleanup. Use for implementations, migrations, refactors, multi-workstream or test-heavy changes, resuming/cancelling/resetting plan state, guided request intake, or a requirements file path.
---

# Plan and Execute

Treat context as a budget. Preserve the user's complete request as evidence, but keep every **derived** study, plan, TODO, context, learning, report, and handoff objective, precise, atomic, and bounded. Never save tokens by weakening requirements, traceability, validation, recovery, or safety.

## 1. Route lifecycle commands first

For exact `current`/`status`, `resume`/`continue`, `cancel`, or `reset`, route before request parsing with `lifecyclectl_concise.py`.

- `current` / `status`: inspect lifecycle state.
- `resume` / `continue`: recover the unique unfinished plan and continue with fresh workers.
- `cancel`: delete the active planning/control workspace; preserve implementation changes.
- `reset`: delete recognized plan-and-execute workspaces; preserve implementation changes.

Read [references/LIFECYCLE.md](references/LIFECYCLE.md) only for lifecycle operations.

## 2. Resolve the request

- No arguments: inspect lifecycle state; if idle, use [references/INTAKE.md](references/INTAKE.md).
- One existing regular file: validate/extract it with `requestctl.py` and preserve it as request evidence.
- Otherwise: use the complete inline text.

Never truncate or rewrite the user's original request merely to save tokens. Concision begins when creating derived artifacts.

Before producing derived text, read [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md). Its contract is mandatory: one semantic job per field, concrete nouns/conditions, observable outcomes, bounded prose, no filler, and no unresolved vague wording in executable requirements.

## 3. Pass the adaptive study gate

Classify before broad exploration:

- `simple`: direct, low-risk, fully scoped; study may be skipped with a precise reason.
- `medium`: search/filter first; use related-package or workspace-keyword discovery and focused external research only when material.
- `complex`: resolve two fixed single-select choices in sequence. Ask **only the internal-study question first**, using native multiple-choice UI when available, and end the turn. After that answer, ask **only the external-study question** in a new turn and end that turn. Never combine or preview both questions. Reuse choices already explicit in the request instead of asking again. A user request for broad/deep repository + internet study selects both broad options automatically.

The fixed internal choices are **Pacotes relacionados**, **Busca por palavras-chave em todo o workspace**, and **Projeto completo**. The fixed external choices are **Sem estudo externo**, **Pesquisa focalizada**, and **Pesquisa ampla**.

Read [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md). Validate/attach study state with `studyctl_concise.py`.

Study artifacts record conclusions, not research narration:

- one evidence item = finding + planning impact;
- cite exact path/symbol/source where possible;
- omit search history, dead ends, generic observations, and raw source dumps;
- stop when additional evidence is unlikely to change architecture, compatibility, TODO boundaries, risk, or validation.

## 4. Build a traceable, context-cohesive plan

Read [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md), [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md), then [references/PLAN_SPEC.md](references/PLAN_SPEC.md) when writing the spec.

Required properties:

- stable request parts (`P...`) and requirements (`R...`) with bidirectional coverage;
- one coherent outcome and independent validation boundary per executable TODO;
- explicit scope, dependencies, acceptance, validation, routing, `context_boundary`, and resumable subtasks;
- unrelated domains split even when framework patterns match;
- no executable `extreme` TODO; justify retained `high` TODOs;
- shared execution context omitted by default; `CONTEXT.md` only for facts required by every TODO; scoped files only for strict multi-TODO subsets;
- sparse, directional `learning_targets` only for expensive validated knowledge a later TODO would otherwise rediscover;
- review approval of coverage, atomicity, dependencies, validation, `contexts_minimal`, and `context_boundaries_sound`.

Derived fields must satisfy the artifact-writing budgets. Short precise text is preferred to padded rationale. Do not use minimum length as a reason to repeat context.

Create and gate with the concise controller:

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py audit --plan .ai-work/<plan-id>
python <skill-dir>/scripts/lifecyclectl_concise.py activate --plan .ai-work/<plan-id> --json
```

Autostart after all gates unless a genuine safety gate blocks execution.

## 5. Execute one isolated TODO at a time

Read [references/WORKFLOW.md](references/WORKFLOW.md) when execution begins and [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) only for routing/escalation.

For each TODO:

1. Reload authoritative state from disk.
2. Claim only the next runnable TODO through `planctl_concise.py`.
3. Start a fresh worker with one task-definition path plus exactly its assigned context/learning files; never pass parent chat, whole plan, study files, future task files, raw reports, or logs.
4. Let the worker inspect only repository evidence needed for that TODO.
5. Checkpoint subtasks through `planctl_concise.py`; never edit planning Markdown for state.
6. Require the bounded completion-report schema: concise summary/details, exact read lists, completed subtask ids, and only predeclared reusable learnings.
7. Re-run every deterministic validation command outside the worker before success.
8. Persist only compact completion memory needed for final handoff; full provider/tool output stays in logs.
9. Escalate effort/model/provider only after concrete technical evidence; usage/rate limits are not technical failures.
10. If execution disproves a material planning assumption, stop downstream work and re-enter study/planning gates.

Strict external execution uses:

```bash
python <skill-dir>/scripts/run_concise.py --plan .ai-work/<plan-id>
```

The compact worker task file is an execution contract, not a duplicate planning dossier. Planning-only atomicity/review prose stays authoritative in `manifest.json` rather than being repeated for every worker.

## 6. Apply the token-efficiency contract

Read [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md) when reviewing context cost or changing the harness.

Always:

- prefer ids/paths/symbols/commands over repeated explanation;
- search/filter before opening files;
- use structured state instead of chat history;
- keep stable prompt prefixes before dynamic data when caching can help;
- bound logs, failure excerpts, validation tails, worker reports, and final-summary input;
- use deterministic code for filtering, state, validation, and cleanup; spend model tokens on judgment;
- route each TODO to the cheapest model/effort credibly able to solve it;
- preserve complete requirements, task invariants, acceptance criteria, material failure evidence, validation commands/outcomes, checkpoints, and safety checks.

## 7. Finish and remove planning state

After the last TODO and final deterministic validation pass:

1. Build final-summary input from compact authoritative task state, validation results, and bounded repository-change evidence — never raw worker reports.
2. Generate the concise handoff with the economy summary route when available.
3. Mark the summary generated and clear the active lifecycle pointer.
4. Run guarded cleanup with `planctl_concise.py cleanup`.

Cleanup is mandatory on successful completion unless the user explicitly requests plan retention. Delete only the verified `.ai-work/<plan-id>/` planning/control workspace (and an empty work root when safe). **Preserve all implementation changes**, tests, product artifacts, commits, and unrelated repository files. If completion, final validation, or summary generation fails, retain plan state for diagnosis/resume.

## Reference map

Load only the phase-specific reference:

- Precise derived writing: [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md)
- Intake: [references/INTAKE.md](references/INTAKE.md)
- Lifecycle: [references/LIFECYCLE.md](references/LIFECYCLE.md)
- Study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Planning: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context/learnings: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Routing: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Token economics: [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md)
- Installation: [references/INSTALLATION.md](references/INSTALLATION.md)
