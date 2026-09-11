---
name: plan-and-execute
description: Orchestrate long-horizon software changes only when durable resumability, independently verifiable workstreams, broad study, or isolation justify it. Do not use for routine bug fixes or cohesive small/medium changes one agent can implement safely; prefer direct execution and promote later when scope grows. For planned work, stage oversized specs before final planning, with adaptive model routing and versioned shared-pattern contracts.
---

# Plan and Execute

Treat context as a budget, model capability as another budget, and durable progress before quota exhaustion as a third. Apply **DIRECT vs ORCHESTRATED** first; only orchestrated work then chooses FINAL_PLAN vs PRIMARY_PLAN. Load only the selected path's references.

## 1. Lifecycle first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Decide DIRECT vs ORCHESTRATED

Prefer **DIRECT** unless durable orchestration pays for itself. Strong ORCHESTRATED signals: independent workstreams, broad repository/external study, migration/security/data-integrity/cross-module coordination, meaningful interruption/quota risk, or valuable worker-context isolation.

File count alone is weak evidence; cohesive related-file work may stay direct.

### DIRECT EXIT

If orchestration is not justified:

- create no `.ai-work`, study, requirements inventory, plan, TODO, task, primary-plan, pattern, worker, or lifecycle state;
- do not read orchestration/primary-plan/schema references;
- implement/validate directly and keep economical model routing.

**DIRECT exits the harness, not adaptive model routing.** A small task with no tests can deserve a stronger model when silent failure is costly.

When uncertain, prefer DIRECT. Read [references/ROUTING.md](references/ROUTING.md) only for an ambiguous boundary.

## 3. ORCHESTRATED input gate — FINAL_PLAN vs PRIMARY_PLAN

Measure request-input pressure **before** loading a large request into an expensive planning model.

For a local/request file:

```bash
python <skill-dir>/scripts/preplanctl.py assess --file <request-file>
```

For Drive/Docs/Office/PDF/external documents, use authenticated host/file tools to obtain readable/local source first; prefer deterministic extraction over pasting the whole document through chat.

### FINAL_PLAN — manageable request

Use [references/ORCHESTRATION.md](references/ORCHESTRATION.md). **Do not read `PRIMARY_PLANNING.md`.** If input is a prepared package, read the small [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md) boundary.

### PRIMARY_PLAN — oversized/credit-expensive request

Use [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md). **Do not preload full ordinary orchestration while creating the primary plan.**

```bash
python <skill-dir>/scripts/preplanctl.py prepare --repo-root . --file <request-file>
```

Economic defaults, not context-window claims: FINAL_PLAN below ~12k estimated source tokens without breadth trigger; PRIMARY_PLAN at 24k+; between them, 30+ detected headings at 8k+ tokens can trigger PRIMARY_PLAN. Tune for provider/project economics.

PRIMARY_PLAN deterministically creates immutable indexed fragments, then a resumable checklist for bounded digests, cross-fragment synthesis, fresh coverage review, and compact `FINAL_PLAN_INPUT.md`. That product enters normal FINAL_PLAN, which recalculates implementation TODOs/routes from scratch.

## 4. Always-on model economy

1. Use deterministic tools for mechanical search, hashing, splitting, indexing, transforms, builds/tests/lint.
2. Delegate broad disposable exploration to the cheapest credible read-only worker; persist only compact evidence.
3. Avoid workers for obvious reads and swarms for sequential work.
4. Route by leaf semantic difficulty, verifiability, and blast radius — not parent size or root-chat model.
5. Cheap-first when validation catches failure; start stronger when silent failure is costly/weakly verifiable.
6. Escalate from evidence; stop when acceptance plus independent validation pass.

Planning has independent routing. Read [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md) only when assigning planning-stage routes. Implementation uses [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) plus only the active provider map. Do not preload both provider guides; read exactly one active provider mapping.

`primary route != final-planning route != implementation route`

## 5. Promote late

When substantial DIRECT work grows into independent remaining outcomes, broad research/migration work, or meaningful interruption/isolation risk, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work and plan only **remaining outcomes**; then run the input gate on remaining authoritative material.

## 6. Final-plan invariants

- `manifest.json` is authoritative; `TODO.md` is the terse task index.
- Every TODO has bounded scope, resumable subtasks, deterministic validation, `provider`, `model_tier`, and `reasoning_effort`.
- Planning stages choose capability deliberately instead of inheriting the root model.
- quota/rate-limit exhaustion and host interruption are not technical failures.
- Another compatible provider can resume without the previous chat transcript.
- implementation changes, tests, product artifacts, and commits survive cleanup.

For a normative contract shared by 2+ TODOs that may evolve, use [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md): create a versioned pattern with signatories. A revision reopens only completed signatories that adopted an older revision. Do not load it when no such contract exists.

## Reference map — on demand

- FINAL_PLAN: [references/ORCHESTRATION.md](references/ORCHESTRATION.md)
- PRIMARY_PLAN: [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md)
- Prepared package: [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md)
- Planning routing: [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md)
- Shared patterns: [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md)
- Promotion: [references/PROMOTION.md](references/PROMOTION.md)
- Artifact writing: [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md)
- Adaptive study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Final planning: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution: [references/WORKFLOW.md](references/WORKFLOW.md)
