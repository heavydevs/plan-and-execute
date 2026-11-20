# 005 Review and Correction Outcome — Shared Acceptance Fixtures

## Summary

Task 005 independently reviewed task 004 (shared fake-provider fixtures and the report-aware task input loader). It corrected every review finding the reviewer could fix in the declared write scope across two rounds and re-reviewed the corrected files. The final dispatch (3) **approved** the review with **0 critical/high** findings. The declared check passes on the final reviewed hashes (`Ran 9 tests ... OK`). Remaining low/info findings are recorded below as deferred follow-ups.

## Independent review (actual dispatches)

All reviews ran through `docs/plans/20261028-skill-optimization/support/review_dispatch.py` in the foreground. Each was read-only (Claude `--permission-mode plan --tools Read,Grep,Glob`) and used a fresh session at the max tier. The Codex max route (`gpt-6.2-sol`) was unavailable for quota on each attempt, so the helper recorded the cooldown and used Claude. No frontier model was used.

| Dispatch | Reviewer | Session | Reviewed source hashes (fixtures / tests) | Verdict | Findings (blocking) | Reported usd |
|---|---|---|---|---|---|---|
| `reviews/005/dispatch-1.json` | claude / claude-opus-5-5 / xhigh | `85a08a33-7df2-4a8b-a287-a50826af6446` | `1486a8e8…` / `1c72c3c7…` (task 004 delivery) | approved | 6 (0) | 0.94 |
| `reviews/005/dispatch-2.json` | claude / claude-opus-5-5 / xhigh | `9666cc8f-2531-4503-903a-eec8dac2a306` | `17e9c158…` / `fd756886…` (round-1 corrections) | approved | 8 (0) | 1.60 |
| `reviews/005/dispatch-3.json` (final; receipt reviewer) | claude / claude-opus-5-5 / xhigh | `402b84ec-5447-4c55-bcbd-b7c882ebf6e5` | `f14fbad1…` / `efce2bf5…` (final) | approved | 6 (0) | 1.37 |

The final reviewed inputs equal the final source files. `test/optimization/shared_fixtures.py` is `f14fbad1e9297364f5205b476bd3e23f5f4d6b631f65e97ecac0efadfcc72f69` and `test/optimization/task_004_self_test.py` is `efce2bf53df89d9e916c869ea1f3bc596c0d7e18259c90fdd88b9a0a68d2dd7f`. The unchanged 004 receipt (`58054376…`) and outcome (`910d9942…`) were also reviewed.

## Changed files

- `test/optimization/shared_fixtures.py`
  - Loader (F1, F2, F4, R2-F3, R2-F4):
    - It validates the catalog: `schema_version` must be 2, the task list must exist, the task id must be unique, the fields must be lists and availability must be one of `existing_baseline_or_current_file`, `prerequisite_output` or `create_in_this_task`.
    - Every listed and requested path must be canonical POSIX and repository-safe. Errors from `_safe_local` and `_load_json` are wrapped as `ReportAwareInputError`.
    - A task's own `create_in_this_task` file is rejected fail-closed (`OwnTaskFileError`), with case-insensitive matching, whether it is requested or the entry also lists it as a prepared report or readable input. This holds for default and explicit loads and also after the file exists.
    - Unlisted requests raise `UnlistedInputError`.
  - Classification (F6, R2-F6, R2-F7): the label comes from `availability.classify` via `classify_outcome`:
    - `success` for exit 0;
    - `availability` for every event that `availability.unavailable` accepts;
    - `configuration` for configuration errors;
    - `functional` otherwise.
  - The module adds its own directory to `sys.path`, so it can be imported from other directories (F6).
  - Docstrings state the limits of argv parity (R2-F8).
- `test/optimization/task_004_self_test.py`
  - The 3 original tests were kept and the suite grew to 9.
  - Every fixture call runs inside `offline_guard`. The guard forbids:
    - subprocesses, sockets and `os.system`/`spawn*`/`exec*`/`startfile`;
    - `open`/`io.open`/`Path.open` in write modes and `os.open` with write flags;
    - `os.replace`/`rename`/`mkdir`/`makedirs`/`remove`/`unlink`/`rmdir`/`symlink`, `shutil.rmtree`, and the `Path` write, delete and rename methods.

    It also redirects `HOME`/`USERPROFILE`/`APPDATA`/`LOCALAPPDATA`/`XDG_CONFIG_HOME`/`CLAUDE_CONFIG_DIR`/`CODEX_HOME` to a temp dir that must stay empty. Temporary catalogs and the production builder's codex schema file are written before the guard as setup, in temp dirs. The production builder runs with user dirs redirected and checked empty.
  - New tests:
    - argv parity with `run_isolated.build_worker_command` under `planctl.default_config()` (F3);
    - own-file overlap through temporary catalogs (F1/F2);
    - non-canonical and unsafe paths (R2-F3/R2-F4);
    - malformed catalogs: unknown availability, missing path, string reports, non-list contract, duplicate id, schema version, missing listed file (F4/R2-F4);
    - classifier coverage (R2-F6);
    - a non-vacuity probe of the guard (F5/R2-F5).
  - `TestCase.enterContext` (3.11+) was replaced by `addCleanup` (R2-F1).

## Validation (actual runs)

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_005`
  - `test_exit=0 health=healthy`
  - Log: `docs/research/20261028-skill-optimization/implementation/logs/005/20261120T073226-19016/check-01.log` (sha256 `8baded3a…`), which shows `Ran 9 tests in 0.465s` / `OK`.
  - Machine receipt: `005-checks.json`.
  - The first attempt stopped with `service_map_invalid` (stale source snapshot) because the two test inputs had changed. The checks and resources were unchanged, so the map was re-stamped with `service_map.py stamp --confirm-reconciled` and the validation was rerun.
- Supporting gate evidence (foreground; the repository was unchanged afterwards; output recorded here, no separate log file):
  - `python docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py`: `Ran 55 tests` / `OK (skipped=1)`. The skipped test is `test_symlink`: symlink creation is not permitted on this host. Passing tests include `test_fake_review_rejected`, `test_low_tier_review_rejected`, `test_reused_review_from_other_receipt_rejected`, `test_frontier_without_evidence_rejected`, `test_frontier_single_failure_rejected`, `test_frontier_for_quota_rejected`, `test_frontier_for_availability_class_rejected`, `test_frontier_reusing_failed_dispatch_rejected`, `test_frontier_wrong_model_rejected` and `test_valid_frontier_review`.
  - `python docs/plans/20261028-skill-optimization/support/review_dispatch_self_test.py`: `Ran 14 tests` / `OK (skipped=1)`. The skipped test is the opt-in live Haiku smoke test. Passing tests include `test_reused_session_is_refused` and `test_identical_inputs_reuse_existing_dispatch_without_spend`.
- Manual compatibility runs of `test/optimization/task_004_self_test.py` (not declared checks):
  - Python 3.12.13: 9 tests OK.
  - Python 3.13.15: 9 tests OK.
  - Python 3.10 was **not** run because no 3.10 interpreter is installed on this host.
- Manual mutation check (scratch script; the source was restored byte-identical each time):
  - 12 deliberate mutations were all caught. They covered: the default-load and requested own-file guards, casefold matching, the canonical-path check, wrapping of unsafe paths, duplicate ids, schema version, missing input, the configuration label, the `missing_cli` availability event, and two argv changes (dropping a codex flag, reordering claude model/effort).
  - The catalog-load error branches that R3-F4 names (missing or invalid catalog, non-dict catalog, non-list tasks, unknown id, non-list `requested_paths`) have **no** test.

## Acceptance coverage

| ID | Task 005 acceptance | Result | Evidence |
|---|---|---|---|
| AC01 | Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded | passed | `reviews/005/dispatch-3.json`, `findings-3.json`, the `reviewer`/`reviewed_inputs` fields of the receipt |
| AC02 | No unresolved critical/high finding; assigned acceptance cases have actual test evidence | passed | `findings-1/2/3.json` (0 blocking in each), `005-checks.json`, `logs/005/20261120T073226-19016/check-01.log` |
| AC03 | A reused or fabricated review receipt is rejected | passed | `check_delivery.py` (`dispatch_record`, `used_dispatches`), `review_dispatch.py` refusals, the gate self-test runs above |
| AC04 | Frontier reviewer only with recorded repeated max-review failure; a reused review session or dispatch is rejected | passed | `check_delivery.py` (`frontier_failures`), the delivery-gate frontier tests above, the final reviewer is max tier (not frontier) with a distinct session per dispatch |
| AC05 | Every 2026-11-20 acceptance addition of task 004 has actual test evidence on the final reviewed hashes | passed | See the task 004 mapping below; log `logs/005/20261120T073226-19016/check-01.log` at `f14fbad1…`/`efce2bf5…` |

Task 004 acceptance mapped to tests at the final hashes:

- Shared fake-provider fixture (claude/codex/antigravity; success, quota, auth and functional outcomes; no subprocess or network): `test_ac01_shared_fake_provider_argv_and_outcomes_offline` and `test_ac01_fixture_argv_matches_production_worker_builder`.
- Report-aware loader that returns only the listed paths and rejects unlisted reports and own not-yet-created files: `test_ac02_report_aware_loader_bounds_and_rejections`, `test_ac02_own_file_overlap_rejected_for_default_and_requested_load`, `test_ac02_noncanonical_and_unsafe_paths_rejected` and `test_ac02_malformed_catalog_entries_rejected`.
- Credit exhaustion classified as availability and distinct from auth and functional failures: `test_ac03_credit_exhaustion_distinct_from_auth_and_functional` and `test_ac03_classification_covers_every_classifier_category`.
- Offline, with no model call or user-global configuration write: `offline_guard` around every fixture call, plus `test_ac04_offline_guard_detects_processes_sockets_and_writes`.

The prepared report `ARCHITECTURE_AND_SCOPE.md` (sha256 `300a1adc…`) is input evidence only. It is not proof that this implementation or its review passed.

## Findings disposition

- Dispatch 1:
  - Resolved: F1, F2, F3, F4 and F6.
  - F5: the test part was resolved (guard on every test, plus an AC04 probe). The overstated text in `004-outcome.md:14,20` is outside the 005 write scope and was **not** edited. The 004 receipt, outcome and `logs/004/.../check-01.log` describe only the superseded files (`1486a8e8…`/`1c72c3c7…`), and this receipt supersedes them for the final hashes.
- Dispatch 2:
  - Resolved: R2-F1, R2-F3, R2-F4, R2-F5, R2-F6, R2-F7 and R2-F8.
  - R2-F2 was addressed by the new 005 log and receipt.
- Dispatch 3 (final):
  - R3-F1 (medium) was addressed by this receipt and the new log at the reviewed hashes.
  - Deferred, non-blocking:
    - R3-F2 (low): exit codes 130/143/-2/-15 are labelled `functional`, while production treats them as an interruption.
    - R3-F3 (low): Windows aliases of own files other than letter case (trailing dot or space, 8.3 names, `::$DATA`).
    - R3-F4 (low): the catalog-load error branches listed above have no tests.
    - R3-F5 (info): `AVAILABILITY_EVENTS` copies the production event set by hand.
    - R3-F6 (info): further guard gaps (`os.link`, `os.truncate`, `chmod`/`utime`, `fork`, `posix_spawnp`, `_winapi.CreateProcess`) and missing probes for `Popen`, `socket.socket` and `os.unlink`.

## Limitations

- Offline contract tests only; no test runs a live provider CLI. The three review dispatches did call Claude Opus 5.5, as the plan requires, through the read-only review helper (reported usd ≈ 3.91 in total). Codex was unavailable for quota on each attempt.
- Python 3.10, the minimum version declared for CI, was not run. 3.10 compatibility rests on code inspection (no `enterContext`; `Path` methods patched at class level), and the final reviewer confirmed it by trace.
- The supporting gate self-test runs and the 3.12/3.13 and mutation runs are recorded only in this report, not as declared check logs.
- `.ai-work/SERVICE_MAP.md` was re-stamped by its helper after the reconciliation; no validation ID, check or resource changed.
