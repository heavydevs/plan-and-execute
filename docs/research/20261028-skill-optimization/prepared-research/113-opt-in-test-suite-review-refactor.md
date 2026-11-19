# P060 — Explicit-scope automated-test review and refactor (TODO 113/114)

Prepared 2026-11-19. Implementation-ready separate contract; **do not run any project-wide refactor as part of implementing the skill**. Task 113 creates the on-demand review/refactor reference and guarded command; task 114 provides actual independent review of capability implementation. P058/P059's policy and P057's batch-failure engine are prerequisites. See `111-impact-aware-test-design-and-selection.md` for the testing taxonomy and impact selector.

## Two distinct scopes and permission boundaries

**Mode A: existing repository tests.** Trigger **only** when the user actively asks to review/refactor existing/repository-wide tests (no opt-out assumptions, no silent migration). Default is `audit_only`; an explicit request that authorizes edits controls migration. The user can authorize a bounded subset first. The runner must retain source of user authorization and precise target scope; a model cannot self-produce permission by inserting a CLI flag or by interpreting a generic "improve project" request. Existing non-plan tests stay untouched otherwise. Reading hundreds of existing tests for a global review is itself a scoped expensive operation: not automatic.

**Mode B: tests introduced/modified by the current plan.** Trigger **only** on explicit request to review the current plan's tests. Restrict analysis and all mutation to test files/definitions with stable provenance from the active plan's task receipts, Git baseline/diffs and source hashes. Distinguish a file newly created by the plan from a legacy file modified by the plan; within a mixed legacy file, modify only test cases/sections genuinely created or altered by this plan, preserving unrelated legacy cases. If ownership cannot be established, report ambiguity and **do not modify** uncertain cases. Default report first. A separate edit request is required for mutating tests if user only requested a review.

**Both:** maintain original test execution behavior and contractual coverage; production code, settings, external test resources, fixtures shared with legacy tests and test-bypass configuration require separate explicit scope. Never delete all old tests to replace with a handful of "green" E2E. No automatic disabling, skip, quarantine or relaxing assertions/coverage thresholds.

## Dedicated on-demand reference instead of always-on nested skill

Add `skill/plan-and-execute/references/TEST_REVIEW_REFACTOR.md`. Router mentions it once in `SKILL.md`/`WORKFLOW.md` **only when explicit user review/refactor request exists**; no default startup loading. Detailed checklist and examples live here, not in every task prompt. A guarded deterministic helper `scripts/test_audit.py` discovers tests, counts/layers, provenance and cost; AI workers receive only the relevant findings + exact allowed paths, not all test files or raw logs. Reuse existing phase/model/provider routing, failure evidence and job monitoring; do not launch a second orchestration engine.

Proposed commands (verify actual CLI conventions before implementation):
- `test_audit.py inventory --repo-root . --scope plan --plan <active-plan> --output <owned-report>`
- `test_audit.py inventory --repo-root . --scope repository --request-evidence <trusted-host-reference> --output <owned-report>`
- `test_audit.py refactor-plan --report <reviewed-report> --request-evidence <trusted-host-reference> --dry-run`

Read-only inventory cannot modify any project file or call paid providers. Refactor command validates authorization through trusted session/plan provenance and a per-file allowlist before writing; `--scope repository` or a JSON flag alone cannot authorize edits. Reject path traversal, symlinks escaping root, stale source hashes, untracked ownership conflicts, plans outside project, current plan mismatch and concurrent conflicting migrations.

## Deterministic analysis and review rubrics

1. Snapshot repository base, tests, runner version, task receipts and user authorization. Enumerate test files via framework discovery and hash them; infer layer/cost via actual runner/test metadata, classify unknown rather than guessing. Build `test_case -> requirement/behavior -> fixture/dependency -> owner_task -> runtime` map.
2. Flag **duplicate behavior across layers**, over-represented E2E field combinations, unasserted outcomes, brittle selectors, sleep/network dependency, shared fixture/order coupling, flaky tests, over-mocking contracts, missing negative cases, dead tests, unexecuted tests, very expensive setup, missing ownership and unsafe deletion. Some duplication is deliberate for critical cross-layer checks; explain before suggesting removal.
3. Produce prioritized findings with severity, source paths/test IDs, observed runtime/run frequency, measured/estimated savings clearly distinguished, risk and **proposed lowest trustworthy replacement**. Preserve full behavior matrix (including validation edges, role/security errors, min/max fields, integration boundaries, critical E2E).
4. Present `audit_only` report: counts by trustworthy layer, E2E candidates for conversion, behavior-gap map, retained critical flows, impacted code/tests, unknown/ambiguous owners, estimated validation plan. Do not mutate from review alone.
5. On explicit edit authorization, create a bounded refactoring plan with isolated batches: establish baseline green state; add/strengthen equivalent unit/contract/integration coverage first; run old+new tests together; rewrite only scoped test cases; remove redundant expensive cases only after independently demonstrating equivalence and no regression (including missing-field/validation semantics); validate changed fixtures and targeted dependents after each batch.
6. Final validation for authorized repository-wide migration: complete affected/global suite on the same final fingerprint, plus required browser/CI cross-configured projects. For plan-owned-only review/refactor: scope to current-plan-owned tests plus touched dependencies and mapped acceptance; full global run at plan final unless changes to shared framework/fixtures need earlier broad gate. P057 triage applies to failing cases.
7. Store real `review_scope`, original user request anchor, `approved_edit_scope`, source/plan fingerprints, changed tests, preserved legacy tests, before/after test counts/runtime (if measured), traceability, missing risks, and reviewer/evidence hashes. Never mark a model's claim as a measured improvement.

## Review checklist for migration quality

- No blind 80/15/5 quota, fake test coverage increase or universal `max three E2E` rule.
- Every validation/business rule still tested, including boundaries, denial cases, error/retry behavior and accessibility/UI semantics.
- Min/max successful E2E and representative validation E2E retained when behavior warrants; all other browser E2E require specific unique confidence value.
- No weakening security, payment/financial, concurrency, real database/contract or configuration regressions.
- No uncontrolled shared state, arbitrary sleep, long-running setup or test-order dependency introduced.
- No production code edits, no preexisting legacy case touched in plan mode without permission, no unauthorized suite-wide rewrite.
- The source hashes and selected test list remain current across parallel tasks/other branches; tests are not accepted from previous code snapshots.
- AI decisions run through applicable capability floor; deterministic inventory and report filtering need no model. Review fixes go only to explicit approved scope.
- Before/after time/compute/tokens and defects detected are measured only when a matched baseline exists; otherwise report "unknown".

## Adversarial fixtures

1. Repo 500 existing E2E tests, generic new feature request -> inventory/refactor *not called*, files unchanged.
2. User asks "review only tests created by my active plan" -> only plan-provenance test cases reported; no edits; unrelated 100 legacy tests untouched even when in same file.
3. User explicitly authorizes current-plan refactor -> only exact plan-owned test cases changed and current baseline/CI checks pass; unowned mixed-file sections preserved.
4. User authorizes global refactor but **not** production changes -> helper rejects changes outside test scope; old test behavior retained until equivalent replacements verify.
5. Unknown source-provenance, moved test, changed baseline, symlink path, untrusted flag or concurrent plan -> refuse write, report safe next action.
6. Duplicate E2E found but one covers browser-specific authorization bug -> keep browser test with reason despite unit replacement; test quality not judged by count alone.
7. Flaky or intentionally skipped legacy tests -> classify, don't fake green or delete; preserve evidence and user-facing risk.
8. Simulate 1,000 E2E, 100 unit/contract alternatives, 3 critical UI flows; compare measured run counts, independence and seeded mutation/regression detections. No invented time/token percentage.

## Sources and limits

See detailed P058/P059 primary-source register in `111-impact-aware-test-design-and-selection.md`. Specific refactoring basis:
- Gerard Meszaros, *xUnit Test Patterns*, publisher summary and "test smells": https://www.oreilly.com/library/view/xunit-test-patterns/9780131495050/
- Ham Vocke, practical pyramid and pushing tests down: https://martinfowler.com/articles/practical-test-pyramid.html
- Martin Fowler on non-determinism, quarantine and fixtures: https://martinfowler.com/articles/nonDeterminism.html
- Playwright real-user behavior and robust locators: https://playwright.dev/docs/best-practices
- Google, freely available book ch11/ch14: https://abseil.io/resources/swe-book/html/ch11.html and https://abseil.io/resources/swe-book/html/ch14.html
- Official Claude progressive disclosure: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

**Evidence boundary:** recommendations derive from public book chapters, publisher overviews and tool documentation; this repository-wide provenance and authorization scheme is an engineering design, not a guaranteed native capability of any provider. Test code has not been modified and no existing suite has been audited as part of this planning amendment.
