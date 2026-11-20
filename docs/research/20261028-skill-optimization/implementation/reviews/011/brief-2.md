You are a fresh, independent, read-only code reviewer (maximum tier) for review task 011.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task 010 (Implement adaptive internal and external study) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task 011: Review and correct adaptive internal and external study
Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

Review task checkpoints (the review worker performs them after your review; context only):
- S001 Read assigned decision and pin baseline: Read docs/research/20261028-skill-optimization/prepared-research/010-adaptive-study.md. Confirm source applicability; do not repeat broad research.
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

Implementation task 010 acceptance:
- A source with no date/version is flagged for refresh when it affects CLI behavior.
- Two tasks sharing the same source retain different applicability notes without copying an entire article.
- A contradictory provider document yields a probe requirement, not an invented resolution.
- Known prepared reports are consumed without requiring another broad research phase.
- A source that was only located cannot satisfy a verified-interface claim.
- An API pricing record cannot silently substitute for subscription-quota evidence.
- A provider-version change invalidates only affected recommendations, not all 32 reports.
- Prepared research is not proof of implementation or independent-review completion.

Reviewed inputs (path sha256):
- docs/research/20261028-skill-optimization/implementation/010-receipt.json 31eb3655184acae09d34b51e3cd75ca43e1d02863d827e99363d6b986bd1441e
- docs/research/20261028-skill-optimization/implementation/010-outcome.md 92a6a0d216e1c26f36220ad1306a66e9ca75416336e3f2d1be038466d43b2f0a
- skill/plan-and-execute/scripts/studyctl.py dc4b944cf4fdd5fd6be6e26db205f502a81f57c299e666359246ce3087c76ef5
- skill/plan-and-execute/scripts/study_self_test.py d0e6c32dd7ed32a4c7e8051613f4e1e1a814d0024296d805e7e74b6d411c4664
- test/optimization/adaptive_study_self_test.py 7121f82b8ecfb7493c50eb7fa233b2c30d0403baaaaacb4f905d93ed0b8ca7d2
- skill/plan-and-execute/references/ADAPTIVE_STUDY.md a345f36320cd861d0dba62f8397cbaf9404d2f0373aa2c37ff1bcc2f09b9addd

Changed files named by the 010 receipt:
- skill/plan-and-execute/scripts/studyctl.py
- skill/plan-and-execute/scripts/study_self_test.py
- test/optimization/adaptive_study_self_test.py
- skill/plan-and-execute/references/ADAPTIVE_STUDY.md

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/010-adaptive-study.md

Additional focus from the review worker:
Second dispatch after corrections by review worker 011. The four files named by the 010 receipt changed since dispatch-1 (see current hashes above). Verify the code directly; do not trust this note.
Changes claimed (verify each, and look for regressions they introduce):
- studyctl.py normalize_recommendations: guard status now derives from the recommendation's own claim_type (only capability_probe uses probe_required).
- studyctl.py resolve_source_dating (used by normalize_external_sources and deduplicate_source_register): an undated/placeholder version_or_date is rejected unless affects_cli_behavior is declared or evidence_domain is cli_interface.
- studyctl.py normalize_questions/validate_ready_state/evaluate_stopping_condition: contradicted questions cannot be resolved/assumed without probe_verified; probe_verified needs a capability_probe plus a cited internal or observed_repository_behavior source; high-impact resolved questions need an internal or inspected citation; verified_source_fact rejected for abstract_only.
- Quota evidence must be an inspected subscription_quota/account_capability source; prepared-report waiver excludes security_sensitive/conflicting_evidence and requires source_ids; evidence_origin enumerated and prepared-research paths forced to prepared_research; receipts must be separate relative .json paths; research_revision/version_sensitive type-checked; invalidation signals need targets, report unmatched_signals, extend report-only matching, and attribute only targeted sources.
- New regression tests in study_self_test.py and test/optimization/adaptive_study_self_test.py; ADAPTIVE_STUDY.md documents the rules.
Not changed (deferred, non-blocking): free-text length budgets beyond source summaries (F11), internal-source kind restriction for verified_interface (F12), per-product version matching in provider_version_change (F09 second half), existence/hash checks of prepared-report and receipt files (the delivery gate verifies receipts).
