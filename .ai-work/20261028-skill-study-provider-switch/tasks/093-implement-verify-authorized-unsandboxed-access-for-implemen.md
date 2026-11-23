---
task_id: "093"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R049"
dependencies: "029, 031, 033, 035, 037, 039, 041, 043, 045, 047, 061, 092, 073"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 093 — Implement verify authorized unsandboxed access for implementing agents

## Objective

For authorized trusted-project implementation delegation, ensure effective localhost, network and workspace access without a hidden sandbox; pause when host policy blocks it.

## Requirements covered

- R049

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One coherent outcome, focused tests and an independent review boundary.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: Steps share one observable implementation or review outcome.
- Context that is genuinely shared by all subtasks:
- Only assigned contract and actual code evidence.
- Concerns deliberately isolated into other TODOs:
- Unrelated TODOs and old transcripts are excluded.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read evidence
  - Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** — Implement contract 1
  - Treat the owner's user-global config as the authorization record: when it grants full access, Codex and Antigravity implementation workers run full-access without sandbox; the skill never writes that config; the built-in default stays conservative.
- [ ] **S003** — Implement contract 2
  - Replace the Codex worker default --sandbox workspace-write (build_worker_command codex branch) with the configured mode and a version-verified flag; keep Antigravity skip_permissions; reviewers/observers inherit no write access.
- [ ] **S004** — Implement contract 3
  - Report unsupported or prohibited full access instead of silently falling back to a sandbox or modifying global settings.
- [ ] **S005** — Implement contract 4
  - Keep non-implementing observers restricted and test host denial, wrong flags, resume and unsafe inputs.
- [ ] **S006** — Run tests
  - Implement test/optimization/full_access_delegation_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** — Record implementation
  - Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/093-receipt.json and docs/research/20261028-skill-optimization/implementation/093-outcome.md.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- For authorized trusted-project implementation delegation, ensure effective localhost, network and workspace access without a hidden sandbox; pause when host policy blocks it.

## Out of scope

- No second plan or unrelated changes.
- No installation, provider login, publishing or user-global configuration changes without permission.

## Expected files

- skill/plan-and-execute/scripts/run_isolated.py
- skill/plan-and-execute/scripts/configure.py
- skill/plan-and-execute/scripts/routingctl.py
- skill/plan-and-execute/references/DELEGATION.md
- skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md
- skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md
- skill/plan-and-execute/references/ASSISTANTS.md
- test/optimization/full_access_delegation_self_test.py
- docs/research/20261028-skill-optimization/implementation/093-receipt.json
- docs/research/20261028-skill-optimization/implementation/093-outcome.md

## Dependencies

- 029
- 031
- 033
- 035
- 037
- 039
- 041
- 043
- 045
- 047
- 061
- 092
- 073

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 093 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/093-receipt.json and docs/research/20261028-skill-optimization/implementation/093-outcome.md; do not mark a pending task done without validation.

## Acceptance criteria

- An authorized delegated implementer can access permitted loopback services and required paths.
- Provider flags are version-qualified, and effective permission is actually verified.
- Host-enforced restrictions cause an actionable pause, not an unsafe bypass or false success.
- Observers remain genuinely read-only or tool-less, rather than gaining source writes.
- Threats from unrestricted commands are documented, with consent and no credential leakage.
- Implementation and review remain pending until actual execution evidence exists.
- A provider that cannot be probed (Codex credits exhausted) records effective_access: not_verified(quota).

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_093`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_093`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
