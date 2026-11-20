# 007 Review-and-correct outcome: selective activation, intake and late promotion

The prepared decision (`prepared-research/006-activation-intake.md`, sha256 `01463c79…`) was input evidence only. It does not prove this implementation or its review.

## Independent review

| Round | Dispatch evidence | Route | Session | Verdict | Blocking |
|---|---|---|---|---|---|
| 1 | `reviews/007/dispatch-1.json` (`f1df60ab…`) | claude / claude-opus-5-5 / xhigh, max, read-only, fresh | `f4843e41-99c2-49f3-93db-8f0305664596` | changes_requested (9 findings) | H1, H2 |
| 2 | `reviews/007/dispatch-2.json` (`ecc7aa77…`) | claude / claude-opus-5-5 / xhigh, max, read-only, fresh (codex/gpt-6.2-sol skipped: quota) | `a4cc33d8-ff48-4445-b39c-77d8cb222f60` | approved (10 findings) | none |

Round 2 reviewed the final hashes listed in `007-receipt.json` and found no critical or high defect. Both rounds used a max-tier reviewer, not a frontier one, and the receipt claims no reused session or dispatch. Reported reviewer spend: USD 1.77 for round 1 and USD 2.14 for round 2.

## Corrections made for round-1 findings

- **H1 (high): held-out cases were not held out.** The extractor cues are now a frozen `requestctl.ACTIVATION_CUES` table, hashed by `cue_table_sha256()` (`54d5c6df…`). The eight cases seen while tuning (D016-D019, O011, O012, P004, P005) moved to the `tuning` split. The cue `do not promote`, which encoded the label, was removed. New held-out cases H001-H019 were written after the freeze by a separate agent; see the authoring record below. The cue table was not changed after their first evaluation. `routing_self_test.py` checks the following:
  - the hash is still the frozen one;
  - held-out prompts are distinct from tuning prompts and contain no label text;
  - the measured ceilings hold;
  - no new held-out miss appears.

  The exact `== 0.0` assertions were removed. D019 now uses `pae current`, a plan lifecycle command, instead of `pae status`, which reports the installer.
- **H2 (high): lifecycle commands and skill-name mentions were routed ORCHESTRATED.** Lifecycle cues are now matched before invocation. Explicit invocation requires a `$`/`/` sigil or a directive verb, and a skill name inside a path (`bin/plan-and-execute.js`) is not an invocation. O010 and D019 are relabeled `lifecycle`. New tuning cases cover the gap: L001 (`$plan-and-execute status`), L002 (`/plan-and-execute resume`) and D020 (a file-path mention).
- **M1: tautological artifact tests.** The tests now run the actual `requestctl.py evaluate-route` CLI inside a temporary git repo and compare a recursive file snapshot, including `.git`. They also assert on `extract_prompt_signals` output for the acceptance prompts. The hard-coded `created_artifacts` field and the unused `prompt` parameter were removed. `--spec` now rejects unknown fields and invalid signals with `ERROR:` and exit code 2, not a traceback.
- **M2: invented baseline and costs.** The metric is now labeled `offline_cue_extractor_proxy`. It is computed for four alternatives: selective, explicit-only, all-direct and always-orchestrate. The paid classifier is `unmeasured`, and `c_unneeded_plan`/`c_recovery` are `null`. The synthetic keyword "baseline" was removed. No offline proxy exists for the 0.11.0 SKILL.md description.
- **M3: a capability override dropped the security floor.** Risk signals (`silent_failure_costly`, `cross_cutting_risk`, `weak_validation`) are now always merged into `capability_signals`. `{security_sensitive, capability_signals:[mechanical_edit]}` gives strong/high, both in-process and through the CLI.
- **M4: promotectl and requestctl disagreed.** There is now one shared rule, `requestctl.near_finished_stays_direct`, which promotectl imports. A nearly finished, cohesive request with at most one remaining outcome stays DIRECT unless `EXPLICIT_INVOCATION` is set. A cross-module test covers 16 combinations of near-finished/cohesive/count/explicit.
- **L1/L2.** Transcript-file and `user:`/`assistant:`/`human:` turn detection now covers `original_goal` and every list field, and catches turns split across items. The promotion test parses the `Remaining outcomes`, `Completed work` and `Source evidence pointers` sections exactly.
- **I1.** All checks were re-run on the final reviewed hashes; see Validation. SKILL.md was not changed by 007. It is 6967 bytes with LF line endings, against the 6955-byte 0.11.0 baseline (+12), at hash `cda3a0…`. The reason-code persistence and offline/live evaluation limits are documented in ROUTING.md (`Route decision and capability separation`, `Offline and host evaluation`), not in SKILL.md.

## Measured offline proxy (run `20261120T075627-15120`, check-02)

Tuning split (39 cases, in-sample regression lock): selective proxy has exact match 39/39.

Held-out split (19 cases, written by a separate author, evaluated once after the freeze):

| Alternative | Accuracy | FP rate | FN rate |
|---|---|---|---|
| selective cue proxy | 0.7368 | 0.0 | 0.5714 |
| explicit-only | 0.7368 | 0.0 | 0.7143 |
| all-direct | 0.6316 | 0.0 | 1.0 |
| always-orchestrate | 0.3158 | 0.9167 | 0.0 |
| paid classifier | unmeasured | unmeasured | unmeasured |

Known misses, all kept as recorded:
- **Route misses:** H012, H013 and H014 (orchestration needed but routed DIRECT); H018 (promotion routed DIRECT); H017 (routed `orchestrated` instead of `promote`; a plan is still created, so it does not count as a plan-creation error).
- **Capability floor:** only 1 of 3 held-out short high-risk fixes reaches strong (H001). H002 (hard-coded key) and H003 (missing role check) stay standard/medium because no frozen cue matches them. All three stay DIRECT.

The proxy prefers DIRECT. On held-out cases it creates no unneeded plan but misses 4 of 7 needed orchestrations. These rates measure a deterministic regex extractor, not host skill selection. E[C] cannot be computed because the plan, recovery and classifier costs are unmeasured; they stay unknown, not zero.

**Superseded 006 claims.** `006-outcome.md` lines 10 and 17-19, and the AC04 evidence in `006-receipt.json` (run `20261120T054702`), are superseded by this report. They claimed 8 held-out cases with FP=FN=0, accuracy 1.0 and E[C]=0 against a synthetic baseline, and SKILL.md=6963 B; those results were in-sample. The 006 artifacts were left unchanged because they are outside this task's write scope.

## Held-out authoring record

- **Author:** a synchronous Agent-tool subagent, model alias `sonnet`, agent id `aa6a59a20ff06682d`. It ran on 2026-11-20 after the freeze and before the 07:56 UTC check run, with 39,663 tokens and about 18 s duration.
- **Isolation:** the subagent was told not to read, search or open any file, and its only tool call was the handback. It received the route definitions and a category distribution only, not requestctl.py or the corpus.
- **Freeze:** the cue table hash at authoring time was `54d5c6df29048222cd81cd35500aec55fabbb60d979479b0589f9534772c9564`. This is the same value now recorded in `held_out_protocol`.
- **Output:** 20 prompts. One (`$plan-and-execute status`) was excluded as an exact duplicate of tuning case L001, and the exclusion is recorded in `held_out_protocol.excluded`. The other 19 were inserted verbatim with the author's labels.
- **Brief:** route definitions as in ROUTING.md (direct, orchestrated, promote, lifecycle), plus the invocation and lifecycle command forms. The distribution was: 3 short high-risk, 2 long logs, 2 medium cohesive CRUDs, 2 cohesive near-misses, 2 near-finished high-context, 3 independent/broad/cross-cutting, 2 explicit invocations, 2 late promotions and 2 lifecycle commands. The brief forbade label words in prompts and asked for varied phrasing.
- **Limitation:** the author is another model session started by the review worker, not a human or an external party. The raw output is preserved only through the inserted cases.

## Validation

- **`P1_TESTS_007`** (resource watcher; `.ai-work/resource-watch/20261120T045626-P1_TESTS_007-…jsonl`): all 4 declared checks exit 0. They are activation_intake (9 acceptance groups), routing_self_test, promotion_self_test and self_test. Logs are in `implementation/logs/007/20261120T075627-15120/check-01..04.log`, and the receipt is `007-checks.json`.
- **`P1_GATE_TESTS`** (resource watcher; `.ai-work/resource-watch/20261120T050509-P1_GATE_TESTS-…jsonl`): 55 tests, OK (1 skipped). This includes rejection of fake reviews, low-tier reviews, reused or foreign dispatches, and frontier reviews without two recorded functional max failures.
- **Additional local runs, all passing:** `node tools/validate-skill.js`, `token_efficiency_self_test.py`, `artifact_concision_self_test.py`, `companion_self_test.py` and `model_routing_self_test.py`.
- **Mutation checks:** reverting each of the M3, M4, L1 and H2 fixes in-process makes the new tests fail.
- **Service map:** stamped with `--confirm-reconciled` after the test edits. No service or resource changed, and validation IDs are preserved.

## Deferred round-2 findings (non-blocking)

- **M1:** a preposition followed by the skill name (`with/via/using plan-and-execute`) still counts as explicit invocation.
- **M2:** lifecycle cues are not anchored to a command-shaped prompt, and a lifecycle route ignores risk flags.
- **M3:** the freeze hash covers only the cue table, not the combination logic or the held-out labels.
- **M4:** the authoring record exists only in this report, not as a separate pinned artifact.
- **M5:** handled by the supersede note above.
- **L1:** a `strong_validation` override lowers security effort to medium.
- **L2:** the agreement test does not cover promotions with no strong reason.
- **L3:** `--spec` values are not type-checked, and a JSON load error prints a traceback.
- **L4:** the label-leak list is short.
- **L5:** small mismatches between the docs and the code.

Fixing M1 or M2 changes the cue table. That turns H001-H019 into tuning data, so a fresh held-out set must be written first. The other fixes change reviewed files and need a new review dispatch.

## Limitations

- Live host skill loading, token use, latency and real activation FP/FN were not measured; that needs owner-confirmed authenticated runs.
- The held-out set has 19 cases from a single model author; its rates are coarse.
- Unchanged: 006 receipt/outcome (outside the write scope), SKILL.md and agents/openai.yaml (already state the contract and were reviewed as preserved).
