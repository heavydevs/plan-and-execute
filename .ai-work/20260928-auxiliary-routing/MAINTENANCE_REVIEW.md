# Final whole-skill maintenance review

Task: 006. Base: da785e567f5f3c6640f1ba3e0caf39900e4b0310.
Method: host-managed review of entrypoint, changed runner/controller flows, persisted
configuration/evidence, resource-map integration, tests, docs and package boundaries.
No independent model worker or authenticated native-provider generation was used.

## Verified contracts

- DIRECT still creates no plan. New configuration is an exact command, not a broad
  activation trigger. New references load only for relevant routing/advisory work.
- Global defaults and version-2 plan overlays merge predictably; legacy full
  snapshots and user model/capability overrides remain intact.
- Availability maintains logical tier/effort, phase isolation, permissioned chains
  and functional-failure evidence. Exhaustion/cancellation preserve resumable state.
- Assistant defaults off, uses bounded failure evidence and durable reservations,
  and never mutates authoritative failure classes, task status or code. Unsupported
  profiles skip safely. Claude's API-key billing is explicit in UI and docs.
- The compact worker retains context allowlists, unrelated-change preservation,
  service-map reconciliation, subtask controls and deterministic acceptance.
- User-requested plan retention overrides ordinary guarded cleanup. No plan was
  deleted; each completed task has its own committed report/checkpoint.

## Findings fixed

1. Pre-existing instruction budgets exceeded in SKILL, ORCHESTRATION and
   TOKEN_EFFICIENCY. Compressed wording, did not increase budgets.
2. Pre-existing timeout fixture mocked the old communicate API rather than current
   streamed wait-based capture. Updated fixture while retaining invalid-UTF8 and
   exit-124 checks. Standard-library subprocess fixtures now use -S to avoid
   unrelated site startup overhead hiding descendant-termination behavior.
3. Full suite exposed a pre-existing compact-worker prompt budget violation.
   Reduced repeated wording without relaxing the 2,600-character regression gate.
4. Reviewed Windows command quoting and registered the four new regression suites
   for native Windows CI as well as Linux. Windows CI remains a separate gate.
5. Corrected overly universal cache-invalidation claims; actual provider cache keys
   are provider/settings dependent. No billed-token economy claim was introduced.

## Executed validation

- npm run check: PASS through mapped resource watcher (Linux, Python 3.13, Node 22).
  27 Node tests; all registered Python suites, including 54 newly added tests.
- Focused availability suite after Windows fixture adjustment: PASS (15 tests).
- Skill schema/entrypoint validator: PASS; budgets unchanged.
- planctl validate, studyctl validate-plan and service-map audit-plan: PASS.
- Git diff whitespace check: PASS.

Instruction characters (not billed tokens):
- SKILL.md: 7727 -> 6826.
- references/ORCHESTRATION.md: 12877 -> 11963.
- references/TOKEN_EFFICIENCY.md: 10480 -> 9909.

## Explicit limits and further verification

- Native assistant support is Claude bare/tool-less with ANTHROPIC_API_KEY; this
  bills the API rather than subscription OAuth. No paid request was performed.
- Antigravity remains selectable but advisory generation skips it because its
  verified headless sandbox grants workspace writes. Other unverified advisory
  profiles also skip; all seven coding-provider adapters remain available.
- Native Windows CI and actual provider-version compatibility are not established
  by Linux or mocked tests. Check the PR's native Windows result separately.
- Automatic redaction is best effort. Owner-only POSIX file modes are not a claim
  that arbitrary Windows inherited ACLs were audited.
- Comparative quality, billed tokens and monetary savings remain unmeasured. The
  research document contains a matched-task experiment protocol, not a result.
- These changes have not been published to npm or merged into main.
