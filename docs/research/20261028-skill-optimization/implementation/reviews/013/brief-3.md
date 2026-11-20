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
- skill/plan-and-execute/scripts/planctl.py 331cbf4178071151a0073b3543deb9a13bc3271e23f5f95dbf82bd368502d0e2
- skill/plan-and-execute/scripts/artifact_contract.py 20492b6e95f6346cb545c9d94acb56d746a307ac74deb89322230f98d852a812
- test/optimization/plan_contract_self_test.py f9c2c45af8252783908542fde6a164252e5c0426ad095d91627e528ee2908612
- skill/plan-and-execute/references/PLAN_SPEC.md 2d0585cf9770bcecdf56b47707a30db323caf964b930196f445fefa4f4cb6d70
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
Correction review (dispatch 3). Dispatch 2 (reviews/013/findings-2.json) approved the earlier corrections with medium/low findings N01-N06; the pinned files changed again to address them. Verify each disposition against the current code, look for regressions, and judge the code rather than this note.
- N01: revise now carries forward every top-level manifest key the spec does not own (SPEC_OWNED_MANIFEST_KEYS), e.g. study_gate; spec-owned keys dropped from the spec stay dropped. Tier/effort reclassification is NOT preserved; PLAN_SPEC.md tells planners to restate it in the revised spec. Test: test_r08.
- N02: complete_task always recomputes contract digests before building the receipt, so out-of-band contract edits no longer block completion. Test: test_r08.
- N03: receipt `validations` now come from the runner's validation_results; worker-reported failed checks are recorded as worker_reported_failed_validations and do not refuse completion. Test: test_r08.
- N04: the lock loop checks the deadline and sleeps when a takeover did not remove the lock (busy guard or undeletable lock) and raises a distinct PlanError; a stale guard is removed by rename-and-verify with a per-guard token; the guard is released only if it is still ours. Test: test_r04 (busy guard, stale guard, Windows undeletable lock).
- N05: only flag-bound digests (scoped_input_digests_source=revise_flag) are carried forward; omitting spec-bound digests unbinds them. Test: test_r06.
- N06: docs now say revisions[] / plan_revised. The live .ai-work plan is not migrated by this task (plan artifacts are outside its write scope; a runner is active) - recorded as a follow-up.
