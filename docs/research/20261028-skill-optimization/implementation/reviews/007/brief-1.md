You are a fresh, independent, read-only code reviewer (maximum tier) for review task 007.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task 006 (Implement selective activation, intake and late promotion) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task 007: Review and correct selective activation, intake and late promotion
Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

Review task checkpoints (the review worker performs them after your review; context only):
- S001 Read assigned decision and pin baseline: Read docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md. Confirm source applicability; do not repeat broad research.
- S003 Implement change 2: Correct every blocking finding or leave the gate incomplete with a recorded reason.
- S004 Implement change 3: Re-run declared checks after corrections and pin the final reviewed source state.
- S005 Run declared regression checks: Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- S006 Record acceptance evidence: Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

Review task acceptance:
- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 006 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

Implementation task 006 acceptance:
- A one-module feature touching seven files remains DIRECT and leaves no plan artifacts.
- A short security-sensitive fix remains direct when cohesive, but its model floor is not lowered.
- A promoted task includes only remaining outcomes and preserves the original worktree.
- Entrypoint bytes and offline false-positive/false-negative rates on held-out routing-evals.json are measured against baseline; live host loading/latency needs owner-confirmed authenticated runs, else a recorded limitation.
- A near-finished high-context task stays DIRECT without creating control files.
- A tiny security-sensitive edit can select a strong worker without forcing an orchestration plan.
- Promotion preserves changed files and validated outcomes and schedules only remaining work.
- Prepared research is not proof of implementation or independent-review completion.

Reviewed inputs (path sha256):
- docs/research/20261028-skill-optimization/implementation/006-receipt.json e8a89fdc43b52a6f342e5e5d232ed1f06d2392e1a5d4287ce54bd9218709a997
- docs/research/20261028-skill-optimization/implementation/006-outcome.md 34608cb3ce1da1e23b14f9630aaf48b51addfb72dc63485873665d4c8d86c5dc
- skill/plan-and-execute/scripts/requestctl.py 352e7b14d1c71e975b5b76f670fd4f67dc2b1a844f07ca5954449514e6db2c2d
- skill/plan-and-execute/scripts/promotectl.py 2e2ecf7a48d821a721054abde4be62fb03c9ccdf5b597a47414cc754e1bf85e6
- skill/plan-and-execute/scripts/routing_self_test.py f48275119a832bf81c66663487f083e2e2139a34fc17536e3c854c8198d4fa5e
- test/optimization/activation_intake_self_test.py b217de6e29dbad80760eab4f32b14107ed828577022ab7580d3e0b63c3552bcf
- skill/plan-and-execute/SKILL.md cda3a0bcc6e28543de3b59bec29f85b8bccdddda411f72622fc6566bf6f228d8
- skill/plan-and-execute/references/ROUTING.md dca5fa50fd29da949f34ca203619b07f1c23bc463ea2fc069e86109dc84219a4
- skill/plan-and-execute/references/PROMOTION.md d2cc14e241893fc4e29379bd42941aeacc435a0057807e8623d342851ca5cda0
- skill/plan-and-execute/references/routing-evals.json 11a00b284ad45c632bd7f87ea1920ff4df04d2e4dfc71ffffa1c9e58b679a604
- skill/plan-and-execute/agents/openai.yaml e60055f3d6bb5b39aa4f310591b4efe2b4d52fbdb7d31b57c1d6bae39b7475e0

Changed files named by the 006 receipt:
- skill/plan-and-execute/scripts/requestctl.py
- skill/plan-and-execute/scripts/promotectl.py
- skill/plan-and-execute/scripts/routing_self_test.py
- test/optimization/activation_intake_self_test.py
- skill/plan-and-execute/SKILL.md
- skill/plan-and-execute/references/ROUTING.md
- skill/plan-and-execute/references/PROMOTION.md
- skill/plan-and-execute/references/routing-evals.json
- skill/plan-and-execute/agents/openai.yaml

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/006-activation-intake.md

Additional focus from the review worker:
- Check the revision-2 alternatives (no orchestration / explicit-only / selective metadata / paid classifier), the scope boundary and the negative (near-miss) tests against the actual changed code, not against the outcome text.
- Report unsupported cost/quality claims in 006-outcome.md (e.g. FP/FN/E[C] numbers that the corpus or code does not actually compute, or held-out cases that are not actually held out from tuning).
- Verify that a rejected implicit match and exact lifecycle commands create no plan/ledger/study/reason-code files, and that promotion keeps worktree edits and schedules only remaining outcomes.
- Verify that routing mode is separated from capability tier (a short security-sensitive direct fix keeps its strong/high floor).
- SKILL.md now hashes differently from the 006 receipt (other later edits in the tree); confirm the 006 SKILL.md contract still holds in the current file.
- Check that tests would fail if the guarded behaviour regressed (no tautological assertions).
