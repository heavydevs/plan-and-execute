You are a fresh, independent, read-only code reviewer (maximum tier) for review task 005.
Rules: read the reviewed inputs below and only the code they reference; never modify a file; never run review_dispatch.py, a provider CLI or a write command; never launch background or asynchronous agents or tasks; finish the whole review in this session and return only the JSON object required by the schema.
Assignment: review the actual implementation delivered by task 004 (Implement shared acceptance fixtures and report-aware task inputs) against its acceptance criteria and the review checkpoints. Report concrete defects with `path:line`. Use critical/high only for a broken acceptance criterion, correctness, security or data-integrity defect. Verdict "approved" only when no critical or high finding remains.

Review task 005: Review and correct shared acceptance fixtures
Objective: Independently review task004 and correct fixture or context-selection defects before its acceptance.

Review task checkpoints (the review worker performs them after your review; context only):
- S001 Read assigned decision and pin baseline: Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md. Confirm source applicability; do not repeat broad research.
- S003 Implement change 2: Correct every blocking finding or leave the gate incomplete with a recorded reason.
- S004 Implement change 3: Re-run declared checks after corrections and pin the final reviewed source state.
- S005 Run declared regression checks: Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- S006 Record acceptance evidence: Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

Review task acceptance:
- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 004 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

Implementation task 004 acceptance:
- One shared fake-provider fixture covers claude/codex/antigravity argv with success, quota, auth and functional outcomes and starts no subprocess or network call.
- The report-aware loader returns only the entry's prepared_reports/input_contract paths and rejects unlisted reports and the task's own not-yet-created files.
- A credit-exhaustion fixture is classified as availability, distinct from auth and functional failures.
- Offline contract tests pass with no model call or user-global configuration write.
- Actual code changes and acceptance evidence are recorded.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

Reviewed inputs (path sha256):
- docs/research/20261028-skill-optimization/implementation/004-receipt.json 58054376ff54b60196d13cb8cd60ef59268274c5f0ece9e2389cf03b1f82eb39
- docs/research/20261028-skill-optimization/implementation/004-outcome.md 910d9942841e5a66535febc0a9d7d079b1099cf9805b4d0eb79d142785b9ea56
- test/optimization/shared_fixtures.py f14fbad1e9297364f5205b476bd3e23f5f4d6b631f65e97ecac0efadfcc72f69
- test/optimization/task_004_self_test.py efce2bf53df89d9e916c869ea1f3bc596c0d7e18259c90fdd88b9a0a68d2dd7f

Changed files named by the 004 receipt:
- test/optimization/shared_fixtures.py
- test/optimization/task_004_self_test.py

Prepared decision (background only; read if a finding needs it):
- docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md

Additional focus from the review worker:
This is the second re-review after corrections. Dispatch 2 of this task (docs/research/20261028-skill-optimization/implementation/reviews/005/findings-2.json) approved with findings R2-F1..R2-F8 and none blocking. The 005 worker changed both reviewed source files again:
- R2-F1: tests use addCleanup instead of TestCase.enterContext. offline_guard now patches pathlib.Path.open (write modes), write_text/write_bytes/mkdir/touch/replace/rename/unlink/rmdir/symlink_to directly, so it does not depend on Python 3.10's path accessor.
- R2-F3/F4: the loader rejects non-canonical or unsafe paths in every listed and requested path. It wraps _safe_local/_load_json PreflightError as ReportAwareInputError, requires schema_version 2, rejects a duplicated task id and matches own files case-insensitively.
- R2-F5: the guard also forbids os.open with write flags, os.remove/unlink/rmdir/symlink/system/spawn*/exec*/startfile and shutil.rmtree. The production-builder setup of the parity test runs with user dirs redirected and checked empty. Temp catalogs are still written before the guard as setup.
- R2-F6/F7/F8: classify_outcome maps every availability.unavailable event to "availability" and "configuration" to its own label, with a test covering each value availability.classify can return. AC03 asserts that the (classification, category) pairs differ. Docstrings now state the argv parity limits.
The worker's local results: 9 tests pass on Python 3.11, 3.12 and 3.13 (no 3.10 interpreter on this host). Each new check fails under a deliberate mutation of the code it guards. R2-F2 (no test log for the final hashes yet) is handled after this review by the declared resource_watch run and the 005 receipt; 004-outcome.md stays outside the 005 write scope.
Verify that these corrections are correct and complete, and look for regressions or new defects they introduced. Judge the current files on their merits; do not just confirm this note.
