---
name: plan-and-execute
description: Orchestrate long-horizon software changes only when durable resumability, independently verifiable workstreams, broad study, or isolation justify it. Do not use for routine bug fixes or cohesive small/medium changes one agent can implement safely; prefer direct execution and promote later when scope grows. For planned work, stage oversized specs before final planning, with adaptive model routing and versioned shared-pattern contracts.
---

# Plan and Execute

Treat context as a budget, model capability as a second, and durable progress before quota exhaustion as a third. Apply **DIRECT vs ORCHESTRATED** first; only orchestrated work then chooses FINAL_PLAN vs PRIMARY_PLAN. Load only the selected path's references.

## 1. Lifecycle first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Decide DIRECT vs ORCHESTRATED

Prefer **DIRECT** unless durable orchestration pays for itself. Strong ORCHESTRATED signals: independent workstreams, broad repository/external study, migration/security/data-integrity/cross-module coordination, meaningful interruption/quota risk, or valuable worker-context isolation. File count alone is weak evidence.

### DIRECT EXIT

If orchestration is not justified: create no `.ai-work`, study, requirements inventory, plan, TODO, task, primary-plan, pattern, worker, or lifecycle state; do not read orchestration/primary-plan/schema references; implement/validate directly with economical model routing.

**DIRECT exits the harness, not adaptive model routing.** A small task with no tests can deserve a stronger model when silent failure is costly.

When uncertain, prefer DIRECT. Read [references/ROUTING.md](references/ROUTING.md) only for an ambiguous boundary.

## 3. ORCHESTRATED input gate — FINAL_PLAN vs PRIMARY_PLAN

Measure request-input pressure **before** loading a large request into an expensive planning model:

```bash
python <skill-dir>/scripts/preplanctl.py assess --file <request-file>
```

For Drive/Docs/Office/PDF sources, obtain readable/local text with host tools first; never paste the document through chat.

- **FINAL_PLAN** (manageable): [references/ORCHESTRATION.md](references/ORCHESTRATION.md). Do not read `PRIMARY_PLANNING.md`. For a prepared package, read the small [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md).
- **PRIMARY_PLAN** (oversized/credit-expensive): [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md); `preplanctl.py prepare --repo-root . --file <request-file>` creates immutable fragments and a resumable checklist whose product (`FINAL_PLAN_INPUT.md`) enters normal FINAL_PLAN.

Economic defaults: FINAL_PLAN below ~12k estimated source tokens without breadth trigger; PRIMARY_PLAN at 24k+; between them, 30+ headings at 8k+ tokens trigger PRIMARY_PLAN.

## 4. Always-on model economy

1. Deterministic tools for search, hashing, splitting, indexing, transforms, builds/tests/lint.
2. Cheapest credible read-only worker for broad disposable exploration; persist only compact evidence. No worker for one grep or two obvious reads; at most two explorers.
3. Route each leaf by its signals, not by parent size or root-chat model. Floor per leaf (`python <skill-dir>/scripts/routingctl.py route --signals a,b`):

| Leaf signal | Floor |
|---|---|
| `deterministic_lookup` | tool, no model |
| `exploration`, `mechanical_edit` | economy low |
| `bounded_implementation` | standard medium |
| `subtle_debugging` | strong medium |
| `architecture_decision`, `cross_cutting_risk`, `silent_failure_costly` | strong high |
| `frontier_long_horizon` / `repeated_strong_failure` | max high / xhigh |

`weak_validation`: +1 tier, effort high. `strong_validation`: strong may start medium. `implementation`: never `low` unless mechanical and deterministically checked.

4. **Never switch the root session's model or effort** (it invalidates the prompt cache). Elevate by delegation: if the root tier is below a leaf's floor, delegate that leaf — including planning stages — to a fresh worker at the floor with a minimal prompt, and consume its compact result. A small root model is a delegator, not a ceiling.
5. Cheap-first when validation catches failure; start stronger when silent failure is costly or weakly verifiable.
6. Escalate only from classified failure evidence (`failure_class`); stop when acceptance plus independent validation pass.

Planning has independent routing: [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md) only when assigning planning-stage routes. Implementation uses [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) plus exactly one active provider map. Do not preload both provider guides.

`primary route != final-planning route != implementation route`

## 5. Promote late

When substantial DIRECT work grows into independent remaining outcomes, broad research/migration work, or meaningful interruption/isolation risk, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work and plan only **remaining outcomes**; then run the input gate on remaining authoritative material.

## 6. Final-plan invariants

- `manifest.json` is authoritative; `TODO.md` is the terse task index.
- Every TODO has bounded scope, resumable subtasks, deterministic validation, `provider`, `model_tier`, and `reasoning_effort`; a `high` TODO may add `design_route` for a strong design pass before cheaper implementation.
- Planning stages choose capability deliberately instead of inheriting the root model; hard decisions may be resolved first by strong workers (`hard_decisions`).
- quota/rate-limit exhaustion and host interruption are not technical failures; another compatible provider can resume without the previous chat transcript;
- implementation changes, tests, product artifacts, and commits survive cleanup.

For a normative contract shared by 2+ TODOs that may evolve, use [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md): a versioned pattern with signatories; a revision reopens only completed signatories on an older revision.

## Reference map — on demand

Files not linked above: artifacts [ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md), study [ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md), final planning [PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md), execution context [EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md), plan schema [PLAN_SPEC.md](references/PLAN_SPEC.md), execution [WORKFLOW.md](references/WORKFLOW.md).
