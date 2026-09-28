---
name: plan-and-execute
description: Orchestrate long-horizon software changes only when durable resumability, independently verifiable workstreams, broad study, or isolation justify it. Do not use for routine bug fixes or cohesive small/medium changes one agent can implement safely; prefer direct execution and promote later when scope grows. For planned work, stage oversized specs before final planning, with adaptive model routing and versioned shared-pattern contracts.
---

# Plan and Execute

Treat context as a budget; preserve capability and durable progress. Choose **DIRECT vs ORCHESTRATED**, then FINAL_PLAN vs PRIMARY_PLAN for orchestrated work. Load only selected references.

## 1. Lifecycle and configuration

`current`/`status`, `resume`/`continue`, `cancel`, and `reset`: [LIFECYCLE.md](references/LIFECYCLE.md). Exact `configure`: run `scripts/configure.py` or `pae configure`; see [ROUTING_CONFIG.md](references/ROUTING_CONFIG.md). Configuration does not create a plan. Ask one numbered question at a time; never assume installation proves authentication. Do not run configuration for ordinary implementation requests.

## 2. Decide DIRECT vs ORCHESTRATED

Prefer DIRECT unless durable orchestration pays for itself. Strong signals: independent workstreams, broad repository/external study, migration/security/data-integrity coordination, interruption/quota risk, or valuable worker-context isolation. File count alone is weak evidence.

### DIRECT EXIT

Without those benefits, create no `.ai-work`, study, requirements inventory, plan, TODO, worker, or lifecycle state. Do not load orchestration/schema references; implement and validate directly.

**DIRECT exits the harness, not adaptive model routing.** A small task with no tests can deserve a stronger model when silent failure is costly.

When uncertain, prefer DIRECT. Read [ROUTING.md](references/ROUTING.md) only for an ambiguous boundary.

## 3. ORCHESTRATED input gate

Measure request pressure before loading a large source into an expensive model:

```bash
python <skill-dir>/scripts/preplanctl.py assess --file <request-file>
```

Extract readable text from Drive/Office/PDF with host tools first, without pasting whole documents through chat.

- FINAL_PLAN: [ORCHESTRATION.md](references/ORCHESTRATION.md). Do not load PRIMARY_PLANNING. Prepared packages also use [PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md).
- PRIMARY_PLAN: [PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md). `preplanctl.py prepare --repo-root . --file <request-file>` creates immutable fragments and a resumable checklist; its `FINAL_PLAN_INPUT.md` enters FINAL_PLAN.

Defaults: FINAL_PLAN below ~12k estimated source tokens without breadth; PRIMARY_PLAN at 24k+, or 30+ headings at 8k+ tokens between the thresholds.

Before planning, reconcile `.ai-work/SERVICE_MAP.md`: freshness, changed inputs, preflights, validation resources and plan audit. Validators use its resource watcher; long tests also monitor progress. Follow [TEST_RESOURCE_MONITORING.md](references/TEST_RESOURCE_MONITORING.md). Cleanup preserves the shared map; DIRECT creates none.

## 4. Always-on model economy

Use tools for lookup, transforms, builds/tests/lint. Disposable exploration uses at most two credible cheap read-only workers and persists compact evidence. One grep needs no agent.

Route each leaf by its own signals, not parent size or root model. Compute its floor with `python <skill-dir>/scripts/routingctl.py route --signals a,b`:

| Leaf signal | Floor |
|---|---|
| `deterministic_lookup` | tool, no model |
| `exploration`, `mechanical_edit` | economy low |
| `bounded_implementation` | standard medium |
| `subtle_debugging` | strong medium |
| `architecture_decision`, `cross_cutting_risk`, `silent_failure_costly` | strong high |
| `frontier_long_horizon` / `repeated_strong_failure` | max high / xhigh |

`weak_validation`: +1 tier, high effort. With `strong_validation`, strong may start medium. Implementation never uses low effort unless mechanical and deterministically checked.

Keep the root route stable; delegate leaves above its capability, including planning, to fresh qualified workers and consume compact results. Cache effects depend on provider/model settings, not a universal effort rule. Start stronger when silent failure is costly; otherwise use cheap-first with strong validation. Escalate only from classified failure evidence; stop after acceptance plus independent validation pass.

Planning routes: [PLANNING_ROUTING.md](references/PLANNING_ROUTING.md). Implementation: [MODEL_ROUTING.md](references/MODEL_ROUTING.md) plus only the active provider guide. Do not preload both provider guides.

Tier priority/fallback: [ROUTING_CONFIG.md](references/ROUTING_CONFIG.md). Optional bounded advice: [ASSISTANTS.md](references/ASSISTANTS.md), loaded only for setup, eligible failure or maintenance. Unsupported read-only profiles skip.

## 5. Promote late

When DIRECT work grows into independent remaining outcomes, broad study or meaningful interruption risk, use [PROMOTION.md](references/PROMOTION.md). Preserve completed work and plan only **remaining outcomes**; assess the remaining authoritative material.

## 6. Final-plan invariants

- `manifest.json` is authoritative; `TODO.md` is the terse index. Each TODO has bounded scope, resumable subtasks, validation, `provider`, `model_tier`, and `reasoning_effort`; a high leaf may add `design_route`.
- Planning selects capability independently; strong workers may resolve `hard_decisions` first.
- quota/rate-limit exhaustion and host interruption are not technical failures. Another compatible provider resumes without the previous chat transcript. Exhausted availability chains pause without changing the semantic ladder.
- implementation changes, tests, artifacts and commits survive cleanup. Retain the plan when explicitly requested or whenever completion/validation fails.
- Every automated validation references the fresh service map and runs through its watcher. An assistant cannot classify authoritatively, edit, validate or complete a task.

Shared normative contracts used by 2+ TODOs: [SHARED_PATTERNS.md](references/SHARED_PATTERNS.md). Revisions reopen only completed signatories on an older version.

## On-demand references

Artifacts: [ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md). Study: [ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md). Planning: [PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md). Context: [EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md). Schema: [PLAN_SPEC.md](references/PLAN_SPEC.md). Execution: [WORKFLOW.md](references/WORKFLOW.md). Self-maintenance final review: [SKILL_MAINTENANCE_REVIEW.md](references/SKILL_MAINTENANCE_REVIEW.md). Research stays in repository `docs/`, never routine worker context.
