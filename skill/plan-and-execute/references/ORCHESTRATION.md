# Full orchestration workflow — final plan

Read only after the entrypoint selected **FINAL_PLAN**, including a completed PRIMARY_PLAN handoff or late promotion. Oversized-source preprocessing belongs to `PRIMARY_PLANNING.md`; do not load it here.

## 1. Resolve final-planning input

Use this order:

1. lifecycle commands were already routed before this reference;
2. with no arguments, resume the unique unfinished plan first; create guided intake only when idle (`INTAKE.md`, `LIFECYCLE.md`);
3. for a PRIMARY_PLAN handoff, read `PLANNING_INPUT_CONTRACT.md`, start from `FINAL_PLAN_INPUT.md`, and retrieve immutable source fragments only when a material planning decision needs primary evidence;
4. for one ordinary request file, validate/extract it with `requestctl.py`;
5. otherwise use the complete manageable inline request.

For promoted DIRECT work, completed implementation is current-state evidence and only `remaining_outcomes` becomes executable work. Preserve user-authored evidence. Before writing derived artifacts, follow `ARTIFACT_WRITING.md`.

## 2. Route planning capability separately

Planning does not inherit the root chat model. Read `PLANNING_ROUTING.md` only when assigning planning-stage routes.

- deterministic lookup/filtering/splitting/indexing stays in tools;
- bounded extraction can use economy capability;
- ordinary synthesis normally uses standard;
- architecture, security, migration, data-integrity, high-impact decomposition, or weakly verifiable decisions can require strong;
- fresh review should be strong enough to challenge the hardest material decision;
- max/frontier is evidence-driven.

Planning routes and implementation routes are independent.

## 3. Study only what can change the plan

Read `ADAPTIVE_STUDY.md`. Study repository/external evidence only when uncertainty can change architecture, compatibility, TODO boundaries, shared patterns, risk, or validation. Search/filter before broad reads.

Prepared packages start from digests/indexes and retrieve source fragments only for verification; do not reconstruct the entire original source in one context. Validate study with `studyctl_concise.py`.

## 4. Build requirements-traceable TODOs

While drafting, read `PLANNING_PROTOCOL.md`, `EXECUTION_CONTEXT.md`, and `PLAN_SPEC.md`.

Inventory request parts (`P...`) and observable requirements (`R...`). Map every request part -> requirement -> executable TODO and every TODO back to requirements.

Recursively split until each TODO has:

- one coherent outcome and independent validation boundary;
- a context surface whose reasoning is useful throughout that TODO;
- explicit scope in/out and expected files;
- dependencies, acceptance criteria, deterministic validation commands, and resumable subtasks;
- `context_boundary` plus sparse `learning_targets` when needed;
- `provider`, `model_tier`, and `reasoning_effort` selected for the implementation leaf.

Split unrelated domains even if they share a framework pattern. Do not split mechanically per file when controller/service/entity/migration/tests implement one invariant. Reject executable `extreme` TODOs; justify retained `high` leaves. Never create retroactive TODOs for implementation already completed before promotion.

## 5. Separate context, learning, and evolving patterns

Execution context is omission-first:

- global `CONTEXT.md` only for non-obvious facts required by every TODO;
- scoped contexts only for facts shared by a strict subset;
- single-task facts stay in the task definition;
- runtime discoveries cross tasks only through predeclared validated learning targets.

Separately ask whether multiple TODOs share a **normative contract that may evolve**. If no, do not load `SHARED_PATTERNS.md` and create no registry. If yes, read it and create `/tmp/pattern-spec.json` only after TODO ids stabilize.

Good patterns include REST Resource facades, Admin CRUD conventions, SCSS/design tokens, error envelopes, or persistence invariants. `PATTERN_SEEDS.json` from PRIMARY_PLAN is evidence, not authority: the final planner chooses live patterns and signatories.

## 6. Preserve adaptive implementation routing

Read `MODEL_ROUTING.md` only when selecting/escalating implementation routes, then read only the chosen provider mapping when a concrete model is needed.

Logical tiers are `economy`, `standard`, `strong`, and `max`. Choose the lowest credible capability based on leaf difficulty, verifiability, and blast radius. Keep `provider: auto` unless provider-specific behavior is required. Record actual execution route separately so another compatible provider can resume.

Never inherit PRIMARY_PLAN routes into implementation.

## 7. Review and create the durable plan

Use a fresh reviewer for complex plans when supported. Revise until coverage, atomicity, dependencies, validations, context minimality, pattern signatories, and routing plausibility pass.

Create and gate with concise controllers:

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json [--request-file <file>]
python <skill-dir>/scripts/studyctl_concise.py attach --spec /tmp/study-spec.json --plan .ai-work/<plan-id>
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py audit --plan .ai-work/<plan-id>
```

If patterns were approved, initialize after plan creation so signatories reference final TODO ids:

```bash
python <skill-dir>/scripts/patternctl.py init --plan .ai-work/<plan-id> --spec /tmp/pattern-spec.json
python <skill-dir>/scripts/patternctl.py validate --plan .ai-work/<plan-id>
```

Activate lifecycle state, then autostart unless a genuine authorization/safety gate or unresolved material question blocks execution. For prepared packages retain only the compact handoff plus package/source references, not copies of every raw fragment.

## 8. Persist minimal resumable state

`manifest.json` is authoritative. `TODO.md` stays terse: one line per parent TODO. One definition file per TODO carries objective, assigned context/learnings, resumable subtasks, scope, non-obvious guidance, acceptance, validation, and logical route.

When patterns exist, `patterns/registry.json` owns revisions/signatories and `patternctl.py` projects task assignments. Pattern assignment is separate from immutable context because a revision can invalidate completed consumers.

Never hand-edit task/subtask status, retries, routing state, pattern revisions, adoption, or assignment projections.

## 9. Execute one isolated TODO at a time

Read `WORKFLOW.md` when execution begins. The standard `run_concise.py` path owns pattern hooks as well as ordinary task execution.

For each runnable TODO:

1. reload authoritative state and recover interrupted state when necessary;
2. validate shared-pattern registry when present;
3. choose the actual provider/model/effort route and claim the TODO;
4. start a **fresh worker** with exactly one task definition plus assigned context, learnings, and pattern files;
5. never pass parent chat, the whole plan, future task definitions, raw reports, or logs;
6. checkpoint subtasks only through controllers;
7. if implementation evidence requires a pattern revision, stop that task safely and revise through `patternctl` rather than diverging silently;
8. require the bounded completion report, including exact assigned artifacts read;
9. rerun deterministic validations outside the worker;
10. mark success only after validation passes; the runner records current pattern adoption automatically;
11. materialize only predeclared validated target-specific learnings.

Write-heavy tasks remain sequential unless isolated worktrees remove reconciliation risk.

## 10. Pattern revisions invalidate only signatories

Validated learning flows earlier -> later. Shared patterns differ: they may evolve and affect already-completed signatories.

When concrete evidence requires a contract change:

```bash
python <skill-dir>/scripts/patternctl.py update \
  --plan .ai-work/<plan-id> --pattern PAT001 \
  --contract-file /tmp/pattern-v2.json \
  --reason "Concrete evidence" --changed-by-task 006
```

`patternctl` increments the revision, preserves history, and resets only completed signatories that adopted an older revision. Pending signatories consume the newest revision later. Updating is rejected while another affected signatory is actively executing stale instructions.

This is dependency invalidation, not automatic full replanning. Re-enter planning only if evidence changes requirements, TODO boundaries, dependencies, or architecture outside the pattern contract. Final completion requires `patternctl validate` to pass.

## 11. Resume across quota/session/provider failure

Lifecycle state must survive lost credits, process termination, host restart, or provider switching.

On resume:

- discover the unique active/actionable plan;
- acquire/recover the runner lease;
- return only orphaned `in_progress` task/subtask state to runnable state;
- preserve completed work, pattern revisions/adoptions, prepared-package references, and partial repository changes;
- do not count quota/rate/capacity interruption as technical failure;
- dispatch from persisted task/context/pattern state, never prior chat history.

`run_concise.py` / `pae resume` performs these hooks for the standard runner.

## 12. Replan only when evidence invalidates structure

Re-enter necessary study/planning gates for contradictory contracts, new security/version/migration risk, invalid dependencies, wrong context boundaries, or pattern changes that alter task boundaries.

Do not replan because a worker used many tokens, a provider hit quota, or a pattern revision affects only declared signatories.

## 13. Finish and cleanup safely

Before handoff:

1. every TODO and deterministic final validation must pass;
2. `patternctl validate` must pass when patterns exist;
3. build summary input from compact authoritative task state, validations, pattern revision summary, and bounded repository-change evidence — never concatenate raw worker reports;
4. generate the user-facing handoff with an economy route when available;
5. mark summary generated, deactivate lifecycle state, and run guarded cleanup.

Cleanup removes planning/control state only. Preserve implementation changes, tests, generated product artifacts, commits, and unrelated repository content. Retain plan state whenever completion, validation, pattern adoption, or summary generation fails.