---
name: plan-and-execute
description: Orchestrate long-horizon software changes with selective planning, staged preprocessing for oversized specifications, resumable isolated TODOs, adaptive model routing, and versioned shared-pattern contracts. Prefer direct execution for cohesive bounded work; create a final plan only when orchestration is useful; create a primary preprocessing plan first when request volume would make one-shot final planning economically unsafe.
---

# Plan and Execute

Treat **context**, **model capability**, and **resumability before quota exhaustion** as separate budgets. Route to exactly one of three execution shapes and load only the references required by the selected path.

## 1. Route lifecycle commands first

Exact `current`/`status`, `resume`/`continue`, `cancel`, and `reset` use [references/LIFECYCLE.md](references/LIFECYCLE.md).

## 2. Gate 1 — DIRECT vs planned work

Prefer **DIRECT** when the remaining request is cohesive and can be implemented/validated safely in the current useful context. Strong signals for planned work are:

- two or more independently verifiable workstreams whose retained reasoning would not materially help each other;
- broad repository/external study before implementation is safe;
- repo-wide migration, compatibility, security, data-integrity, concurrency, or cross-module coordination;
- likely work across sessions/providers/quota windows/context compaction where durable resume has material value;
- isolated workers would materially reduce unrelated context or improve independent validation;
- the user explicitly requires a durable plan/checklist rather than merely selecting the skill.

File count alone is not a signal. Cohesive related-file work may stay direct.

### DIRECT EXIT

When DIRECT wins:

- create no `.ai-work`, study, requirement inventory, plan, TODO, task file, primary plan, pattern registry, worker, or lifecycle state;
- do not read orchestration, primary-planning, or plan-schema references;
- implement and validate directly in current useful context;
- continue applying model economy from section 4.

When uncertain, prefer DIRECT. Read [references/ROUTING.md](references/ROUTING.md) only for a genuinely ambiguous boundary.

## 3. Gate 2 — FINAL_PLAN vs PRIMARY_PLAN

Run this gate **only after planned/orchestrated work has been selected**.

The goal is to make a durable checkpoint before an oversized request can consume expensive-model credits merely to understand itself.

### Lightweight assessment first

- If the authoritative request is a local/request file, run `scripts/preplanctl.py assess --file <path>` before loading the whole file into an expensive planning context.
- For a Drive/Docs/Office/PDF or other external document, use the host's authenticated file/connector tools to obtain readable text or a local source representation first; prefer deterministic extraction. Do not paste the complete document through chat merely to measure it.
- If a large inline request is already model-visible, persist it to a request file when practical so later phases can resume from disk. Small inline requests need no extra measurement round-trip.
- The assessment uses economic working-set guardrails, not a model's advertised maximum context window.

Route:

1. **FINAL_PLAN** — planned work whose request is small/manageable enough for ordinary adaptive study + final-plan construction.
2. **PRIMARY_PLAN** — request volume/breadth would make direct final planning credit-heavy, attention-fragile, or non-resumable before a durable plan exists.

Default `preplanctl` guardrails: direct final planning below roughly 12k estimated source tokens without a breadth trigger; primary planning at 24k+ estimated tokens; between them, structural breadth (default 30+ detected headings at 8k+ tokens) can trigger primary planning. These are tunable economics defaults, not universal model limits.

### FINAL_PLAN path

Read [references/ORCHESTRATION.md](references/ORCHESTRATION.md). **Do not read `PRIMARY_PLANNING.md`.**

If the input is a prepared package produced by an earlier primary plan, read [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md); otherwise ordinary final planning does not need that file either.

### PRIMARY_PLAN path

Read [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md). It owns deterministic fragmentation, the resumable preprocessing checklist, package coverage, and the compact handoff. **Do not preload the ordinary full orchestration protocol while creating the primary plan.**

Use:

```bash
python <skill-dir>/scripts/preplanctl.py prepare --repo-root . --file <request-file>
```

The generated primary plan uses the existing durable `planctl` engine, but its only deliverable is a prepared request package. After `validate-package` succeeds, enter the normal **FINAL_PLAN** path using `FINAL_PLAN_INPUT.md`. Final planning recalculates implementation TODO boundaries and model routes from scratch.

## 4. Always-on model economy

These rules apply in DIRECT, PRIMARY_PLAN, FINAL_PLAN, and implementation:

1. Use deterministic tools for mechanical search, hashing, splitting, indexing, builds/tests/lint, and exact transforms.
2. If exploration would load substantial disposable context, delegate it to the cheapest credible read-only worker and request/persist a compact evidence map.
3. Do not spawn a worker for one or two obvious reads or a swarm for sequential work. Prefer at most two concurrent explorers unless branches are genuinely independent.
4. Route by **leaf semantic difficulty, verifiability, and blast radius**, not by parent-request size or the model selected in the root chat.
5. Cheap-first is appropriate when deterministic validation catches failure. Start stronger for high-blast-radius, weakly verifiable decisions.
6. Escalate from concrete failure evidence and stop once acceptance criteria plus available independent validation pass.

Planning itself has adaptive routing. Read [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md) only when assigning planning-stage workers/routes. Final implementation TODOs continue to use [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md) plus exactly one active provider mapping.

A route used in primary preparation never becomes an implementation route by inheritance:

`primary route != final-planning route != implementation route`.

## 5. Promote late when DIRECT grows

Promote a DIRECT request when substantial work remains and scope splits into independent outcomes, broad research/migration analysis becomes necessary, interruption/quota risk makes durable resume valuable, or high context pressure accompanies substantial non-cohesive work.

Context pressure is secondary; do not promote a nearly finished cohesive task merely because context is high.

On promotion, read [references/PROMOTION.md](references/PROMOTION.md). Persist completed work, validations, active decisions, relevant code, blockers/risks, and **remaining outcomes** with `promotectl.py`; plan only remaining work. After promotion, run Gate 2 on any remaining authoritative request material that has not already been compacted.

## 6. Final-plan invariants

The ordinary final-plan harness owns adaptive study, traceable requirements, TODO decomposition, execution context, shared patterns, model/provider routing, resumable subtasks, validated learnings, deterministic validation, lifecycle recovery, final handoff, and guarded cleanup.

Non-negotiable invariants:

- `manifest.json` is authoritative for normal plan/task state; `TODO.md` is the terse status index;
- every executable TODO has a bounded definition and resumable subtasks;
- every TODO declares `provider`, `model_tier`, and `reasoning_effort`; use the lowest credible leaf capability and escalate only from evidence;
- planning stages also choose capability deliberately rather than blindly inheriting the root model;
- cross-cutting normative contracts may live in versioned `patterns/` artifacts with explicit signatory TODOs;
- a pattern revision invalidates only completed signatories that adopted an older revision; those TODOs must be reopened/revalidated before final completion;
- quota/rate-limit exhaustion and host interruption are not technical failures;
- another compatible provider can resume from persisted state without the previous chat transcript;
- implementation changes, tests, product artifacts, and commits survive cleanup.

Use [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md) only when final planning identifies a genuine evolving cross-TODO contract. Do not preload it for plans with no shared patterns.

## Reference map — load on demand

- Orchestration/final plan: [references/ORCHESTRATION.md](references/ORCHESTRATION.md)
- Oversized primary plan: [references/PRIMARY_PLANNING.md](references/PRIMARY_PLANNING.md)
- Prepared-package boundary: [references/PLANNING_INPUT_CONTRACT.md](references/PLANNING_INPUT_CONTRACT.md)
- Planning-stage routing: [references/PLANNING_ROUTING.md](references/PLANNING_ROUTING.md)
- Shared evolving patterns: [references/SHARED_PATTERNS.md](references/SHARED_PATTERNS.md)
- Artifact writing: [references/ARTIFACT_WRITING.md](references/ARTIFACT_WRITING.md)
- Intake: [references/INTAKE.md](references/INTAKE.md)
- Direct routing: [references/ROUTING.md](references/ROUTING.md)
- Promotion: [references/PROMOTION.md](references/PROMOTION.md)
- Lifecycle: [references/LIFECYCLE.md](references/LIFECYCLE.md)
- Adaptive study: [references/ADAPTIVE_STUDY.md](references/ADAPTIVE_STUDY.md)
- Final planning protocol: [references/PLANNING_PROTOCOL.md](references/PLANNING_PROTOCOL.md)
- Execution context: [references/EXECUTION_CONTEXT.md](references/EXECUTION_CONTEXT.md)
- Final plan schema: [references/PLAN_SPEC.md](references/PLAN_SPEC.md)
- Execution: [references/WORKFLOW.md](references/WORKFLOW.md)
- Generic model routing: [references/MODEL_ROUTING.md](references/MODEL_ROUTING.md)
- Codex routing: [references/MODEL_ROUTING_CODEX.md](references/MODEL_ROUTING_CODEX.md)
- Claude routing: [references/MODEL_ROUTING_CLAUDE.md](references/MODEL_ROUTING_CLAUDE.md)
- Token economics: [references/TOKEN_EFFICIENCY.md](references/TOKEN_EFFICIENCY.md)
