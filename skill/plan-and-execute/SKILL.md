---
name: plan-and-execute
description: Orchestrate long-horizon software changes with selective planning, staged preprocessing for oversized specifications, resumable isolated TODOs, adaptive model routing, and versioned shared-pattern contracts. Do not use for routine bug fixes, bounded cohesive features/refactors/tests, or small/medium work one agent can implement and validate safely in current context. Prefer direct execution and promote only when scope, research, resumability, isolation, or request-input pressure materially justify it.
---

# Plan and Execute

Treat context as a budget, model capability as another budget, and durable progress before quota exhaustion as a third. Apply the **DIRECT vs ORCHESTRATED** gate first; only orchestrated work then chooses FINAL_PLAN vs PRIMARY_PLAN. Load only the selected path's references.

## 1. Lifecycle first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Decide DIRECT vs ORCHESTRATED

Prefer **DIRECT** unless durable orchestration clearly pays for itself. Strong ORCHESTRATED signals include independent workstreams, broad repository/external study, migration/security/data-integrity/cross-module coordination, meaningful interruption/quota risk, or valuable worker-context isolation.

File count alone is weak evidence. Cohesive related-file work may stay direct.

### DIRECT EXIT

If orchestration is not justified:

- create no `.ai-work`, study, requirements inventory, plan, TODO, task, primary-plan, pattern, worker, or lifecycle state;
- do not read orchestration/primary-plan/schema references;
- implement and validate directly;
- keep economical model routing.

When uncertain, prefer DIRECT. Read [references/ROUTING.md](references/ROUTING.md) only for an ambiguous boundary.

## 3. For ORCHESTRATED work, route FINAL_PLAN vs PRIMARY_PLAN

Measure request-input pressure **before** loading a large request into an expensive planning model.

For a local/request file:

```bash
python <skill-dir>/scripts/preplanctl.py assess --file <request-file>
```

For Drive/Docs/Office/PDF or another external document, use authenticated host/file tools to obtain readable/local source first; prefer deterministic extraction rather than pasting the entire document through chat.

### FINAL_PLAN — manageable request

Use the ordinary workflow in [references/ORCHESTRATION.md](references/ORCHESTRATION.md). **Do not read `PRIMARY_PLANNING.md`.**

If FINAL_PLAN receives a prepared package created earlier, read only the small [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md) boundary first.

### PRIMARY_PLAN — oversized/credit-expensive request

Use [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md). **Do not preload full ordinary orchestration while creating the primary plan.**

```bash
python <skill-dir>/scripts/preplanctl.py prepare --repo-root . --file <request-file>
```

Defaults are economic guardrails, not context-window claims: direct final planning below roughly 12k estimated source tokens without a breadth trigger; PRIMARY_PLAN at 24k+; between them, default structural breadth (30+ detected headings at 8k+ tokens) can trigger PRIMARY_PLAN. Provider/project economics may tune these thresholds.

PRIMARY_PLAN deterministically creates immutable indexed fragments, then a resumable checklist for bounded source digests, cross-fragment synthesis, fresh coverage review, and a compact `FINAL_PLAN_INPUT.md`. Its product then enters normal FINAL_PLAN. Final planning recalculates implementation TODOs/routes from scratch.

## 4. Always-on model economy

1. Use deterministic tools for mechanical search, hashing, splitting, indexing, transforms, builds/tests/lint.
2. Delegate broad disposable exploration to the cheapest credible read-only worker and persist only a compact evidence map.
3. Avoid workers for one/two obvious reads and avoid swarms for sequential work.
4. Route by leaf semantic difficulty, verifiability, and blast radius — not parent size or root-chat model.
5. Cheap-first when deterministic validation catches failure; start stronger when silent failure is costly/weakly verifiable.
6. Escalate from concrete failure evidence; stop when acceptance plus independent validation pass.

Planning has its own adaptive routing. Read [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md) only when assigning planning-stage routes. Implementation uses [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) plus only the active provider map.

`primary route != final-planning route != implementation route`

## 5. Promote late

When substantial DIRECT work grows into independent remaining outcomes, broad research/migration work, or meaningful interruption/context-isolation risk, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work and plan only **remaining outcomes**. Then run the FINAL_PLAN vs PRIMARY_PLAN input gate for remaining authoritative request material.

## 6. Final-plan invariants

- `manifest.json` is authoritative; `TODO.md` is the terse task index.
- Every TODO has bounded scope, resumable subtasks, deterministic validation, `provider`, `model_tier`, and `reasoning_effort`.
- Planning stages choose capability deliberately rather than inheriting the root model.
- quota/rate-limit exhaustion and host interruption are not technical failures.
- Another compatible provider can resume without the previous chat transcript.
- implementation changes, tests, product artifacts, and commits survive cleanup.

When two or more TODOs share a **normative contract that may evolve**, use [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md): create a versioned pattern with explicit signatories. A pattern revision reopens only completed signatories that adopted an older revision; unrelated tasks remain complete. Do not load this reference for plans with no such contract.

## Reference map — load on demand

- FINAL_PLAN: [references/ORCHESTRATION.md](references/ORCHESTRATION.md)
- PRIMARY_PLAN: [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md)
- Prepared-package boundary: [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md)
- Planning routing: [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md)
- Shared evolving patterns: [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md)
- Direct routing: [references/ROUTING.md](references/ROUTING.md)
- Promotion: [references/PROMOTION.md](references/PROMOTION.md)
- Artifact writing: [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md)
- Adaptive study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Final planning: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Final plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Token economics: [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md)
