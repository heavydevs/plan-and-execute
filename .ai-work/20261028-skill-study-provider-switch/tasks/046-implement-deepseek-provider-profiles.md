---
task_id: "046"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,045"
allowed_related_task_reads: "none"
---

# 046 — Implement deepSeek provider profiles

Objective: Keep DeepSeek compatibility, resolved model identity and billing evidence explicit; validate unsupported or ignored fields rather than assuming full Anthropic equivalence.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/046-deepseek.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Test required parameters against documented supported and ignored fields; an HTTP success does not prove that every required option is honored.
- [ ] **S003** Implement revised contract 2 — Track alias replacement and backend identity separately from requested model labels and refresh price/quality evidence.
- [ ] **S004** Implement revised contract 3 — Treat off-peak discounts as optional evidence that cannot override deadline, privacy or capability constraints.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement deepSeek provider profiles
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/routing_config.py`, `skill/plan-and-execute/scripts/deepseek_provider_self_test.py`, `test/optimization/deepseek_self_test.py`, `skill/plan-and-execute/references/MODEL_ROUTING_DEEPSEEK.md`, `docs/research/20261028-skill-optimization/implementation/046-receipt.json`, `docs/research/20261028-skill-optimization/implementation/046-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/046-deepseek.md.
- Use only task 046 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/046-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A compatible endpoint does not cause Claude-native effort values to be sent blindly.
- A route with unverified high-effort support cannot satisfy a maximum task merely through a label.
- Time-window price fixtures cover boundaries and timezone interpretation without assuming current discounts.
- Endpoint/profile changes invalidate route intent and preserve unrelated cooldown state.
- No endpoint credentials appear in process logs, manifests or economic reports.
- A required schema or thinking option reported ignored cannot qualify the route.
- A retired alias serving a replacement triggers evidence requalification without rewriting past attempts.
- Missing usage remains null and positive infinity is rejected.
- No automatic paid endpoint or off-peak waiting policy is enabled.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_046`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_046`
