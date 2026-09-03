---
name: plan-and-execute
description: Orchestrate long-horizon software changes that benefit from durable resumability, multiple independently verifiable workstreams, broad repository or external research, repo-wide migration or compatibility work, or isolated delegated execution. Also use when explicitly invoked or for plan lifecycle status, resume, cancel, or reset. Do not use for routine bug fixes, bounded features or refactors, ordinary test updates, or cohesive small/medium changes one agent can implement and validate in the current context, even across several related files. When uncertain, prefer direct execution and promote later only if scope, research needs, resumability value, independent workstreams, or context pressure materially grow.
---

# Plan and Execute

Treat context as a budget. This entrypoint is a router: pay for the full planning harness only when isolation, persistence, research, or resumability can materially improve the implementation.

## 1. Route lifecycle commands first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` always use the lifecycle workflow. Read [references/LIFECYCLE.md](references/LIFECYCLE.md) only for those operations.

## 2. Decide DIRECT vs ORCHESTRATED before creating state

An explicit user invocation of `plan-and-execute`, an existing requirements file passed for orchestration, or a lifecycle command selects **ORCHESTRATED**.

For implicit invocation, select **ORCHESTRATED** only when at least one strong signal is present:

- two or more independently verifiable workstreams whose retained reasoning would not materially help each other;
- broad repository study or substantial external research is needed before implementation choices are safe;
- repo-wide migration, compatibility, security, data-integrity, concurrency, or cross-module work needs durable coordination;
- the work is likely to cross sessions, providers, quota windows, or context compaction and durable resume state has real value;
- isolated delegated workers materially reduce unrelated context or allow independent validation.

File count alone is not a signal. A cohesive controller/service/entity/test change may stay direct even when it touches many related files.

### DIRECT EXIT

If none of the strong signals applies and the skill was selected implicitly:

- create no `.ai-work` directory, study, requirements inventory, plan, TODO, task file, worker, or lifecycle state;
- do not read orchestration references;
- stop applying this skill and implement/validate the request directly in the current agent context;
- keep shared reasoning in the current conversation while it remains useful.

When uncertain, prefer DIRECT. A false negative can be promoted later; an unnecessary plan has already spent tokens and time.

Read [references/ROUTING.md](references/ROUTING.md) only when the boundary is genuinely ambiguous or when changing routing behavior/evals.

## 3. Promote late when a direct task grows

A DIRECT request may become orchestration-worthy after implementation starts. Promote when substantial work remains and one or more of these becomes true:

- discovered scope splits into independent outcomes;
- broad research or migration/compatibility analysis becomes necessary;
- interruption/quota risk makes durable resume state valuable;
- the host reports high context pressure and substantial non-cohesive work remains.

Context pressure is a secondary signal, never a universal fixed percentage. Do not wait for a hard 90% threshold when semantic scope already justifies promotion, and do not promote a nearly finished cohesive task merely because context is high.

On promotion, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work, validated results, active decisions, relevant code, blockers/risks, and **remaining outcomes** with `promotectl.py`; then create TODOs only for remaining work. Never invent retroactive TODOs for work already completed.

## 4. Run the full harness only after ORCHESTRATED is selected

Read [references/ORCHESTRATION.md](references/ORCHESTRATION.md). It owns adaptive study, traceable requirements, TODO decomposition, task-definition files, model/provider routing, resumable subtasks, validated cross-task learnings, deterministic validation, lifecycle recovery, final handoff, and guarded cleanup.

These invariants remain non-negotiable in every orchestrated or promoted plan:

- `manifest.json` is authoritative; `TODO.md` remains the terse status index;
- every executable TODO has its own bounded definition and resumable subtasks;
- every TODO declares `provider`, `model_tier`, and `reasoning_effort`; choose the lowest credible capability for that leaf task and escalate only from evidence;
- quota/rate-limit exhaustion and host interruption are not technical failures;
- another compatible AI/provider can resume from persisted state without the previous chat transcript;
- implementation changes, tests, generated product artifacts, and commits survive plan cleanup.

## Reference map

- Full long-horizon workflow: [references/ORCHESTRATION.md](references/ORCHESTRATION.md)
- Precise derived artifact writing: [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md)
- Guided request intake: [references/INTAKE.md](references/INTAKE.md)
- Direct/orchestrated routing: [references/ROUTING.md](references/ROUTING.md)
- Late direct -> orchestrated handoff: [references/PROMOTION.md](references/PROMOTION.md)
- Lifecycle/resume: [references/LIFECYCLE.md](references/LIFECYCLE.md)
- Adaptive study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Planning/decomposition: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context/learnings: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Model/provider routing: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Token economics: [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md)
