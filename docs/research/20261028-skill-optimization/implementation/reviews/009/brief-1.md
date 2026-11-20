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
- skill/plan-and-execute/scripts/preplanctl.py 5c15578441a0456adf8ef9e15aec30358e6950139977670c0c425dc1538af1fd
- skill/plan-and-execute/scripts/preplan_self_test.py 56bcf13402596f0a2143439a2a8afae7eefedb5f89be789c3037e90225d35b94
- test/optimization/primary_planning_self_test.py 868612ab8dd80f0c5cc4d8e135fa8695b29e45c50e200308ce4e42d1888bf1b3
- skill/plan-and-execute/references/PRIMARY_PLANNING.md 3a410e690e768881c7b86d30d5986ae4181677b00665cad3d66fca070bb27c64
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md 0a81afbe319dd468eeddc49766f897ed87e3b9d0694d78b9ca91211480413910

Changed files named by the 008 receipt:
- skill/plan-and-execute/scripts/preplanctl.py
- skill/plan-and-execute/scripts/preplan_self_test.py
- test/optimization/primary_planning_self_test.py
- skill/plan-and-execute/references/PRIMARY_PLANNING.md
- skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/008-primary-planning.md

Additional focus from the review worker:
- Check the revision-2 alternatives and scope boundary against the actual changed code: consumption-time integrity (raw source, block stream, fragment hashes re-verified at final consumption, not only preparation), ordered nested/merged OOXML table extraction with ZIP/XML bounds, unsupported-structure recording, obligation/contradiction coverage audit, routing-only deduplication.
- Check that negative tests really exercise the rejection paths (one-byte mutation, same-size rewrite with restored mtime, duplicate/missing/escaping fragment IDs, symlink/junction, table-only obligation removal, repeated blocks) and would fail if the guard were removed.
- Report any unsupported cost/quality/recall claim in the 008 outcome, receipt or reference docs (e.g. claims of measured savings or live comparisons not actually run).
- Look for bypasses: a package path that skips verify_fragments, a digest or coverage file whose obligations can be silently dropped, or an extraction path that can still loop/exhaust memory on hostile DOCX input.
