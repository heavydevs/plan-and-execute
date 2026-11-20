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
- skill/plan-and-execute/scripts/requestctl.py e276e152c9705a3541f7aaa27bf22171ac3186a2fabb9c3433949de21478873b
- skill/plan-and-execute/scripts/promotectl.py 148c5c547c6d01aa630e1b701136240646bf3852c3d4a0ae5cdd9a05003f7532
- skill/plan-and-execute/scripts/routing_self_test.py 092593be00fb927bd22b360949e6881111e9fcfeb5c755aa618626ea3f20a0f2
- test/optimization/activation_intake_self_test.py b88a4c133b5d5d2c59696cb3a4ba70e97316be73b5c23f0f1828f0f105ee9482
- skill/plan-and-execute/SKILL.md cda3a0bcc6e28543de3b59bec29f85b8bccdddda411f72622fc6566bf6f228d8
- skill/plan-and-execute/references/ROUTING.md de94299128fb54223fdcb960f8dd90846df70f76cb0c11a24a3aee1ac1e3b01f
- skill/plan-and-execute/references/PROMOTION.md 993f52344f5886b252a1cbe18d03e5e193f97317ab6ace19f608c9fc5d10c74c
- skill/plan-and-execute/references/routing-evals.json 86ed90a252a6a1168ced9a3eb53cd57d64a9f82fae44688d5936f2e82c79238b
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
This is review round 2. Round 1 (docs/research/20261028-skill-optimization/implementation/reviews/007/findings-1.json) found H1, H2, M1-M4, L1, L2 and I1 in the 006 code. The review worker has since corrected the files listed above. Verify each correction against the actual code and report any remaining or newly introduced defect:
- H1: the cue table is now `requestctl.ACTIVATION_CUES`, hashed by `cue_table_sha256()`. The old held-out cases moved to the tuning split. H001-H019 were written by a separate agent session from a route-definition brief, without access to the code, after the freeze. `held_out_protocol` records the hash, honest measured results and regression ceilings. Check whether the held-out claim is now honest, and whether the frozen-hash guard and the label-leak guard in routing_self_test.py are sound.
- H2: lifecycle commands are detected before explicit invocation, explicit invocation requires a sigil or a directive verb, and path mentions are excluded. O010 and D019 were relabeled `lifecycle`, and L001, L002 and D020 were added.
- M1: the tests run the `evaluate-route` CLI in a temporary repo with a recursive snapshot and assert on extracted prompt signals. `created_artifacts` and the unused `prompt` parameter were removed. `--spec` rejects unknown fields.
- M2: the metric is labeled as an offline cue-extractor proxy with four computed alternatives, the paid classifier is unmeasured and the E[C] cost terms are null.
- M3: risk signals are merged into the `capability_signals` overrides. M4: there is a single `near_finished_stays_direct` rule shared by requestctl and promotectl (only EXPLICIT_INVOCATION overrides it, with at most one remaining outcome), plus a cross-module agreement test.
- L1/L2: the transcript guard now covers every field and role-prefixed turns, and the test parses the handoff sections.
Also check that ROUTING.md and PROMOTION.md match the code, and that nothing else in the write scope regressed.
