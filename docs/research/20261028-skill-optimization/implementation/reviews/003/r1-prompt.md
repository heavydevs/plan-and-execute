You are an independent, fresh-context code reviewer (plan task 003: review of task 002). Review only; do NOT edit, create or delete any file in the repository.

Repository root: C:/Users/luizc/projetos/plan-and-execute/git/plan-and-execute (Windows; Python 3.11 is `python` on PATH; use the Bash tool with POSIX syntax).

## What task 002 was asked to deliver (from its receipt/outcome)
Offline source and contract coverage checks for a single-implementation plan:
- `test/optimization/baseline_contracts.py` must reuse `docs/plans/20261028-skill-optimization/support/check_delivery.py` (`structural`, `verified_files`) directly, not reimplement it, and expose `run_source_and_contract_coverage()`.
- `test/optimization/task_002_self_test.py` must provide negative fixtures proving rejection of: unknown SOURCES ids, prepared-report hash drift (INDEX.json and TASK_INPUTS.json), a requirement without a consuming task, a task entry without `prepared_reports`, and a plan missing a required `082` extension review-gate dependency; plus: a missing authenticated provider is recorded as an explicit execution limitation, never a failure and never a fabricated independent review.
- Each fixture distinguishes historical baseline, current code and expected new behavior.

## Reviewed inputs (verify these SHA-256 values with `sha256sum` before reviewing; report any mismatch)
- test/optimization/baseline_contracts.py  640c2634a0560b31360adcea35a3fdc103260b339651dc0b66e6db1d355c0fca
- test/optimization/task_002_self_test.py  8c0852f477faa86709b3b945cf21b9780e2f2f9f8aebd0099d5c77b890b4a1db
- docs/research/20261028-skill-optimization/implementation/002-receipt.json  fd72360fb27dce55ba6a87e166dd56ae851c6cc5e22a8380a55326aa30f5bcb5
- docs/research/20261028-skill-optimization/implementation/002-outcome.md  2e9583e59ac9ca2d4e9ed9e3d84cb11653aef52980e00b64a834bc64a2e20afb
- docs/research/20261028-skill-optimization/implementation/002-checks.json  7e0d11fd5c132bc92770eb5b85a9abf769a5e0c29304d937a01107727e24d10e
- docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md  300a1adcfc903e555f106543861a5ee96d6aac4631a6289bf210af265c67d379

Both test files are new (untracked) relative to git HEAD, so the whole file is the diff. `baseline_contracts.py` was first created by an earlier task (001: preflight helpers `run_preflight`, `validate_cli_versions`, `validate_context_scope`, `check_inventory_drift`); task 002 added the `check_delivery` import/aliases, `collect_provider_limitations` and `run_source_and_contract_coverage`. Focus on task 002's additions and on any regression they cause to the 001 helpers.

You may read, as supporting context only: `docs/plans/20261028-skill-optimization/support/check_delivery.py` (the gate being reused) and the JSON files it loads (`docs/plans/20261028-skill-optimization/TASK_INPUTS.json`, `PLAN1_SPEC.json`, `FEATURE_SEED.json`, `docs/research/20261028-skill-optimization/prepared-research/INDEX.json`, `SOURCES.json`) only as far as needed to verify behaviour. Do not read `.ai-work/` artifacts, transcripts, other tasks' receipts/logs, or other prepared-research reports.

You may run, read-only: `python test/optimization/task_002_self_test.py` and `python docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py`, and throwaway Python snippets that import the modules (put any scratch file outside the repository). Do NOT run `run_task_checks.py`, `resource_watch.py`, `check_delivery.py --task`, git write commands, installers or anything that writes into the repository.

## What to look for
Correctness bugs (a negative fixture that passes for the wrong reason or would still pass if the guarded check were removed; assertions that are vacuous; mocks that do not reach the code path claimed; path/hash handling errors such as CRLF vs LF, symlink, traversal; reimplementation instead of reuse; import side effects such as `sys.path` mutation that break the 001 helpers; misleading receipt/outcome claims vs. what the tests actually prove), and missing coverage of the stated requirements. Verify each candidate finding by reading the code and, where cheap, by running a snippet; drop anything you cannot substantiate.

## Output (final message only, no preamble)
1. `MODEL_ID:` the exact model ID you are running as (from your system prompt).
2. `HASHES:` `verified` or the list of mismatches.
3. `FINDINGS:` a JSON array; each item `{"id": "F1", "severity": "critical|high|medium|low", "file": "...", "line": N, "summary": "...", "failure_scenario": "concrete input/state -> wrong result", "evidence": "what you ran/read that confirms it", "suggested_fix": "..."}`. Empty array if none survive verification.
4. `VERDICT:` `approved` (no critical/high finding) or `changes_requested`.
