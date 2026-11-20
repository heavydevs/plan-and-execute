# Task 009 outcome: review and correction of oversized-request fragmentation and prepared packages

## Result

Five fresh, read-only, max-tier reviews ran through `review_dispatch.py`. Codex was in quota cooldown for every dispatch, so each review ran on Claude Opus 5.5 at xhigh effort. The final review (dispatch 5) **approved** with 0 critical or high findings. Every blocking finding from earlier dispatches was corrected (F01, F02, F03 and R4-01). Each correction has a regression test that fails when the fix is reverted.

The prepared report `008-primary-planning.md` is input evidence only. It does not prove that this implementation or its review passed. This outcome and `009-receipt.json` supersede the claims in `008-outcome.md`, which is outside task 009's write scope and is now stale. In particular:

- the extractor is now `ooxml-text-v4`;
- contradiction preservation is identity-based;
- run-level text boxes are recorded.

## Independent reviews

| Dispatch | Reviewer | Verdict | Findings (blocking) | Reported USD | Session |
|---|---|---|---|---|---|
| 1 | claude / claude-opus-5-5 / xhigh | changes_requested | 13 (3 high) | 2.33 | 3d0c2726-6747-4228-baa8-d194fe55c53f |
| 2 | claude / claude-opus-5-5 / xhigh (codex: quota) | approved | 8 (0) | 2.63 | ef211661-7a07-4abc-b5d8-cb8d48beb84b |
| 3 | claude / claude-opus-5-5 / xhigh (codex: quota) | approved | 8 (0) | 2.44 | 15e6beb3-9f12-4159-a7a0-b28e3f58991b |
| 4 | claude / claude-opus-5-5 / xhigh (codex: quota) | changes_requested | 7 (1 high) | 2.03 | 9f279a29-a8c4-4d40-a8fb-252553a9e511 |
| 5 | claude / claude-opus-5-5 / xhigh (codex: quota) | **approved** | 6 (0) | 1.70 | 10395237-a60e-42b7-8e2b-cdd03ca32974 |

The receipt pins dispatch 5. Its reviewed-input hashes equal the final file hashes. Total reported review spend was about USD 11.13, provider-reported. No frontier model was used.

## Corrections

- **F01 (high):** an id-less digest item matched every id-less obligation (`None == None`). Only non-empty ids now count. The audit and its error messages give a reason per id.
- **F02 (high):** `gridSpan`, `gridBefore` and row extent were unbounded. All three are now capped at 64 columns, and hostile values fail fast. Covered by a time-bounded test.
- **F03 (high):** content wrapped in `w:sdt` or `w:customXml` at row, cell, block and run level is now traversed. The following are now recorded: run-level `mc:AlternateContent`, Office Math, `altChunk`, `subDoc`, tracked moves, and any text-bearing element the walker does not handle (`w:t`/`m:t`/`a:t`).
- **F04:** contradictions are carried by identity through `WORKSTREAM_INDEX`, `recorded_contradictions` and the comparator.
- **F05 and R2-01:** obligations in split prose or Markdown-table blocks map to the fragment that holds them.
- **F06:** `document.xml` must be UTF-8. UTF-16/32 input, NUL bytes and non-UTF-8 declarations are rejected.
- **F07:** schema-v2 pins are mandatory. `validate-package` and `validate-consumption` re-hash the raw source and re-derive blocks, `block_count`, fragments, obligations, contradictions and unsupported structures. `--source` and `--require-source` are new.
- **F08:** worker guidance names every validator contract.
- **F09:** new negative tests cover duplicate fragment ids, paths and consumption requests.
- **F11:** fragments are read once and verified from that single read.
- **F12:** `gridBefore` column alignment is fixed.
- **R2-02:** the coverage review must acknowledge each `unsupported_structures` entry, one acknowledgement per entry, or block.
- **R2-03, R3-01, R3-02 and R4-02:** an id match also needs a restatement. That means 3 or more words besides ids, or 4 or more CJK/Thai letters. Bare id echoes fail, and translated digests pass.
- **R2-04:** `validate-digest` audits its own batch's obligations, so `resume-status` keeps an incomplete digest pending. `fragment_hashes` is required.
- **R2-05, R3-05 and R4-03:** digest contradictions need ids. New ids must start with `<digest_id>-` and be unique.
- **R3-04:** a source with zero extracted obligations needs `acknowledged_obligation_floor`. The scope of the heuristic is documented.
- **R3-06:** acknowledgements are type-checked and counted per entry.
- **R4-01 (high):** hierarchical ids such as REQ-7.1 and REQ-007-A are extracted whole. An explicit id shared by several clauses never identifies one of them.

## Open, non-blocking (recorded, not fixed)

- **R5-01 (medium):** one mislabelled item, whose `canonical_id`, `obligation_id` and leading text id point at different obligations, can still satisfy several obligations.
- **R5-02 (low):** a 60% same-polarity substring can cover sibling clauses and drop a qualifier.
- **R5-03 (low):** no reverting test exists for the ambiguity rule inside `covered_obligation_ids`, or for the change of the floor gate's condition.
- **R5-04 (low):** short restatements in Indic scripts can be falsely rejected.
- **F10 (extraction side):** a clause's first explicit id still becomes its `explicit_id`. This is fail-safe over-reporting.
- **R3-03:** text inside tracked insertions and moves stays excluded and is only recorded, as the decision allows. The docs warn about inverted polarity.

## Test evidence

These are the declared checks through `resource_watch.py`, validation `P1_TESTS_009`, run `20261120T093711-16256`. Both exited 0.

- `logs/009/20261120T093711-16256/check-01.log`: `test/optimization/primary_planning_self_test.py`. It covers the 008 cases AC01–AC09, the comparator, and 18 task-009 regressions: F01–F09, F12, R2-01/02/04, R3-01/04/05/07 and R4-01.
- `logs/009/20261120T093711-16256/check-02.log`: `skill/plan-and-execute/scripts/preplan_self_test.py`, including the `--source` wiring of the `validate-package` and `validate-consumption` CLI commands.
- Supplemental, not a declared check: `delivery_gate_self_test.py` ran 18 reuse, frontier and dispatch cases, all OK. They cover a fake review, a reused session or dispatch, frontier without two max failures, frontier for quota, and a stale reviewed input.
- Manual mutation check, using a scratch script that is not a repository artifact: 23 in-memory reverts of the fixes were all caught by the suite.

## Limitations

- No live model digest comparison was run (G002), and no paid-model benchmark. `compare-baselines` checks fragmentation losslessness of the deterministic extractor, not model digest quality. No cost or quality improvement is claimed.
- The reviewers were read-only and ran no tests. The tests above ran locally on Windows with Python 3.11.15.
- Obligation extraction recognises English modals and fixed id prefixes only. When the raw source is unavailable, consumption reports `unavailable` unless `--require-source` is given.
- The service map was re-stamped with `stamp --confirm-reconciled` after the test changes. No resources or validation ids changed.
