---
task_id: "050"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001"
allowed_related_task_reads: "none"
---

# 050 — Implement resource discovery, freshness and runtime health

Objective: Maintain a content-fingerprinted, least-privilege resource map with explicit readiness, health and progress roles; reconcile only relevant inventory inputs and fail unknown observations conservatively.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/050-resource-map.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Separate startup readiness, runtime health and task progress in resource observations.
- [ ] **S003** Implement revised contract 2 — Reject stale content fingerprints and unsafe or unbounded probes; unknown observations never mean healthy.
- [ ] **S004** Implement revised contract 3 — Measure probe count and duration per validation and reuse only generation-valid scoped inventory.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement resource discovery, freshness and runtime health
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/service_map.py`, `skill/plan-and-execute/scripts/resource_watch.py`, `test/optimization/resource_map_self_test.py`, `skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md`, `docs/research/20261028-skill-optimization/implementation/050-receipt.json`, `docs/research/20261028-skill-optimization/implementation/050-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/050-resource-map.md.
- Use only task 050 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/050-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- Removing a referenced test file or changing toolchain input makes the map stale/actionable.
- A service inside startup grace is not misclassified as unhealthy.
- An unresponsive health probe ends at its bounded timeout and does not stall the watcher.
- A semantic failing test with healthy dependencies differs from a dependency outage.
- Unrelated resources are not probed or read for a focused validation.
- An open port with an unready service blocks dependent validation without escalating the model.
- A same-size build configuration change invalidates the map.
- Probe timeout or permission denial is explicit unknown/environment evidence.
- A map probe cannot silently run a service repair command.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_050`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_050`
