# 013 — Review and correction outcome: requirements, task decomposition and schema-v4 state

Status: `completed`. Independent review of task `012`, corrections applied, four fresh max-tier review dispatches; the final dispatch approved the pinned source with no critical or high finding.

The prepared decision `012-plan-contract.md` (revision 2) and the `012` receipt are input evidence only. Acceptance below rests on the 013 test logs and the dispatch-4 review of the corrected source.

## Independent review

| Dispatch | Reviewer | Verdict | Blocking | Evidence |
|---|---|---|---|---|
| 1 | claude / claude-opus-5-5 / xhigh (codex skipped: quota cooldown) | changes_requested | 2 high | `reviews/013/dispatch-1.json`, `findings-1.json` |
| 2 | claude / claude-opus-5-5 / xhigh (codex: quota) | approved | 0 | `reviews/013/dispatch-2.json`, `findings-2.json` |
| 3 | claude / claude-opus-5-5 / xhigh (codex: quota) | approved | 0 | `reviews/013/dispatch-3.json`, `findings-3.json` |
| 4 (final, pinned in receipt) | claude / claude-opus-5-5 / xhigh (codex: quota) | approved | 0 | `reviews/013/dispatch-4.json`, `findings-4.json` |

Each dispatch is a fresh read-only session (`--permission-mode plan`, Read/Grep/Glob). Re-dispatches happened because a reviewed file changed. No frontier model was used.

## Corrections (all in the declared write scope)

| Finding | Severity | Disposition |
|---|---|---|
| D1-F01 review tasks could never complete through the runner (receipt required a verdict the completion schema cannot carry) | high | Fixed. `validate_receipt` rejects an explicit pending or non-approved verdict. A missing verdict fails only with `require_review_verdict` (`validate-receipt --require-review-verdict`). The receipt records `independent_review_gate: declared_validation_commands`. Test `test_r01`. |
| D1-F02 stale revise could replace a newer generation (generation check was opt-in) | high | Fixed. `revise_plan` and CLI `revise` require `expected_generation`, which is `0` for a manifest without a counter. Test `test_r02`. |
| D1-F03 pre-012 schema-4 manifests never got a generation | medium | Fixed via explicit migration. `recover-projections` (or the first `revise`) initialises generation 1 and records a `generation_initialized` event. `save_manifest` does not auto-migrate. Test `test_r03`. |
| D1-F04 writer-lock takeover race, age-based theft of live locks, Windows access-denied, non-dict JSON, release errors | medium | Fixed. Re-entrancy is now per thread. Takeover runs under a guarded O_EXCL and removes only the inspected content. A live same-host owner is never stolen by age. PID reuse is detected through a process-start token. `ERROR_ACCESS_DENIED` counts as alive. Release never raises. Test `test_r04`: 4-process contention, busy and stale guard, undeletable lock on Windows. |
| D1-F05 scoped inputs never hashed | medium | Fixed. Completion hashes the declared inputs on disk (an LF pin matches a CRLF checkout) and rejects drift. `validate-receipt` re-hashes by default. Test `test_r05`. |
| D1-F06 flag-bound digests lost on later revise | medium | Fixed. Flag-bound digests (`scoped_input_digests_source: revise_flag`) are carried forward. Spec-bound ones are unbound by omitting them (D2-N05). Test `test_r06`. |
| D1-F07 negative tests never reached the staged rollback | medium | Fixed. Added a `_before_authority_publish` hook. Tests inject a staged-audit failure after the staged projections exist, and kill a revise process (`os._exit`) before publication. Recovery compares task statuses on disk. Test `test_r07`. |
| D1-F08 complete/reset made two locked saves | low | Fixed in `artifact_contract.py`. The summary fields are now part of the single save and are restored if completion fails. |
| D1-F09 doc said create runs under the lock; lag detection is generation-only | low | Docs corrected. Lag detection stays generation-only because `studyctl` writes `manifest.json` directly (documented). |
| D1-F10 create-staging leftovers; MODEL_MATRIX not rebound on revise | low | Leftovers are cleaned by `recover-projections`. MODEL_MATRIX rebinding is out of scope (follow-up). |
| D1-F11 scoped-input existence, learning edges in digest, second-plan wording | low | The second-plan pattern is widened. Scoped inputs are not required to exist at plan time, because they may be prerequisite outputs. Learning edges are not added to the digest, because that would invalidate every existing receipt (documented). |
| D2-N01 revise dropped `study_gate` and tier reclassifications | medium | Partly fixed. Every top-level key the spec does not own (such as `study_gate`) is carried forward (test `test_r08`). Tier/effort still comes from the spec, and PLAN_SPEC.md says to restate reclassifications. |
| D2-N02 out-of-band contract edits blocked completion | medium | Fixed. The receipt binds to the recomputed contract that actually ran. D3-F01 showed that the first version re-stamped every task, so now only the completing task's stored digest is refreshed. Tests `test_r08`, `test_r09`. |
| D2-N03 worker-reported failed check refused runner-validated work | medium | Fixed. Receipt `validations` come from the runner's `validation_results`. Failures the worker reports are kept as `worker_reported_failed_validations`. Test `test_r08`. |
| D2-N04 lock loop busy-spin / no timeout when the takeover fails | low | Fixed (deadline check, sleep, distinct error, rename-verify guard removal). Test `test_r04`. |
| D3-F02 completion side effects ran before the receipt check | medium | Fixed. The receipt is validated before subtask reconciliation and learning publication. Test `test_r09`. |
| D3-F03 failed manifest write left the in-memory generation ahead of disk | low | Fixed by restoring the generation on write failure. Test `test_r09`. |

### Remaining findings (non-blocking, recorded, not fixed)

- D4-F01 (medium): `complete_task` and `reset_task` write or delete learning and design files before the stale-generation check in `save_manifest`. Only a stale writer reaches this path. Proposed follow-up: hold the re-entrant lock and check the generation at the start.
- D4-F02 (medium): a dependent task completed after its dependency was hand-edited outside `revise` binds the edited dependency into its stored digest, so `revise` reopens the dependency but not the dependent. Hand-editing `manifest.json` is unsupported (use `revise`). Proposed follow-up: chain stored dependency digests.
- Low/info: D3-F04 narrow guard races (double fault, or a filesystem without hard links); D3-F05 flag digests from pre-013 code carry no origin marker (no live impact: the live manifest has none); D3-F06 CLI `complete` has no runner validation evidence; D3-F07 `studyctl` writes the manifest without the lock (outside write scope); D4-F03 reconciliation can mark subtasks before it raises; D4-F04 `revise` reopens an `in_progress` task without coordinating with the active claim; D4-F05 renaming a task ID that has a preserved learning artifact fails the staged audit; D4-F06 `revise` does not enforce preservation of requirement IDs; D4-F07 the digest excludes requirement text and guidance; D4-F08 `revise` backfills receipts for pre-012 completions from declared hashes. D3-F08/D4-F09: the `012` receipt hashes are superseded by this receipt.
- D2-N06: the live `.ai-work` plan has not been migrated (no generation). Plan artifacts are outside this task's write scope and a runner is active. Run `recover-projections` once while no runner is active.

## Acceptance coverage (assigned AC01–AC04 from the prepared decision)

- **AC01** A failed revision leaves the previous manifest and task projections readable: `test_ac01` (cycle, uncovered requirement, orphan review, vague text), `test_r07` (staged-audit failure after staging was written; killed revise before publication, then recovery), `test_r02` (a refused revision without a generation leaves the files byte-identical).
- **AC02** Every requirement has a consumer; every implementation has explicit acceptance and validation: `test_ac02` (coverage, missing acceptance/validation, strict JSON, subtask IDs), `test_r01` (the review task completes through the runner path).
- **AC03** A transformed research task stays pending, with subtasks that cite its assigned report: `test_ac03`. Prepared research is rejected as completion or review proof.
- **AC04** Legacy schema 1–3 files are not silently rewritten with schema-4 projection rules: `test_ac04`. `test_r03` limits the generation upgrade to schema-4 manifests and makes it explicit.

Evidence: `implementation/logs/013/20261120T113403-24540/check-01.log` … `check-06.log` (all six declared checks exit 0) and `implementation/013-checks.json`.

## Claims check

The revision-2 alternatives (staged generation + single writer, rejecting per-file atomic rename alone, deferring SQLite) match the code: no database or service was added. The decision's cost/latency section asks to measure bytes read and rebuild duration. That was not measured here, and no doc claims a cost or latency saving. Crash testing uses process-level interruption (`os._exit`) and injected exceptions, not power loss or fsync fault injection. The review dispatches cost about USD 3.00, 4.21, 2.60 and 3.17 as reported by the provider CLI.
