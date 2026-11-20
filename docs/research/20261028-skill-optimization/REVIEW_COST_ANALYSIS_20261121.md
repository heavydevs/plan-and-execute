# Review cost analysis (2026-11-21)

**Sources:**
- Worker cost and time: `.ai-work/runner-logs/runner-20261120-d.log` (`total_cost_usd`, `duration_ms`).
- Nested reviewer cost and time: `implementation/reviews/<id>/dispatch-*.json` (`usage.usd`, timestamps).
- Findings: `findings-*.json`.
- Finding status: `implementation/<id>-receipt.json`.

No model was called. Opus 5.5 list prices reproduce the 003 worker cost exactly.

| Review | Dispatches | Worker $ | Nested $ | Total $ | Worker min | Nested min | H/M/L/I findings | Highs in round 1 |
|---|---|---|---|---|---|---|---|---|
| 003 | 2 | 3.91 | 2.65 | 6.56 | 21 | 8 | 0/3/5/6 | 0 |
| 005 | 3 | 4.94 | 3.91 | 8.85 | 30 | 13 | 0/6/10/4 | 0 |
| 007 | 2 | 6.91 | 3.90 | 10.81 | 31 | 12 | 2/9/7/1 | 2 |
| 009 | 5 | 15.35 | 11.14 | 26.49 | 72 | 34 | 4/12/16/10 | 3 |
| 011 | 2 (brief-2 has no dispatch record) | 6.34 | 4.48 | 10.82 | 30 | 11 | 3/10/9/0 | 3 |
| 013 | 4 | 8.76 | 12.98 | 21.73 | 54 | 28 | 2/12/16/4 | 2 |
| **Sum** | **18** | **46.20** | **39.06** | **85.26** | | | **11/52/63/25** | **10** |

Costs the table leaves out:
- An earlier blocked 003 attempt ($3.54, background subagent; now prevented).
- The missing 011 dispatch (unknown).

## Findings

1. **Cost.** The average is $14.21 per review. The nested reviewer accounts for 46% of it. For the 60 remaining reviews (015 in progress, 59 pending), that projects to about **$853** and about 40 hours.
2. **Round 1 is where the value is.**
   - Round 1 found 10 of the 11 highs, and no criticals, in 4 of 6 reviews. All are real defects:
     - 013 F01: review tasks could never complete through the runner.
     - 009 F02: a DOCX denial of service.
     - 011 F01–F03: guard bypasses.
   - All 11 highs are `resolved` in the receipts.
   - Round 1 costs only **$10.95 of the $39.06** nested spend, or $1.82 per review.
3. **Later rounds are verification loops.**
   - Rounds 2 and later cost $28.11 in nested reviews. Fitting worker cost to round count gives about **+$3.06 and +15.5 minutes per extra round** (n=6, rough).
   - They found 1 high: 009 R4-01. Whether it already existed at the R2 hashes is unknown.
   - They also found three regressions introduced by corrections (005 R2-F1, 013 R3-F01, 009 R3-01), so one confirming round is valuable.
   - Every dispatch reported 6–13 findings, so the loop never converges on its own. In 005 and 013, rounds 2 and later were all `approved` with 0 blocking findings. They ran only because fixing medium/low items changed reviewed hashes and forced re-dispatch. The procedure has no stop rule.
   - Rounds 3+: 6 dispatches, $13.32 nested plus about $18 worker, for at most 1 high.

## Options

- **A: keep as is.** Rejected: no convergence, about a third of spend wasted.
- **B: lower effort.**
  - Evidence: CursorBench has Opus high equal to xhigh (56.0%, $3.97 vs $6.98); the AA index gives 52 vs 57 at 0.55x output (`anthropic-claude.md` §6, `cross-model-benchmarks.md` §2a).
  - Nested reviewer: keep xhigh. Round 1 is cheap and holds the value.
  - Worker: high is acceptable, because a fresh xhigh confirmation checks its corrections. Estimated worker saving 25–40% (unmeasured here).
- **C: the worker is the reviewer.** Rejected: self-approval of corrections breaks PROTOCOL step 6 and would have missed the three regressions above.
- **D: tier reviews by risk.** The gate (`check_delivery.py:346`) requires a max/frontier tier, a fresh context and dispatch evidence, not an effort level, so Sonnet does not qualify. The sample shows no cheap review class (4 of 6 had highs). Only the effort exceptions below are adopted.
- **E: bounded convergence.** Recommended, combined with B for the worker only.

## Recommendation

**The rule:**
1. Dispatch 1 is a full review at xhigh.
2. The worker fixes every critical, high and in-scope medium finding, re-runs the checks, and dispatches **once** more to confirm.
3. If the confirmation is `approved` with no critical/high, the worker stops editing reviewed files. It records the remaining findings as `follow_up` or `accepted_limitation`. The gate already allows unresolved non-blocking findings (`check_delivery.py:369`).
4. A further dispatch happens only to fix a new critical/high. The existing frontier-escalation rule still applies after two failed max reviews.

**Steps:**
1. **Helper change (no runner stop).** Apply it after 015 completes.
   - In `docs/plans/20261028-skill-optimization/support/review_dispatch.py`, `print_dispatch()` (line 594): if the verdict is `approved`, `blocking_findings==0` and `dispatch>=2`, print `CONVERGED: approved with no critical/high; do not edit reviewed files; record remaining findings as follow_up/accepted_limitation; do not re-dispatch`.
   - Add a test case to `review_dispatch_self_test.py`.
   - Keep `EFFORT_FLOOR="xhigh"` (line 67), so the nested reviewer stays at xhigh.
2. **Guidance (runner stopped at a task boundary).** Write a new apply script on the `apply_review_dispatch_20261120.py` pattern (it refuses to run while the runner lease is live).
   - It replaces the `GUIDE_PROC` text "fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed" with the rule above.
   - Files: `PLAN1_SPEC.json`, `manifest.json` and the re-rendered `tasks/*.md`, plus a REPLAN_TRACE line.
   - Tasks: the 59 pending reviews (odd 017–081, 083, 085, 086, even 088–132).
3. **Worker effort (same stop).** Run the command below for the 55 pending reviews other than 083, 085, 086 and 108, which keep xhigh. Then run `planctl validate` and restart the runner.

   `python skill/plan-and-execute/scripts/model_catalogctl.py reclassify --plan .ai-work/20261028-skill-study-provider-switch --task <id> --tier max --effort high --reason "review worker high; fresh xhigh reviewer unchanged"`

**Saving (estimated):**
- Two-dispatch reviews averaged $9.39 and 27 minutes, against $14.21 and 40 minutes overall. E alone saves about **$4.8 and 12 minutes per review**, or about **$290 and 12 hours** over 60 reviews. This assumes about 2.2 dispatches per review.
- Worker effort high saves about $1.4–2.5 more per review, or **$80–140** over 55 reviews.
- The total projection falls from about $853 to **about $420–480**. Re-measure after about five reviews.

**Remaining quality risk:**
- Medium/low findings from the confirming round stay deferred. In 013, N01–N03 were operationally relevant; such items fall to 082, 084 and 086.
- A high found only in round 3 or later would be missed. The 009 R4-01 high is the only case, in 1 of 6 reviews.
- Worker high may make weaker corrections; the fresh xhigh confirmation still blocks critical/high ones.
- Independence and all validators are unchanged.
