# Single-plan integration and acceptance - revision 2

Tasks087-098 add six implementation/review pairs. Tasks099-100 add semantic progress and safe stall recovery; tasks101-102 add host OS sleep guard and overnight readiness; tasks082-086 integrate the implemented topic contracts and provider-switch track. They do not generate another plan.

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

10. Before TODO 082, require real independent reviews 088/090/092/094/096/098, source hashes and mapped validations. Check DIRECT architecture delegation, skill activation negatives, blocked-task replanning, authorized localhost/full-access, per-agent setup/login only at new plan creation, and precise concise user-facing outputs. Keep A01–A12 unchanged.

11. P052: Before TODO 082, require actual 099 implementation plus genuine independent 100 review. Validate trustworthy work-unit counters, honest stage-local percentages and 300-second semantic stall diagnosis; only authorized confirmed code defects may escalate models and trigger corrected reruns. Keep monitoring plan-free in DIRECT, protect owned processes and distinguish environment failures.

12. P053: integration 082 depends on actual 101 native Windows/macOS/Linux host power lease and real independent 102 review. Test gapless 2-provider/long validation, safe acquire/release and crash-resume, WSL host scope, Modern Standby DC, lid/policy and strict unattended preflight; record safe CI/native tests and explicitly unknown physical-host behavior.

13. P054: Integration 082 depends on real 103 scheduler implementation and genuine independent 104 review. Exercise gate 5/6, exactly-once consent, 20-minute host scheduling for Windows/systemd-user/macOS, plan-owned registration, live-lease-safe recovery and automatic terminal removal, including plan vanished on crash, without confusing scheduling with OS-native sleep inhibition 101.
14. P055: Integration 082 depends on 105/106 six-tier frontier model routing and genuine independent review; test legacy opt-out/argv, L1–L6/F1–F6 schemas, observed `claude-fable-5-2` and `gpt-6.2-astra` as frontier (F6), architecture/code review only, after repeated Opus 5.5 / Sol 6.2 failure; Antigravity has no frontier preset (Carbon is Ultra/Enterprise only and never preset). Compare quality per validated credit, require permission/availability and current official model evidence; no unapproved pay-per-use promotion.

15. P058/P059: reviewed 111/112 conservatively selects changed/impacted task tests by source graph, ownership and risk, with broad fallback on unknown/dynamic/shared dependencies. Task completion uses all mapped impacted suites and P057's safe failure cycle. At final integration/release verify all configured global unit/integration/contract/E2E projects/shards on same final source; rerun final gate after code changes.

16. P060: 113/114 provide explicitly opt-in, audit-only-by-default legacy-suite or current-plan-created-test review. Require separately authorized edits and case-level provenance; preserve unrelated legacy test cases even within mixed files. Independent 114 review gates integration 082; check privacy/security, token context and no second orchestrator.


## 2026-11-19 P061–P064 extension

The **single active plan now contains 120 pending tasks**. 115/116: preferred provider auto-restoration and durable all-quota pause/wake. 117/118: contract-grounded AI test oracles and defect-detection evidence, complementing 109–114. 119/120: universal qualified phase routing and minimal indexed context. The three scoped research reports are `docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md`, `docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md`, `docs/research/20261028-skill-optimization/prepared-research/119-task-wide-lazy-routing.md`. Independent acceptance gates 116/118/120 precede 082; final review 086 remains last. Research and plan preparation are not actual product implementation, external review, test success or measured cost reduction. User authorized plan commit/push on this branch only.

## 2026-11-20 P067 extension

The single active plan now contains 132 tasks. 131/132: manager-tier delegation for plan supervision (configurable `routing_policy.manager_tier`, `routingctl.py supervise`, one read-only diagnosis per blocker fingerprint, availability faults never escalate, no root model switch). Research: `docs/research/20261028-skill-optimization/prepared-research/131-manager-tier-delegation.md`. Independent review 132 precedes 082; final review 086 remains last.
