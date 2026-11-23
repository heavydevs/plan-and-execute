---
task_id: "022"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "strong"
reasoning_effort: "high"
complexity: "high"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 021"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 022 — Implement provider chains, cooldowns, quotas and availability ledgers

## Objective

Use one coherent allowed-provider chain and a bounded availability policy with explicit quota scopes, combined retry budgets and non-secret route fingerprints.

## Requirements covered

- R002
- R003
- R004
- R005
- R007
- R032
- R037
- R038
- R039
- R042
- R044

## Complexity and atomicity

- Complexity: **high**
- Why this is one executable TODO: One bounded implementation contract with its regression tests; source coupling requires a shared acceptance boundary, not an arbitrary file-count split.

## Context-isolation boundary

- Why one fresh worker context helps this whole TODO: This task owns one behavior or correction gate with independently checkable outcomes.
- Context that is genuinely shared by all subtasks:
- Read only the assigned decision, source targets and accepted prerequisite receipts.
- Concerns deliberately isolated into other TODOs:
- Do not load unrelated reports, provider guides or historical conversation transcripts.

## Isolation contract

This task definition and the exact execution-context files listed below are the only planning artifacts assigned to this worker. Read the task definition first, then read every assigned context file. Do not discover or open any other context file, `PLAN.md`, `TODO.md`, `manifest.json`, `orchestrator.config.json`, result files, logs, or unrelated task definitions. You may read repository source, tests, build files, and runtime output relevant to this task.

Another task definition may be opened only when one of the explicitly allowed task ids above is necessary to resolve a blocked dependency, ambiguity, or validation conflict. Record the task id and reason in the completion report.

## Assigned execution context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Assigned validated learnings

- None

These files are concise, immutable artifacts produced only after another TODO passed deterministic validation. Read exactly the assigned files, never a previous worker transcript or an unassigned learning file.

## Resumable subtask checklist

- [ ] **S001** — Read assigned research and pin applicable contracts
  - Read docs/research/20261028-skill-optimization/prepared-research/022-availability.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Track quota scope and observation expiry independently from functional failure evidence and provider capability.
- [ ] **S003** — Implement revised contract 2
  - Document and cap the combined runner, CLI and SDK retry budget; report unobservable internal retries as unknown.
- [ ] **S004** — Implement revised contract 3
  - Include allowed-provider, privacy, workload, snapshot and effective-routing settings, the per-tier chain (tier_routes) and the provider permission/sandbox mode in the availability fingerprint.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement provider chains, cooldowns, quotas and availability ledgers

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/availability.py
- skill/plan-and-execute/scripts/workload_routing.py
- test/optimization/availability_self_test.py
- skill/plan-and-execute/references/ROUTING_CONFIG.md
- docs/research/20261028-skill-optimization/implementation/022-receipt.json
- docs/research/20261028-skill-optimization/implementation/022-outcome.md

## Dependencies

- 001
- 021

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/022-availability.md.
- Use only task 022 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/022-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- TODO 022 implements the availability contract and backward-compatible selector seam. The opt-in top-switch controller is integrated only by 074; disabled behavior must remain unchanged.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- Quota in one configured pool does not block another pool unless the configuration explicitly shares it.
- Availability failures leave functional failure counts and semantic ladder evidence unchanged.
- Fallback-disabled and CLI-pinned cases never widen the allowed chain.
- A changed route fingerprint invalidates cached intent while retaining unrelated valid cooldowns.
- Every eligible unavailable candidate yields a bounded, redacted reason; all-unavailable returns75 without a spin loop.
- Quota exhaustion in one configured pool leaves another observed-independent pool eligible.
- A fallback that violates required capabilities or data policy is rejected with a reason.
- SDK retry fixtures cannot multiply an unbounded runner wait.
- Availability pauses preserve subtasks without adding a functional failure.
- Credit exhaustion is a long-lived quota-scope observation with reset/expiry, not a 300-second retry loop, and never a functional or capability failure.
- With one provider's credits exhausted the chain continues Antigravity > Codex > Claude for implementation and Codex > Claude for review.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_022`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_022`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
