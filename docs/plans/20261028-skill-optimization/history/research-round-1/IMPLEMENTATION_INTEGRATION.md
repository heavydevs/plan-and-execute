# Single-plan integration and acceptance

Tasks082-086 integrate the implemented topic contracts and provider-switch track. They do not synthesize another backlog or generate another plan.

1. Require current receipts for every implementation and its independent code-review/correction gate.
2. Re-run composed-entrypoint, disabled-mode, legacy schema, availability, phase/reset, process, log/redaction and package-membership regressions.
3. Preserve the twelve original provider-switch acceptance cases; map every case to an executed test and hash-pinned log. Research proposals are not passes.
4. Run `npm ci`, `npm run check`, and `npm pack --dry-run --json`; inspect the actual package file list. Record pre-existing failures with exact baseline evidence rather than waiving new failures.
5. Verify all newly added targeted tests are wired into repository checks. Avoid tests that only assert the presence of a phrase without checking behavior.
6. Apply `skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md` last; report decisions, changed files, actual test results, Windows/live-provider limits and costs in Portuguese.
7. Keep source changes, tests and prepared research. Do not install, modify global configuration or publish/commit/push without separate permission.

Maximum-qualified code reviews remain independent execution requirements. The host-generated research and structural plan review do not satisfy them. The absence of an authenticated reviewer must remain visible, not be filled with a fabricated receipt.
