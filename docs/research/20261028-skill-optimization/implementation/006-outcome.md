# 006 Implementation Outcome — Selective activation, intake and late promotion

## Summary of changes

- `skill/plan-and-execute/scripts/requestctl.py`: Added deterministic zero-classifier-call activation routing (`evaluate_activation`), cue extraction (`extract_prompt_signals`), offline corpus evaluation (`evaluate_routing_corpus`), and read-only CLI commands (`evaluate-route`, `eval-corpus`).
  - Separates routing mode (`direct` / `orchestrated` / `promote` / `lifecycle`) from capability tier (`routingctl.minimum_route`), so a small security-sensitive cohesive edit stays `DIRECT` while preserving a `strong`/`high` implementation floor.
  - Bounds `reason_codes` (max 6) and records persisted reason codes only when `persist_plan` is true (`orchestrated` or `promote`); rejected implicit matches (`direct` and exact `lifecycle`/`configure` commands) create no plan, ledger, study, or reason-code files and load no orchestration references.
  - Documents optional `validate-or-fix` exit pointer (`references/VALIDATION_WORKLOADS.md`) without eager loading.
- `skill/plan-and-execute/scripts/promotectl.py`: Added optional bounded `reason_codes`, `estimated_working_set`, and `evidence_pointers`, rejected pasted conversation transcripts (`transcript.jsonl` / chat history markers), and rejected `nearly_finished` cohesive promotions so high context alone creates no control files while preserving worktree edits and scheduling only `remaining_outcomes`.
- `skill/plan-and-execute/references/routing-evals.json`: Extended from 28 to 36 cases with 8 held-out cases (`D016`-`D019`, `O011`-`O012`, `P004`-`P005`) covering short high-risk security fixes, long repetitive logs, medium cohesive CRUDs, exact lifecycle commands, unrelated workstreams, explicit invocation, and near-finished vs. substantial high-context promotion.
- `skill/plan-and-execute/SKILL.md`, `skill/plan-and-execute/references/ROUTING.md`, `skill/plan-and-execute/references/PROMOTION.md`: Clarified ledger-free negative implicit exit, bounded reason-code persistence, routing-mode vs. capability-tier separation, and offline/live-host evaluation limits (`SKILL.md` = 6963 LF bytes vs. 6955 baseline, +8 bytes, within the 7000-byte budget).
- `skill/plan-and-execute/agents/openai.yaml`: Preserved unchanged; already encodes selective `DIRECT vs ORCHESTRATED`, late promotion of remaining outcomes, and signal-based capability routing (`allow_implicit_invocation: true`).
- `skill/plan-and-execute/scripts/routing_self_test.py` and `test/optimization/activation_intake_self_test.py`: Added regression and acceptance coverage for all positive, negative, capability-separation, promotion-worktree-preservation, and corpus-measurement cases.

## Measured offline routing evaluation (`routing-evals.json`)

- Entrypoint LF bytes: `SKILL.md` = 6963 (`+8` vs. 6955 baseline), `agents/openai.yaml` = 1312, `ROUTING.md` = 6028, `PROMOTION.md` = 4696.
- All 36 cases: selective metadata gate `FP=0.0`, `FN=0.0`, `accuracy=1.0`, `near_miss_FP=0.0` vs. catch-all baseline `FP=0.619`, `FN=0.1333`, `near_miss_FP=0.8`.
- Held-out 8 cases: selective metadata gate `FP=0.0`, `FN=0.0`, `accuracy=1.0` (`E[C]=0.0`) vs. catch-all baseline `FP=0.6`, `FN=0.0` (`E[C]=0.6`).
- Capability check `D016` (2-line JWT signature bypass): `route=direct`, `capability_route={"tier": "strong", "effort": "high"}`.

## Validation checks (`P1_TESTS_006`)

All 4 declared checks passed (`006-checks.json`, run `20261120T054702-28916`):
1. `python test/optimization/activation_intake_self_test.py` — exit 0
2. `python skill/plan-and-execute/scripts/routing_self_test.py` — exit 0
3. `python skill/plan-and-execute/scripts/promotion_self_test.py` — exit 0
4. `python skill/plan-and-execute/scripts/self_test.py` — exit 0

Additional repo checks run and passing after final edits: `node tools/validate-skill.js`, `token_efficiency_self_test.py`, `model_routing_self_test.py`, `companion_self_test.py`.

## Limitations

- Live host skill loading, token usage, and latency were not measured because no owner-confirmed authenticated provider run was executed.
- Independent max-capability code review (`007`) remains pending and is not claimed by this implementation receipt.
