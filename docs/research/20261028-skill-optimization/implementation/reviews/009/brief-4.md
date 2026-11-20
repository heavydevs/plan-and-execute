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
- skill/plan-and-execute/scripts/preplanctl.py cfeb425887cbf7285ceeebe4b8a5f747aab377685737113fe28a96f50552d16a
- skill/plan-and-execute/scripts/preplan_self_test.py ad5b87cc461c9365cc4954f301f92ea8f4e53e9e55b4cd5f3c534f2ad83f83a6
- test/optimization/primary_planning_self_test.py dca2f5f949216ab5471b8508826665122469bc1c6bd05aad0baaf9ad67c2da0b
- skill/plan-and-execute/references/PRIMARY_PLANNING.md b6b308d5f05b798f695de1b03a9235f73f0f93245edeb077c9353febc58dc402
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md dfc0c189e101949f5e3602fe1c301a7c050cab23b4307f5397bb2dadbd509540
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-1.json be51ccc66bb67dca0af33baafe1efe1f3676574813ac8e920869de13a8ff6d73
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-2.json ab0d1dadc74cb14f7d969e73c7a8243c19ff5d69a24666dda6428e129a956176
- docs/research/20261028-skill-optimization/implementation/reviews/009/findings-3.json e25890d02b3100b540e94fb392cea4325bfc78910521382ec95947a65c12b0e8

Changed files named by the 008 receipt:
- skill/plan-and-execute/scripts/preplanctl.py
- skill/plan-and-execute/scripts/preplan_self_test.py
- test/optimization/primary_planning_self_test.py
- skill/plan-and-execute/references/PRIMARY_PLANNING.md
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md

Additional focus from the review worker:
Final re-review of task 009 corrections (round 3). Dispatches 1-3 are in findings-1/2/3.json; dispatches 2 and 3 already approved. Dispatch 3's R3 findings are now addressed as follows. Verify against the current code:
- R3-01/R3-02: the id-match rule now needs a restatement (3+ letter words besides ids, any language) instead of the English content-word overlap, so translated digests pass. Bare RULE-/CLAUSE-/R###/OBL- echoes fail. Audit errors give a reason per id (fragment not cited, id without restatement, no id/text). Digest guidance states the rule.
- R3-04: zero extracted obligations requires COVERAGE_REVIEW acknowledged_obligation_floor. The heuristic's scope (English modals, fixed id prefixes) is documented.
- R3-05: worker contradiction ids must be unique across digests (SOURCE_INDEX ids exempt). Guidance asks for D00N-C# ids.
- R3-06: acknowledgements need string kind/location and count one per recorded entry.
- R3-07: DrawingML a:t is counted as text, and the --require-source CLI exit path has tests.
- R3-03: documented only. Inline tracked insertions stay excluded, as the prepared decision asks for them to be recorded as limitations. Docs warn about inverted polarity and require reviewers to check previews.
Look for false rejections of valid packages, new bypasses, and doc claims beyond the code. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect.
