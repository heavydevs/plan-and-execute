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
- skill/plan-and-execute/scripts/preplanctl.py d87f06249f12b68dca2a7ed3abf0018bcb79592a1ed20ca9ccfcee22eb2cd6d0
- skill/plan-and-execute/scripts/preplan_self_test.py ad5b87cc461c9365cc4954f301f92ea8f4e53e9e55b4cd5f3c534f2ad83f83a6
- test/optimization/primary_planning_self_test.py 53ff68a506d6fd899eab4970e0265f276cb4b1b721114e6df5e673233ce2523e
- skill/plan-and-execute/references/PRIMARY_PLANNING.md 4762e4fd5c88162bd9501f1ca0892ca6142e6bd22c09521643e50c4db72f904c
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md 73c9e90bbe1f90fbcadeca57cc2737d04e8f7b91dcb8d4df3ea18cba2b25fd12
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-1.json be51ccc66bb67dca0af33baafe1efe1f3676574813ac8e920869de13a8ff6d73
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-2.json ab0d1dadc74cb14f7d969e73c7a8243c19ff5d69a24666dda6428e129a956176
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-3.json e25890d02b3100b540e94fb392cea4325bfc78910521382ec95947a65c12b0e8
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-4.json 37828bf08d8a6aa332df4c8f02b67e73858e2f225c32e15ce0be72d697a6223f

Changed files named by the 008 receipt:
- skill/plan-and-execute/scripts/preplanctl.py
- skill/plan-and-execute/scripts/preplan_self_test.py
- test/optimization/primary_planning_self_test.py
- skill/plan-and-execute/references/PRIMARY_PLANNING.md
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md

Additional focus from the review worker:
Re-review of task 009 after dispatch 4 (findings-4.json, R4-01 high). Earlier rounds are in findings-1..3.json. Verify against the current code:
- R4-01: EXPLICIT_OBLIGATION_ID_RE consumes hierarchical ids whole (REQ-7.1, FR-1.2.3, REQ-007-A); EXTRACTION_VERSION is bumped to ooxml-text-v4. An explicit id shared by several clauses (duplicate_explicit_ids or repeated in the given obligations) is ambiguous: the audit, validate-digest's batch audit and covered_obligation_ids accept only the canonical_id or a text match for it. Missing-reason keys fall back to the canonical id.
- R4-02: _substantive also accepts 4+ letters in CJK/Thai scripts; the reason text says so.
- R4-03: validate_digest requires new contradiction ids to start with '<digest_id>-' and be unique within the digest. The all_digests uniqueness check remains as a backstop.
- R4-04: the zero-obligation floor gate keys on non-empty fragments, and verify_source_derivation re-derives block_count.
- R4-06: the docs also warn about tracked moves.
Each fix should have a test that fails when it is reverted. Look for false rejections of valid packages, remaining coverage bypasses (especially one item covering several obligations), and doc claims beyond the code. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect.
