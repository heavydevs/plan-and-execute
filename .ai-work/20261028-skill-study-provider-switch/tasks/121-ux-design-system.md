---
task_id: "121"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R065, R068"
dependencies: "025, 120, 128"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 121 — Implement opt-in UI/UX design system, identity and compact agent memory

## Objective

Implement opt-in UI/UX design system, identity and compact agent memory. Read assigned P065 architectural report and current affected symbols; verify accepted 025/120 prior receipts only.

## Requirements covered

- R065
- R068

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation change or independent final-hash correction gate.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Single independently verifiable UI/UX capability contract.
- Context that is genuinely shared by all subtasks:
- Read only P065 report, affected source symbols and accepted dependency evidence.
- Concerns deliberately isolated into other TODOs:
- Do not read unrelated tasks, full style inventories, private screenshots or old logs.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Inspect scoped source architecture
  - Read assigned P065 architectural report and current affected symbols; verify accepted 025/120/128 receipts only (shared consent comes from 127).
- [ ] **S002** — Implement or genuinely review contract
  - Implement UX intent/setup gate: ask once for new project or explicit design request; non-UI DIRECT default OFF with no prompt, model, browser or reading new reference.
- [ ] **S003** — Enforce consent/source-of-truth/safety
  - Extract real existing components, token/style source, route map by rg/AST and hashes; distinguish inferred from user-approved identity, do not rebrand mature UI.
- [ ] **S004** — Run adversarial validation
  - Produce durable project-local docs/ui-ux/AGENT_INDEX.md, manifest.json, identity.md, tokens.json, components.json and UX_PATTERNS.md only when opted in; validate DTCG aliases/cycles/contrast and keep approved status honest.
- [ ] **S005** — Record actual acceptance evidence
  - Wire concise lazy reference from SKILL.md, use shared routing and source hash invalidation not whole-project re-study.
- [ ] **S006** — Close current-source final check
  - Add tests for greenfield, brownfield, denied setup, backend-only no overhead, stale hashes, token cycles, path traversal, privacy; actual receipts only.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement opt-in UI/UX design system, identity and compact agent memory

## Out of scope

- No automatic production frontend edits, unrelated test changes, second plan or paid agent use.

## Expected files

- skill/plan-and-execute/scripts/design_context.py
- skill/plan-and-execute/scripts/uxctl.py
- skill/plan-and-execute/references/UI_UX_WORKFLOW.md
- skill/plan-and-execute/references/UI_UX_DESIGN_SYSTEM.md
- skill/plan-and-execute/SKILL.md
- test/optimization/ux_context_self_test.py
- docs/research/20261028-skill-optimization/implementation/121-receipt.json
- docs/research/20261028-skill-optimization/implementation/121-outcome.md

## Dependencies

- 025
- 120
- 128

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/121-uiux-design-prototype-research.md only while implementing task 121 and examine only current affected source/dependency receipts.
- Read assigned P065 architectural report and current affected symbols; verify accepted 025/120/128 receipts only (shared consent comes from 127).
- Implement UX intent/setup gate: ask once for new project or explicit design request; non-UI DIRECT default OFF with no prompt, model, browser or reading new reference.
- Extract real existing components, token/style source, route map by rg/AST and hashes; distinguish inferred from user-approved identity, do not rebrand mature UI.
- Produce durable project-local docs/ui-ux/AGENT_INDEX.md, manifest.json, identity.md, tokens.json, components.json and UX_PATTERNS.md only when opted in; validate DTCG aliases/cycles/contrast and keep approved status honest.
- Wire concise lazy reference from SKILL.md, use shared routing and source hash invalidation not whole-project re-study.
- Add tests for greenfield, brownfield, denied setup, backend-only no overhead, stale hashes, token cycles, path traversal, privacy; actual receipts only.
- Reuse routingctl, task_context_router, planctl, existing validators and P056 security/performance gates; no parallel orchestration.
- Produce real source hashes/test results and genuine independent review where required; never call prepared research executed implementation.
- P066: broad UX study strictly on first approved relevant project use or explicit pae ux init/refresh. Shared coding+UX consent from 127/128; subsequent UX tasks load approved scoped design index only; no repeated research.
- Shared first-use decision/state is implemented by 127 and reviewed by 128; do not build a second UX consent controller.
- Cross-check applicable negative cases A–P and provenance in P065 research; screenshot matching never overrides keyboard/functional failures; an unsupported tool is not a green run.

## Acceptance criteria

- Existing visual patterns remain canonical and fresh UI components reuse real exports and styles without unapproved redesign.
- Greenfield identity remains provisional until the user approves; design tokens have deterministic typed semantics.
- Non-UI task has no UX runtime or extra context; agent index is short, source-indexed and privacy-safe.
- Real tests prove hash invalidation and that no fictitious product implementation/review is credited.
- No recurring UX external study or model calls after setup; explicit refresh and one-time opt-in work with durable project state.
- UX init/refresh, first-use consent and no repeated research are verified by spies in tests; no backend-only overhead or silent paid calls.
- node tools/validate-skill.js passes and SKILL.md stays <= 7167 normalized characters with at most one lazy pointer line.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_121`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_121`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
