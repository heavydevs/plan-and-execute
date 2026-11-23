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
- skill/plan-and-execute/scripts/planctl.py fe4ab8aeeb0119c27b7effb05246f38c8c5d75c7f0be19b95079769492e9d679
- skill/plan-and-execute/scripts/artifact_contract.py b8d2e529ebe6d3f6ca328dad0890860f313a1f093de097afe870dd4d028a87cb
- skill/plan-and-execute/scripts/runner_contract.py 039a64617751ff5eff07466253082c094c89a79748d9e3ebc56c8f85a9e8ada1
- test/optimization/context_learning_self_test.py 6d9e3581f9d119be6c6ff75020b05abac7afe7c52ecd89a0b895bcb09a0234ca
- skill/plan-and-execute/references/EXECUTION_CONTEXT.md 957822534752366a04445bfdb2cd503295acb7d68511d62bd8b17c4e64d333e8
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md 2f7107c3e620e1629e4fddeab4247ee43bc215acc0b03c61683966d717a9ad08
- skill/plan-and-execute/scripts/run_isolated.py 5798eb94183b4b4b80391492ce4da0794258c6fdad446c85335bc4a70113ea22
- skill/plan-and-execute/scripts/pattern_runner_contract.py bb5a8032f8c9154efd9eed165bbdc63f1d258be545da321d7ffaeda7cee20d2e

Changed files named by the 014 receipt:
- skill/plan-and-execute/scripts/planctl.py
- skill/plan-and-execute/scripts/artifact_contract.py
- skill/plan-and-execute/scripts/runner_contract.py
- test/optimization/context_learning_self_test.py
- skill/plan-and-execute/references/EXECUTION_CONTEXT.md
- skill/plan-and-execute/references/TOKEN_EFFICIENCY.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md
