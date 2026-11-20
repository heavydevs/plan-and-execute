You are a fresh, independent, read-only code reviewer (maximum tier) for review task 009.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task 008 (Implement oversized request fragmentation and prepared packages) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task 009: Review and correct oversized request fragmentation and prepared packages
Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

Review task checkpoints (the review worker performs them after your review; context only):
- S001 Read assigned decision and pin baseline: Read docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md. Confirm source applicability; do not repeat broad research.
- S003 Implement change 2: Correct every blocking finding or leave the gate incomplete with a recorded reason.
- S004 Implement change 3: Re-run declared checks after corrections and pin the final reviewed source state.
- S005 Run declared regression checks: Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- S006 Record acceptance evidence: Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

Review task acceptance:
- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

Implementation task 008 acceptance:
- Mutating one byte of a fragment after coverage approval invalidates the package.
- A DOCX fixture with requirements in paragraphs and table cells preserves all obligations in source order.
- Duplicates, missing IDs, contradictory clauses and symlinks are rejected or explicitly recorded.
- An interrupted batch resumes from validated digests without processing completed raw fragments again.
- Permuting a requirement between beginning, middle and end does not change final requirement coverage.
- A same-size fragment rewrite with unchanged timestamp is rejected.
- Nested and merged table cells produce ordered, nonduplicated source anchors.
- A requirement appearing only in a table cannot disappear from the final coverage map.
- Large repeated blocks change routing estimates without deletion from authoritative evidence.
- Prepared research is not proof of implementation or independent-review completion.

Reviewed inputs (path sha256):
- docs/research/20261028-skill-optimization/implementation/008-receipt.json c0d2e5e3b999e08da4692fd7619e6e9084f2796cc9d1d8f535613bea6013c4eb
- docs/research/20261028-skill-optimization/implementation/008-outcome.md bdb0ce5ebe1d1e548a41754abf1d9517055a0c23d538f898e32cd8b68b3fa968
- skill/plan-and-execute/scripts/preplanctl.py 5508543350cbdaf6469de63b4cae6d614b1987bc1ac2518630b594ece5a40491
- skill/plan-and-execute/scripts/preplan_self_test.py ad5b87cc461c9365cc4954f301f92ea8f4e53e9e55b4cd5f3c534f2ad83f83a6
- test/optimization/primary_planning_self_test.py 452ef96bc9335e1e876e6e94630dce6491275048aa0a33107fa32ee6f5f5376c
- skill/plan-and-execute/references/PRIMARY_PLANNING.md a2556304581184cabf878c8eb74305d87f9b55a2ecf84673e17d855606f5c83c
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md a2f769ae0ac7452fb13aee8cf93c5fa7377f89fc3b25eb2de8fb802e3a30fd4e
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-1.json be51ccc66bb67dca0af33baafe1efe1f3676574813ac8e920869de13a8ff6d73
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-2.json ab0d1dadc74cb14f7d969e73c7a8243c19ff5d69a24666dda6428e129a956176

Changed files named by the 008 receipt:
- skill/plan-and-execute/scripts/preplanctl.py
- skill/plan-and-execute/scripts/preplan_self_test.py
- test/optimization/primary_planning_self_test.py
- skill/plan-and-execute/references/PRIMARY_PLANNING.md
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md

Additional focus from the review worker:
Final re-review of task 009 corrections. Dispatch 1 (findings-1.json) found F01-F03 high; dispatch 2 (findings-2.json) approved them and raised R2-01..R2-08. The reviewed files now also contain the round-2 fixes. Verify against the current code:
- R2-01: Markdown table rows located by their raw line (_block_clauses locator), so a split table maps each row to one fragment.
- R2-02: acknowledged_unsupported_structures gate in validate_coverage, with review guidance.
- R2-03: id matches need a shared content word; partial substrings need >=60% of the obligation and the same polarity.
- R2-04: validate_digest audits obligations held only by its batch and requires fragment_hashes for v2.
- R2-05: digest contradictions need ids and are carried by identity only.
- R2-06: docs wording and DrawingML a:t.
- R2-07: --require-source / require_source, plus handoff guidance.
Each fix should have a regression test that fails when the fix is reverted.
Look for regressions: valid packages or digests that are now falsely rejected (e.g. the R2-03 content-word rule), and any remaining coverage bypass. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect.
Known and deferred: the extraction-side explicit_id is still the first id in a clause (fail-safe over-reporting). 008-outcome.md is outside task 009's write scope; the 009 receipt and outcome supersede its claims.
