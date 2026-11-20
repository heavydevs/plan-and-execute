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
- skill/plan-and-execute/scripts/planctl.py 66c7d32ddd2d7a1e27a6d59f2a2414b68937ed3fc49bed202e6e99c25b507107
- skill/plan-and-execute/scripts/artifact_contract.py 20492b6e95f6346cb545c9d94acb56d746a307ac74deb89322230f98d852a812
- test/optimization/plan_contract_self_test.py 6ab29262966483073ee80af2f7f85870a3fa91f80ec6bd0eb8e0ddf821f90f76
- skill/plan-and-execute/references/PLAN_SPEC.md 6a324db171305213780abec32ad4784b85f523f9b5fcbf0acad39483a8d981e8
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
Correction review (dispatch 2). The files pinned above were changed by review task 013 after dispatch 1 (docs/research/20261028-skill-optimization/implementation/reviews/013/findings-1.json). Verify each disposition against the current code, look for regressions the corrections introduced, and report anything still broken. Judge the code, not this note.
- F01 (high): validate_receipt now rejects an explicit pending/non-approved verdict always, and a missing verdict only with require_review_verdict=True (CLI --require-review-verdict); build_task_receipt records independent_review_gate=declared_validation_commands. Test: test_r01 completes a review_of/requires_independent_review task with a schema-only report.
- F02 (high): revise_plan raises without expected_generation (0 for a manifest without a counter); CLI --expected-generation is required. Test: test_r02.
- F03: recover_projections upgrades a schema-4 manifest lacking generation (event generation_initialized); save_manifest deliberately does not auto-migrate (a live plan is not rewritten by a routine checkpoint). Docs state the gap. Test: test_r03.
- F04: plan_writer_lock re-entrancy is per thread; stale takeover runs under an O_EXCL .takeover guard and removes only the inspected content; live same-host owners are not stolen by age; PID reuse detected by a process-start token; ERROR_ACCESS_DENIED counts as alive; non-dict JSON handled; release never raises and only removes its own lock. Test: test_r04 (4-process contention on a dead-owner lock).
- F05: complete_task hashes declared scoped inputs on disk (LF-pin tolerant) and rejects drift; validate-receipt re-hashes by default. Test: test_r05.
- F06: revise carries forward scoped_input_digests not restated by spec or flag (revision record carried_scoped_input_digests). Test: test_r06.
- F07: _before_authority_publish hook; recover compares task statuses on disk; tests inject a staged-audit failure after staged projections exist and kill a revision process (os._exit) before publication. Test: test_r07. (The 012 outcome text is a prior-task artifact and is not edited.)
- F08: artifact_contract complete/reset fold summary fields into the single locked save, restoring them on failure.
- F09: docs corrected (create publishes by directory rename, not under the lock); lag detection stays generation-only because studyctl writes manifest.json directly (documented), and bump_generation=False saves only happen inside create_plan before the plan is handed out.
- F10: recover cleans .staging-<plan-id>-* create leftovers; MODEL_MATRIX rebinding on revise is left out of scope.
- F11: second-plan pattern widened; scoped_inputs existence is not enforced at plan time (they can be prerequisite outputs of dependencies); learning edges are not added to contract_digest (it would invalidate every existing receipt) - documented.
