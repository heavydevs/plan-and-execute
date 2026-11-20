You are a fresh, independent, read-only code reviewer (maximum tier) for review task 015.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task 014 (Implement assigned context, learned facts and token budgets) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task 015: Review and correct assigned context, learned facts and token budgets
Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

Review task checkpoints (the review worker performs them after your review; context only):
- S001 Read assigned decision and pin baseline: Read docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md. Confirm source applicability; do not repeat broad research.
- S003 Implement change 2: Correct every blocking finding or leave the gate incomplete with a recorded reason.
- S004 Implement change 3: Re-run declared checks after corrections and pin the final reviewed source state.
- S005 Run declared regression checks: Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- S006 Record acceptance evidence: Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

Review task acceptance:
- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 014 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

Implementation task 014 acceptance:
- An unrelated task cannot receive a learning merely because it ran later.
- Changing a cited file invalidates or flags the learning before reuse.
- A malicious or unsupported note cannot alter acceptance, permissions or provider policy.
- The universal context contains only constraints needed by all tasks and remains within its existing budget.
- Prefix stability is owned by 028; 014 changes do not regress the existing byte-stable prefix fixtures.
- A disproven hypothesis never appears as a validated shared fact.
- A source-contract change invalidates its learning without deleting unrelated knowledge.
- The static prefix remains stable while task-specific reports are loaded only for their assigned consumers.
- Prepared research is not proof of implementation or independent-review completion.

Reviewed inputs (path sha256):
- docs/research/20261028-skill-optimization/implementation/014-receipt.json 00b767422b92f8cc2d632826a81bbcf922c37a7a685baa7b50628c801e35f730
- docs/research/20261028-skill-optimization/implementation/014-outcome.md 75c96fd543c1144994a434d8c2a4d9ea78eb68ae7a54ef3aca48ab3202e168aa
- skill/plan-and-execute/scripts/planctl.py f1d94c4704178c102d99beddc25103ef5e37346e755556f8c7068c623375a417
- skill/plan-and-execute/scripts/artifact_contract.py 8e2ce4925ec75cfaadd23bca78aad71e4df545f9f6139281f2129af4993eb4b1
- skill/plan-and-execute/scripts/runner_contract.py b825e5d593882c05e5c723e7af632a18123253a62a3918d30e70f56dc3516a4d
- test/optimization/context_learning_self_test.py 34657a6de109f3ea7776e137e9edecdace1c49b8baa4302758ad3b61c1d8e716
- skill/plan-and-execute/references/EXECUTION_CONTEXT.md 5eb6f9d3c4a2a57a090d0b7b846af1172df4bd2a6ca289ab7fc6c1258fd5d266
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md 1458a8abced3713d95da974dec6b68e8a7ed6a4a6810ba99f5b2e7c0e05f6f59

Changed files named by the 014 receipt:
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/artifact_contract.py
- skill/plan-and-execute/scripts/runner_contract.py
- test/optimization/context_learning_self_test.py
- skill/plan-and-execute/references/EXECUTION_CONTEXT.md
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md
