You are a fresh, independent, read-only code reviewer (maximum tier) for review task 013.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task 012 (Implement requirements, task decomposition and schema-v4 state) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task 013: Review and correct requirements, task decomposition and schema-v4 state
Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

Review task checkpoints (the review worker performs them after your review; context only):
- S001 Read assigned decision and pin baseline: Read docs/research/20261028-skill-optimization/prepared-research/012-plan-contract.md. Confirm source applicability; do not repeat broad research.
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

Implementation task 012 acceptance:
- A failed revision leaves the previous manifest and task projections readable.
- Every requirement has a consumer; every implementation has explicit acceptance and validation.
- A transformed research task remains pending, with subtasks instructing implementation from its assigned report.
- Legacy schema1-3 files are not silently rewritten using schema4 projection rules.
- No active task creates a second plan or depends on a nonexistent research output.
- A crash after manifest replacement but before task rendering rebuilds consistent projections.
- A stale plan writer cannot replace a newer generation.
- Changing one task contract invalidates its dependent outputs, not unrelated completed tasks.
- Prepared research is not proof of implementation or independent-review completion.

Reviewed inputs (path sha256):
- docs/research/20261028-skill-optimization/implementation/012-receipt.json 2f787a86bd445d24c007d1a83b9dca8c2748b087710b04b8ca84221f5797ca49
- docs/research/20261028-skill-optimization/implementation/012-outcome.md 50528a0fcb9252d6451f632a49d175e3f09b734efda5d4471759a67762cf35e8
- skill/plan-and-execute/scripts/planctl.py 174830bac307b117fba5831e11e0ede268a52ae88bbb8cbfd13e7f5fa0924a7d
- skill/plan-and-execute/scripts/artifact_contract.py 20492b6e95f6346cb545c9d94acb56d746a307ac74deb89322230f98d852a812
- test/optimization/plan_contract_self_test.py 86a687abbc82e2dff9bce7cd7ff71c32f79436ce884e4a82761eb4de3fc220f5
- skill/plan-and-execute/references/PLAN_SPEC.md 97075ae9b7f15f5fc05d273c4df12d424596083afcad75816917e548a128fb82
- skill/plan-and-execute/references/PLANNING_PROTOCOL.md 0682cdd82149f8fbb65a6c3437b2048856d9549a453a3ee6a5f7eaf2623dd190

Changed files named by the 012 receipt:
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/artifact_contract.py
- test/optimization/plan_contract_self_test.py
- skill/plan-and-execute/references/PLAN_SPEC.md
- skill/plan-and-execute/references/PLANNING_PROTOCOL.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/012-plan-contract.md

Additional focus from the review worker:
Correction review (dispatch 4). Dispatch 3 (reviews/013/findings-3.json) approved with medium F01/F02 and low F03-F08; the pinned files changed again. Verify against the current code, look for regressions, judge the code rather than this note.
- Dispatch-3 F01: complete_task computes digests locally and refreshes only the completing task's stored contract_digest; other tasks keep stored digests, so revise still sees their out-of-band edits. Test: test_r09.
- Dispatch-3 F02: complete_task now builds and validates the receipt before reconcile_reported_subtasks and materialize_learning_artifacts. Test: test_r09 (rejected completion leaves no learning file/entry and no subtask change).
- Dispatch-3 F03: save_manifest restores the caller's generation if the manifest write raises. Test: test_r09.
- F04-F08 are not changed in code and will be recorded as limitations/follow-ups: narrow double-fault guard races and hard-link-less filesystems; unmarked flag digests from pre-013 code (no live impact); CLI `complete` has no runner validation evidence; studyctl direct manifest write (outside write scope); 012 receipt hashes are superseded by the 013 receipt.
