# Single-plan integration and acceptance - revision 2

Tasks082-086 integrate the implemented topic contracts and provider-switch track. They do not generate another plan.

1. Verify every historical implementation/review receipt against the exact recorded inputs and artifacts. A later unrelated edit does not turn an old pass into a current-tree pass; preserve that history without rewriting it.
2. Use current source, command, resource-map and contract hashes for new integration runs. Revalidate affected contract owners; do not require all historical receipts to pretend they describe the final tree.
3. Exercise composed-entrypoint, disabled-mode, legacy schema, availability, provider/phase reset, process ownership, log/redaction and package-membership regressions on the current tree.
4. Preserve the twelve original provider-switch acceptance cases and map each to an actually executed test and hash-pinned log. Prepared proposals and fixture construction alone do not pass runtime acceptance.
5. Task082 wires the added targeted tests into repository checks and adds a regression proving that the integration command executes them. Never accept a phrase-presence test as behavioral proof.
6. If integration discovers a product defect outside its write scope, reopen the owning implementation and its correction review through the native lifecycle/contract mechanism. Keep integration pending until revalidation; no silent scope expansion.
7. Run `npm ci`, `npm run check`, and `npm pack --dry-run --json`. Inspect actual tarball membership and staged skill ZIPs. An `--ignore-scripts` inventory is not proof that prepack passed.
8. Apply `skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md` last. Report changed files, executed checks, unverified Windows/live-provider cases, measured versus unknown cost, and reopened work in Portuguese.
9. Keep source, tests and research. Do not install, change global configuration or commit/push/publish without separate permission.

Independent maximum-qualified reviews remain real execution requirements. Host research preparation and structural review do not satisfy them. A missing qualified reviewer pauses acceptance; no fake provider/session record is permitted.
