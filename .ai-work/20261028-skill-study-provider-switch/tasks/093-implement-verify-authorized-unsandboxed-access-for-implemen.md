---
task_id: "093"
status: "pending"
requirements: "R049"
dependencies: "029,031,033,035,037,039,041,043,045,047,061,092,073"
allowed_related_task_reads: "none"
---

# 093 — Implement verify authorized unsandboxed access for implementing agents

Objective: For authorized trusted-project implementation delegation, ensure effective localhost, network and workspace access without a hidden sandbox; pause when host policy blocks it.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read evidence — Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md, assigned prepared research and materially affected source files.
- [ ] **S002** Implement contract 1 — Treat the owner's user-global config as the authorization record: when it grants full access, Codex and Antigravity implementation workers run full-access without sandbox; the skill never writes that config; the built-in default stays conservative.
- [ ] **S003** Implement contract 2 — Replace the Codex worker default --sandbox workspace-write (build_worker_command codex branch) with the configured mode and a version-verified flag; keep Antigravity skip_permissions; reviewers/observers inherit no write access.
- [ ] **S004** Implement contract 3 — Report unsupported or prohibited full access instead of silently falling back to a sandbox or modifying global settings.
- [ ] **S005** Implement contract 4 — Keep non-implementing observers restricted and test host denial, wrong flags, resume and unsafe inputs.
- [ ] **S006** Run tests — Implement test/optimization/full_access_delegation_self_test.py and run mapped validation plus feature negative cases.
- [ ] **S007** Record implementation — Record real implementation and test evidence in docs/research/20261028-skill-optimization/implementation/093-receipt.json and docs/research/20261028-skill-optimization/implementation/093-outcome.md.

## Scope

In: For authorized trusted-project implementation delegation, ensure effective localhost, network and workspace access without a hidden sandbox; pause when host policy blocks it.
Out: No second plan or unrelated changes.; No installation, provider login, publishing or user-global configuration changes without permission.
Files: `skill/plan-and-execute/scripts/run_isolated.py`, `skill/plan-and-execute/scripts/configure.py`, `skill/plan-and-execute/scripts/routingctl.py`, `skill/plan-and-execute/references/DELEGATION.md`, `skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md`, `skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md`, `skill/plan-and-execute/references/ASSISTANTS.md`, `test/optimization/full_access_delegation_self_test.py`, `docs/research/20261028-skill-optimization/implementation/093-receipt.json`, `docs/research/20261028-skill-optimization/implementation/093-outcome.md`

## Guidance

- Read docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md.
- Follow task 093 in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Preserve exact user intent, bounded context, security floors and real deterministic tests.
- Refresh only materially changed facts from assigned prepared reports 006, 028, 060, 062.
- Preserve evidence in docs/research/20261028-skill-optimization/implementation/093-receipt.json and docs/research/20261028-skill-optimization/implementation/093-outcome.md; do not mark a pending task done without validation.

## Acceptance

- An authorized delegated implementer can access permitted loopback services and required paths.
- Provider flags are version-qualified, and effective permission is actually verified.
- Host-enforced restrictions cause an actionable pause, not an unsafe bypass or false success.
- Observers remain genuinely read-only or tool-less, rather than gaining source writes.
- Threats from unrestricted commands are documented, with consent and no credential leakage.
- Implementation and review remain pending until actual execution evidence exists.
- A provider that cannot be probed (Codex credits exhausted) records effective_access: not_verified(quota).

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_093`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_093`
