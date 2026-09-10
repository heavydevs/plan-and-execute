---
name: plan-and-execute
description: Orchestrate long-horizon software changes that need durable resumability, independent workstreams, broad repository/external research, repo-wide migration/compatibility work, or isolated delegated execution. Also use when explicitly invoked or for lifecycle status/resume/cancel/reset. Do not use for routine bug fixes, bounded features/refactors/tests, or cohesive small/medium changes one agent can implement and validate in current context. When uncertain, prefer direct execution and promote later if scope, research, resumability, workstreams, or context pressure materially grow.
---

# Plan and Execute

Treat context as a budget and model capability as another budget. Route **execution shape** (DIRECT vs ORCHESTRATED) and **model spend**. Pay for stronger planning/models only when they improve verified quality.

## 1. Route lifecycle commands first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Decide DIRECT vs ORCHESTRATED before creating state

Explicit `plan-and-execute`, an existing requirements file passed for orchestration, or a lifecycle command selects **ORCHESTRATED**.

For implicit invocation, select ORCHESTRATED only when at least one strong signal exists:

- two or more independently verifiable workstreams whose retained reasoning would not materially help each other;
- broad repository study or substantial external research is needed before implementation is safe;
- migration, compatibility, security, data-integrity, concurrency, or cross-module work needs durable coordination;
- work likely crosses sessions/providers/quota windows/context compaction;
- isolated workers materially reduce unrelated context or improve validation.

File count alone is not a signal. Cohesive related-file work may stay direct.

### DIRECT EXIT

If no strong signal applies and invocation was implicit:

- create no `.ai-work`, study, requirements inventory, plan, TODO, task file, worker, or lifecycle state;
- do not read orchestration references;
- implement/validate directly;
- keep model economy: DIRECT exits the harness, not adaptive model routing.

When uncertain, prefer DIRECT. Read [references/ROUTING.md](references/ROUTING.md) only for a genuinely ambiguous boundary.

## 3. Always-on model economy

These rules apply in DIRECT and ORCHESTRATED modes:

1. Use deterministic tools for one-off lookup, build/test/lint, and mechanical operations.
2. Delegate context-heavy repository/log/doc exploration to the cheapest credible read-only subagent; request a compact evidence map.
3. Do not spawn a subagent for one or two obvious reads. Prefer at most two concurrent explorers unless branches are independent.
4. Route by semantic difficulty, verifiability, and blast radius, not parent-request size. A small task with no tests can deserve a stronger model; a large mechanical search can deserve the cheapest one.
5. Cheap-first is appropriate when deterministic validation catches failure; start stronger for high-blast-radius, weakly verifiable decisions.
6. Escalate from concrete failure evidence; stop when acceptance criteria plus available independent validation pass.

Read [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) when choosing a route. ORCHESTRATED plans persist only provider-neutral `F1`–`F4` and `L1`–`L5`. At planning time read [references/MODEL_MATRIX.md](references/MODEL_MATRIX.md), research current providers/models, and create plan-local `MODEL_MATRIX.json`/`MODEL_MATRIX.md`. Concrete model names are execution data, not durable TODO identity.

## 4. Promote late when direct work grows

Promote DIRECT only when substantial remaining work splits into independent outcomes, broad research/migration analysis becomes necessary, interruption/quota risk makes durable resume valuable, or high context pressure accompanies non-cohesive work. Do not promote nearly finished cohesive work only because context is high.

Read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work, validations, decisions, relevant code, blockers/risks, and **remaining outcomes** with `promotectl.py`; create TODOs only for remaining work.

## 5. Full harness after ORCHESTRATED is selected

Read [references/ORCHESTRATION.md](references/ORCHESTRATION.md). It owns adaptive study, traceable requirements, TODO decomposition, execution context, portable routing, resumable subtasks, validated learnings, deterministic validation, lifecycle recovery, handoff, and cleanup.

Non-negotiable invariants:

- `manifest.json` is authoritative; `TODO.md` is the terse status index;
- every executable TODO is bounded, independently verifiable, and resumable;
- every new TODO keeps `provider: auto`, `model_tier: f1|f2|f3|f4`, and `reasoning_effort: l1|l2|l3|l4|l5`;
- every ORCHESTRATED plan has a current plan-local model matrix for providers that may execute/resume it;
- actual provider/model/effort is selected at dispatch and recorded as provenance, not plan semantics;
- quota/rate-limit exhaustion and host interruption are not technical failures;
- another compatible provider can resume from persisted state without the previous chat transcript or a plan rewrite;
- implementation changes, tests, product artifacts, and commits survive cleanup.

Legacy schema-v1–v4 plans may still use `provider`, `model_tier`, and `reasoning_effort` with old tier/effort values. New plans persist only F/L routes.

## Reference map

- [Artifact writing](references/ARTIFACT_WRITING.md), [intake](references/INTAKE.md), [adaptive study](references/ADAPTIVE_STUDY.md)
- [Planning](references/PLANNING_PROTOCOL.md), [execution context](references/EXECUTION_CONTEXT.md), [plan schema](references/PLAN_SPEC.md), [workflow](references/WORKFLOW.md)
- [Model routing](references/MODEL_ROUTING.md), [dynamic matrix](references/MODEL_MATRIX.md), [token economics](references/TOKEN_EFFICIENCY.md)
- [Codex notes](references/MODEL_ROUTING_CODEX.md), [Claude notes](references/MODEL_ROUTING_CLAUDE.md)
