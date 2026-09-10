---
name: plan-and-execute
description: Orchestrate long-horizon software changes that benefit from durable resumability, independently verifiable workstreams, broad repository/external research, repo-wide migration/compatibility work, or isolated delegated execution. Also use when explicitly invoked or for lifecycle status/resume/cancel/reset. Do not use for routine bug fixes, bounded features/refactors/tests, or cohesive small/medium changes one agent can implement and validate in current context. When uncertain, prefer direct execution and promote later if scope, research, resumability, workstreams, or context pressure materially grow.
---

# Plan and Execute

Treat context as a budget and model capability as another budget. Route both **execution shape** (DIRECT vs ORCHESTRATED) and **model spend**. Pay for planning and stronger models only when they materially improve verified quality.

## 1. Route lifecycle commands first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Decide DIRECT vs ORCHESTRATED before creating state

Explicit `plan-and-execute`, an existing requirements file passed for orchestration, or a lifecycle command selects **ORCHESTRATED**.

For implicit invocation, select **ORCHESTRATED** only when at least one strong signal is present:

- two or more independently verifiable workstreams whose retained reasoning would not materially help each other;
- broad repository study or substantial external research is needed before implementation is safe;
- repo-wide migration, compatibility, security, data-integrity, concurrency, or cross-module work needs durable coordination;
- likely work across sessions/providers/quota windows/context compaction makes durable resume valuable;
- isolated workers materially reduce unrelated context or improve independent validation.

File count alone is not a signal. Cohesive related-file work may stay direct.

### DIRECT EXIT

If no strong signal applies and the skill was selected implicitly:

- create no `.ai-work`, study, requirements inventory, plan, TODO, task file, worker, or lifecycle state;
- do not read orchestration references;
- implement/validate directly in current useful context;
- **continue applying model economy**; DIRECT exits the harness, not adaptive model routing.

When uncertain, prefer DIRECT. An unnecessary plan has already spent tokens/time. Read [references/ROUTING.md](references/ROUTING.md) only for a genuinely ambiguous boundary.

## 3. Always-on model economy — DIRECT and ORCHESTRATED

These rules apply even when no plan is created:

1. Use deterministic tools directly for one-off filename/symbol lookup, build/test/lint, or other mechanical operations.
2. If repository/log/doc exploration would load substantial disposable context, delegate it to the cheapest credible **read-only** subagent and request only a compact evidence map.
3. Do not spawn a subagent for one or two obvious reads or a swarm for sequential work. Prefer at most two concurrent explorers unless branches are genuinely independent.
4. Route implementation by semantic difficulty, verifiability, and blast radius — not by parent-request size. A small task with no tests can deserve a stronger model; a large but mechanical search can deserve the cheapest one.
5. Cheap-first is appropriate when deterministic validation catches failure. Start stronger for high-blast-radius, weakly verifiable decisions.
6. Escalate from concrete failure evidence and stop once acceptance criteria plus available independent validation pass. The skill chooses the route dynamically; there is no user model/effort ceiling.

For generic capability choice read [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md). In ORCHESTRATED planning, also read [references/PORTABLE_MODEL_ROUTING.md](references/PORTABLE_MODEL_ROUTING.md) and build the current compatibility table. Provider files are loaded only when resolving that provider: Codex, Claude Code, Gemini CLI, Qwen Code, or Muse Code.

## 4. Promote late when direct work grows

Promote a DIRECT request when substantial work remains and scope splits into independent outcomes, broad research/migration analysis becomes necessary, interruption/quota risk makes durable resume valuable, or high context pressure accompanies substantial non-cohesive work.

Context pressure is secondary; do not promote a nearly finished cohesive task merely because context is high.

On promotion, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work, validations, active decisions, relevant code, blockers/risks, and **remaining outcomes** with `promotectl.py`; create TODOs only for remaining work.

## 5. Full harness after ORCHESTRATED is selected

Read [references/ORCHESTRATION.md](references/ORCHESTRATION.md). It owns adaptive study, traceable requirements, TODO decomposition, task files, portable F/L model routing, resumable subtasks, validated learnings, deterministic validation, lifecycle recovery, final handoff, and guarded cleanup.

Non-negotiable invariants:

- `manifest.json` is authoritative; `TODO.md` is the terse status index;
- every executable TODO has a bounded definition and resumable subtasks;
- every new TODO declares only `model_family` (`F1`-`F4`) and `model_level` (`L1`-`L5`), never a concrete provider/model or vendor-specific effort name;
- during planning, dynamically discover current Codex/Claude/Gemini/Qwen/Muse bindings and write `MODEL_COMPATIBILITY.json` plus rendered `MODEL_COMPATIBILITY.md`;
- every portable TODO and `PLAN.md` explicitly reference the compatibility artifact; changing provider resolves the same F/L and does not require re-planning;
- refresh compatibility when changing provider or when a recorded model/effort is unavailable or uncertain;
- quota/rate-limit exhaustion and host interruption are not technical failures and do not raise F/L by themselves;
- implementation changes, tests, product artifacts, and commits survive cleanup.

Legacy plans that already contain `provider`/`model_tier`/`reasoning_effort` remain resumable for backwards compatibility, but new plans must use F/L.

## Reference map

- Orchestration: [references/ORCHESTRATION.md](references/ORCHESTRATION.md)
- Artifact writing: [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md)
- Intake: [references/INTAKE.md](references/INTAKE.md)
- Direct routing: [references/ROUTING.md](references/ROUTING.md)
- Promotion: [references/PROMOTION.md](references/PROMOTION.md)
- Lifecycle: [references/LIFECYCLE.md](references/LIFECYCLE.md)
- Adaptive study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Planning: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Portable F/L routing: [references/PORTABLE_MODEL_ROUTING.md](references/PORTABLE_MODEL_ROUTING.md)
- Generic model routing: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Codex routing: [references/MODEL_ROUTING_CODEX.md](references/MODEL_ROUTING_CODEX.md)
- Claude routing: [references/MODEL_ROUTING_CLAUDE.md](references/MODEL_ROUTING_CLAUDE.md)
- Gemini routing: [references/MODEL_ROUTING_GEMINI.md](references/MODEL_ROUTING_GEMINI.md)
- Qwen routing: [references/MODEL_ROUTING_QWEN.md](references/MODEL_ROUTING_QWEN.md)
- Muse routing: [references/MODEL_ROUTING_MUSE.md](references/MODEL_ROUTING_MUSE.md)
- Token economics: [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md)
