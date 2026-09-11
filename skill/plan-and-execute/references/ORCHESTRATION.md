# Full orchestration workflow — final plan

Read only after the entrypoint has selected **FINAL_PLAN**, including late promotion or a completed PRIMARY_PLAN handoff. This reference owns the ordinary implementation plan. It does **not** own oversized-source preprocessing; `PRIMARY_PLANNING.md` does.

## 1. Resolve the final-planning input

Treat input in this order:

1. Exact lifecycle commands were already routed before this reference.
2. No arguments: inspect lifecycle state. Resume the unique unfinished implementation first; create guided intake only when idle. See `INTAKE.md` and `LIFECYCLE.md`.
3. A prepared request package from PRIMARY_PLAN: read `PLANNING_INPUT_CONTRACT.md`, start from `FINAL_PLAN_INPUT.md`, and retrieve source fragments only when a planning decision needs primary evidence.
4. One existing ordinary request file: validate/extract it with `requestctl.py` and use it as authoritative request evidence.
5. Otherwise use the complete manageable inline request.

For promoted DIRECT work, the `promotectl.py render` output is authoritative. Completed work is current-state evidence; only `remaining_outcomes` becomes executable work.

Preserve user-authored evidence. Before producing derived study, requirement, plan, TODO, context, pattern, learning, or handoff text, read `ARTIFACT_WRITING.md`; compress only derived artifacts.

Do **not** read `PRIMARY_PLANNING.md` on this path. A prepared package already exposes the small final-planning interface needed here.

## 2. Route planning capability deliberately

Planning does not blindly inherit the root chat's model/effort. Read `PLANNING_ROUTING.md` when assigning planning-stage work.

- deterministic lookup/filtering/splitting/indexing stays in tools;
- bounded evidence extraction can use economy workers;
- ordinary requirement synthesis uses standard capability;
- architecture, high-impact decomposition, security/migration/data-integrity decisions, or weakly verifiable planning use strong capability;
- fresh plan review normally uses the capability required to challenge the hardest material planning decision;
- max/frontier planning is evidence-driven, not a reward for a large parent request.

Planning routes and implementation routes are independent.

## 3. Pass adaptive study before planning

Read `ADAPTIVE_STUDY.md`. Classify study depth from uncertainty that can change architecture, compatibility, task boundaries, risk, patterns, or validation.

- skip broad study when direct evidence already scopes the remaining work;
- search/filter before opening repository files broadly;
- use focused external research only when authoritative current facts materially affect the plan;
- use broad project/external study for genuinely complex architecture, migration, security, compatibility, or user-requested research;
- for prepared packages, start from compact digests/indexes and retrieve immutable fragments only for material verification instead of reconstructing the whole original document in context.

Validate study state with `studyctl_concise.py`. Do not manufacture evidence to satisfy a template. A late promotion studies only remaining work and current repository state.

## 4. Build requirements-traceable TODOs

Read `PLANNING_PROTOCOL.md`, `EXECUTION_CONTEXT.md`, and `PLAN_SPEC.md` only while drafting the plan.

Inventory stable request parts (`P...`) and requirements (`R...`) for every remaining independently testable outcome/constraint. Map each request part -> requirement -> executable TODO, and every TODO back to requirements.

Recursively split until every TODO has:

- one coherent outcome and one independent validation boundary;
- a context surface whose retained reasoning is useful throughout the TODO;
- explicit scope in/out and expected files;
- dependencies, acceptance criteria, and deterministic validation commands;
- resumable subtasks/checkpoints;
- `context_boundary` evidence and optional sparse `learning_targets`;
- `provider`, `model_tier`, and `reasoning_effort` selected for that implementation leaf.

Split unrelated domains even when they share a framework pattern. Do not split mechanically per file: tightly coupled controller/service/entity/migration/tests may remain together when they implement one invariant and benefit from one worker context.

Reject executable `extreme` TODOs; split further. Justify retained `high` leaves. For promoted work, never create retroactive TODOs for completed implementation; only remaining outcomes are planned.

## 5. Separate immutable context from evolving shared patterns

Default to no shared `CONTEXT.md`.

- global context only for non-obvious facts required by every TODO;
- scoped `contexts/<topic>.md` only when the same fact is needed by at least two but fewer than all TODOs;
- single-task information stays in that task definition;
- runtime discoveries cross task boundaries only through predeclared validated learning targets.

Then ask a distinct question: **does any normative contract need to be shared by multiple TODOs and possibly evolve during implementation?**

If no, do not read `SHARED_PATTERNS.md` and create no pattern registry.

If yes, read `SHARED_PATTERNS.md` and create a compact `/tmp/pattern-spec.json` after TODO ids stabilize. Promote only real cross-cutting contracts such as a REST Resource facade, shared Admin CRUD behavior, SCSS/token conventions, error envelopes, or persistence invariants. Do not duplicate these contracts in every TODO.

For prepared packages, `PATTERN_SEEDS.json` is evidence only. The final planner decides which seeds become live patterns and which TODOs sign them.

Review must approve minimal execution context and sound pattern signatories.

## 6. Preserve adaptive task-level model routing

Read `MODEL_ROUTING.md` only when choosing or escalating implementation routes. It defines provider-independent semantics. When a concrete provider/model must be chosen, read **only** that provider's reference.

Each TODO stores logical capability:

- `economy`: exploration, mechanical/narrow work, cheap summarization;
- `standard`: normal bounded implementation/debugging/tests;
- `strong`: subtle/high-risk/weakly verifiable or difficult evidence-heavy work;
- `max`: frontier/long-horizon work when semantic need or concrete lower-route failure justifies it.

Use the lowest credible capability for the leaf. Verifiability and blast radius matter more than overall request size. Keep `provider: auto` when equivalent providers may execute the task; pin only when the task genuinely depends on a provider. Record the actual execution route separately so another compatible AI can resume.

Never copy routes from a PRIMARY_PLAN task into implementation merely because both refer to the same source area.

## 7. Review and create the durable final plan

Use a fresh reviewer for complex plans when supported. Revise until coverage, atomicity, dependencies, validations, context minimality, context boundaries, pattern assignments, and routing plausibility pass with no unresolved material findings.

Create/gate using concise controllers:

```bash
python <skill-dir>/scripts/planctl_concise.py create --repo-root . --spec /tmp/plan-spec.json [--request-file <file>]
python <skill-dir>/scripts/studyctl_concise.py attach --spec /tmp/study-spec.json --plan .ai-work/<plan-id>
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py validate --plan .ai-work/<plan-id>
python <skill-dir>/scripts/planctl_concise.py audit --plan .ai-work/<plan-id>
```

If patterns were approved, initialize them **after** plan creation so signatories reference final stable TODO ids:

```bash
python <skill-dir>/scripts/patternctl.py init \
  --plan .ai-work/<plan-id> --spec /tmp/pattern-spec.json
python <skill-dir>/scripts/patternctl.py validate --plan .ai-work/<plan-id>
```

Then activate lifecycle state. Use request-file semantics from `INTAKE.md`. For a prepared package, preserve the compact final-planning handoff plus source/package references; do not copy every raw fragment into the final plan directory.

Autostart after gates unless a genuine safety/authorization gate or unresolved material question blocks execution.

## 8. Persist checklist, task definitions, and pattern assignments

`TODO.md` is terse: exactly one line per parent task, plus short in-progress/blocked suffix when applicable. Detailed task metadata belongs in `manifest.json` and one definition file per TODO.

Every task definition must be sufficient for a fresh compatible worker without parent chat. It includes objective, assigned execution context/learnings, resumable subtasks, scope, non-obvious guidance, acceptance, deterministic validation, and logical route recommendation.

When patterns exist, `patterns/registry.json` is authoritative for their revisions/signatories. `patternctl.py` projects one assignment file per TODO. Pattern assignment is separate from immutable execution context because pattern revisions can invalidate completed consumers.

Never hand-edit task/subtask status, retries, routing state, pattern revisions, signatory adoption, or assignment projections.

## 9. Execute one isolated TODO at a time

Read `WORKFLOW.md` when execution begins. For every runnable TODO:

1. reload authoritative plan state from disk;
2. recover stale/interrupted state when needed;
3. if patterns exist, validate the registry and obtain the exact pattern assignment for the TODO;
4. claim the next runnable TODO through `planctl_concise.py` with the actual provider/model/effort route;
5. start a fresh worker with exactly one task definition plus assigned context, learning, and pattern files;
6. never pass parent chat, whole plan, future task definitions, raw reports, or logs;
7. checkpoint subtasks only through the controller;
8. if evidence requires a shared-pattern change, use the guarded pattern-revision workflow rather than silently diverging;
9. require the bounded completion report with exact files/revisions read and completed subtask ids;
10. rerun every deterministic validation command outside the worker;
11. mark success only after validation passes;
12. after completion, record adoption of current assigned pattern revisions;
13. materialize only predeclared validated target-specific learnings;
14. continue until all tasks complete or one blocks at its configured limit.

Write-heavy tasks are sequential unless repository isolation/worktrees remove reconciliation risk.

## 10. Pattern revision and backward invalidation

A validated learning only flows earlier -> later. A shared pattern is different: it may evolve and affect already-completed signatories.

When concrete implementation evidence requires a pattern change:

```bash
python <skill-dir>/scripts/patternctl.py update \
  --plan .ai-work/<plan-id> \
  --pattern PAT001 \
  --contract-file /tmp/pattern-v2.json \
  --reason "Concrete evidence" \
  --changed-by-task 006
```

`patternctl` increments the revision, preserves history, and resets only completed signatories that adopted an older revision. Pending signatories will consume the newest revision later. A revision is rejected while another affected signatory is actively executing stale instructions.

This is a dependency invalidation event, not a reason to replan the whole project. Re-enter full planning only if the new evidence changes requirement interpretation, TODO boundaries, dependencies, or architecture outside the pattern contract.

After a completed TODO passes external validation:

```bash
python <skill-dir>/scripts/patternctl.py adopt \
  --plan .ai-work/<plan-id> --task 006
```

Final completion requires `patternctl validate` to pass; no completed signatory may remain on a stale revision.

## 11. Resume across quota/session/provider failure

Lifecycle state exists so work survives lost credits, process termination, host restart, or provider switching.

On resume:

- discover the unique active/actionable plan;
- acquire/recover the runner lease;
- return only orphaned `in_progress` task/subtask state to runnable state;
- preserve completed tasks/subtasks, pattern revisions/signatures, prepared-package references, and partial repository changes;
- do not count quota/rate/capacity interruption as technical failure;
- dispatch a fresh compatible worker from persisted task/context/pattern state, not prior chat history.

Strict external execution uses `run_concise.py` / `pae resume` for ordinary task state. Hosts integrating patterns must perform the pattern assignment/validation hooks described above before dispatch and adoption after completion.

## 12. Replan only when evidence invalidates the plan

If execution reveals a material unknown, contradictory contract, new version/security/migration risk, invalid dependency, wrong context boundary, or pattern change that alters task boundaries, stop downstream execution and re-enter necessary study/planning gates.

Do not replan merely because a worker used many tokens, a provider hit quota, or a pattern revision affects only its declared signatories.

## 13. Finish and clean planning state

Before final handoff:

1. require every TODO and deterministic final validation to pass;
2. if patterns exist, require `patternctl validate` so all completed signatories adopted current revisions;
3. build final-summary input from compact authoritative task state, validations, pattern revision summary, and bounded repository-change evidence — never concatenate raw worker reports;
4. generate the user-facing handoff with an economy route when available;
5. mark summary generated and deactivate lifecycle state;
6. run guarded plan cleanup.

Preserve implementation changes, tests, generated product artifacts, commits, and unrelated repository content. Retain plan state when completion, validation, pattern adoption, or summary generation fails so diagnosis/resume remains possible.
