---
task_id: "046"
plan_id: "20261028-skill-study-provider-switch"
status: "pending"
provider: "auto"
model_tier: "standard"
reasoning_effort: "high"
complexity: "medium"
requirements: "R002, R003, R004, R005, R007, R032, R037, R038, R039, R042, R044"
dependencies: "001, 045"
context_files: "CONTEXT.md"
learning_files: "none"
allowed_related_task_reads: "none"
---

# 046 — Implement deepSeek provider profiles

## Objective

Keep DeepSeek compatibility, resolved model identity and billing evidence explicit; validate unsupported or ignored fields rather than assuming full Anthropic equivalence.

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

- Complexity: **medium**
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
  - Read docs/research/20261028-skill-optimization/prepared-research/046-deepseek.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** — Implement revised contract 1
  - Test required parameters against documented supported and ignored fields; an HTTP success does not prove that every required option is honored.
- [ ] **S003** — Implement revised contract 2
  - Track alias replacement and backend identity separately from requested model labels and refresh price/quality evidence.
- [ ] **S004** — Implement revised contract 3
  - Treat off-peak discounts as optional evidence that cannot override deadline, privacy or capability constraints.
- [ ] **S005** — Validate all assigned positive and negative cases
  - Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** — Record implementation evidence for independent review
  - Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

The manifest is authoritative. Checkpoint progress only through the dedicated `planctl.py subtask-start` and `subtask-complete` commands supplied by the orchestrator. Never edit this checklist directly.

## Eligible future learning targets

- None

## In scope

- Implement deepSeek provider profiles

## Out of scope

- No new broad research phase or second-plan generation.
- Do not change installed copies, user-global settings or publish without permission.

## Expected files

- skill/plan-and-execute/scripts/routing_config.py
- skill/plan-and-execute/scripts/deepseek_provider_self_test.py
- test/optimization/deepseek_self_test.py
- skill/plan-and-execute/references/MODEL_ROUTING_DEEPSEEK.md
- skill/plan-and-execute/scripts/workload_routing.py
- docs/research/20261028-skill-optimization/implementation/046-receipt.json
- docs/research/20261028-skill-optimization/implementation/046-outcome.md

## Dependencies

- 001
- 045

## Allowed related task definitions

- None

## Implementation guidance

- Read docs/research/20261028-skill-optimization/prepared-research/046-deepseek.md.
- Use only task 046 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/046-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance criteria

- A compatible endpoint does not cause Claude-native effort values to be sent blindly.
- A route with unverified high-effort support cannot satisfy a maximum task merely through a label.
- Time-window price fixtures cover boundaries and timezone interpretation without assuming current discounts.
- Endpoint/profile changes invalidate route intent and preserve unrelated cooldown state.
- No endpoint credentials appear in process logs, manifests or economic reports.
- A required schema or thinking option reported ignored cannot qualify the route.
- A retired alias serving a replacement triggers evidence requalification without rewriting past attempts.
- Missing usage remains null and positive infinity is rejected.
- No automatic paid endpoint or off-peak waiting policy is enabled.
- cooldown_key/cooldown_keys include the provider profile/backend, so quota exhaustion of that backend never cools down native Claude/Codex routes; legacy no-profile keys stay valid.
- Prepared research is not proof of implementation or independent-review completion.

## Required validation

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_046`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_046`


## Completion report

Return a concise report with: status, summary, changed files, validations executed, remaining risks, follow-ups, context files read, learning files read, completed subtask ids, any reusable learnings for predeclared future targets, and any related task definition read with its reason. Do not edit planning, context, learning, or checklist files directly.
