---
name: plan-and-execute
description: Orchestrate long-horizon software changes that benefit from durable resumability, independently verifiable workstreams, broad repository/external research, repo-wide migration/compatibility work, or isolated delegated execution. Also use when explicitly invoked or for lifecycle status/resume/cancel/reset. Do not use for routine bug fixes, bounded features/refactors/tests, or cohesive small/medium changes one agent can implement and validate in current context. When uncertain, prefer direct execution and promote later if scope, research, resumability, workstreams, or context pressure materially grow.
---

# Plan and Execute

Treat context as a budget and model capability as another budget. Route **DIRECT vs ORCHESTRATED** first, then spend model capability only where it improves verified quality.

## 1. Route lifecycle commands first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Decide DIRECT vs ORCHESTRATED before creating state

Explicit `plan-and-execute`, a requirements file passed for orchestration, or a lifecycle command selects **ORCHESTRATED**.

For implicit invocation, use ORCHESTRATED only when there is a strong reason: independent verifiable workstreams, broad study/research, repo-wide migration/security/data/concurrency work, durable resume value across providers/quota/context windows, or isolation that materially reduces unrelated context. File count alone is not enough.

### DIRECT EXIT

If no strong signal applies:

- create no `.ai-work`, plan, TODO, task, worker, or lifecycle state;
- implement and validate in the current useful context;
- keep economical model routing active.

When uncertain, prefer DIRECT. Read [references/ROUTING.md](references/ROUTING.md) only for an ambiguous boundary.

## 3. Model economy applies in both modes

Use deterministic tools for mechanical lookup/checks. Delegate broad disposable exploration only when a cheap read-only worker reduces context. Route implementation by semantic difficulty, verifiability, and blast radius, not parent-request size. Cheap-first is appropriate when deterministic validation catches failure; start stronger when silent failure is costly. Escalate only from evidence and stop when acceptance plus independent validation pass.

For generic capability choice read [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md). ORCHESTRATED planning also reads [references/PORTABLE_MODEL_ROUTING.md](references/PORTABLE_MODEL_ROUTING.md). Provider guidance is loaded only for the provider being resolved: Codex, Claude, Gemini, Qwen, or Muse.

## 4. Promote late

If direct work grows into independent outcomes, broad research/migration analysis, durable resume needs, or substantial non-cohesive context pressure, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work and plan only **remaining outcomes**; never recreate completed work as retroactive TODOs.

## 5. ORCHESTRATED contract

Read [references/ORCHESTRATION.md](references/ORCHESTRATION.md). It owns study, requirements, decomposition, execution context, resumable subtasks, F/L routing, validation, recovery, summary, and cleanup.

Non-negotiable invariants:

- `manifest.json` is authoritative and `TODO.md` is the terse status index;
- every TODO has one bounded outcome, resumable subtasks, acceptance criteria, and deterministic validation;
- every new TODO declares only `model_family` (`F1`-`F4`) and `model_level` (`L1`-`L5`), never a concrete provider/model or vendor-specific effort;
- model compatibility is cached independently per provider under `~/.plan-and-execute/cache/model-compatibility`; check that provider's cache before any CLI/documentation discovery;
- a fresh provider cache is reused for the rest of the local calendar day; only a missing/stale/invalid cache triggers live discovery for that provider;
- new plan snapshots write `MODEL_COMPATIBILITY.json` plus `MODEL_COMPATIBILITY.md` for the provider actually being used, not all providers preemptively;
- portable TODOs reference the compatibility artifact; switching provider resolves the same F/L without re-planning and may refresh only that provider's cache/snapshot;
- quota/rate-limit exhaustion and host interruption do not raise F/L by themselves;
- implementation changes, tests, product artifacts, and commits survive cleanup.

Legacy plans may preserve `provider`, `model_tier`, and `reasoning_effort` for backwards-compatible resume; new plans must use F/L.

## References

Core orchestration: [references/ORCHESTRATION.md](references/ORCHESTRATION.md), [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md), [references/PLAN_SPEC.md](references/PLAN_SPEC.md), [references/WORKFLOW.md](references/WORKFLOW.md), [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md), [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md), [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md), [references/INTAKE.md](references/INTAKE.md).

Routing: [references/PORTABLE_MODEL_ROUTING.md](references/PORTABLE_MODEL_ROUTING.md), [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md), [references/MODEL_ROUTING_CODEX.md](references/MODEL_ROUTING_CODEX.md), [references/MODEL_ROUTING_CLAUDE.md](references/MODEL_ROUTING_CLAUDE.md), [references/MODEL_ROUTING_GEMINI.md](references/MODEL_ROUTING_GEMINI.md), [references/MODEL_ROUTING_QWEN.md](references/MODEL_ROUTING_QWEN.md), [references/MODEL_ROUTING_MUSE.md](references/MODEL_ROUTING_MUSE.md), [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md).
