# Plan extension — 2026-11-12: recovery timer and frontier models

**Active plan:** `.ai-work/20261028-skill-study-provider-switch/` on branch `checkpoint/plano1-estudo-provider-switch-20261028`.
**Purpose:** amend the existing 102-task plan to 106 tasks, without replacing completed implementation or spawning another plan. All four new TODOs are pending. Research is not product acceptance or independent code review.

## Already covered — do not duplicate
- **091/092 — complex blockers:** classify genuine complicated design/product defects; safely add bounded repair/design/validation TODOs and suspend affected task, preserve checkpoints and no infinite expansion. Not triggered for quotas or environment outages.
- **099/100 — semantic progress:** five-minute progress diagnosis with reliable work units, not unconditional restart/escalation.
- **101/102 — OS sleep:** one local host-native continuous power lease across tasks/providers, not an interval timer; release at terminal/pause, reacquire before resumed worker.

## New pending features

| Implement | Independent real review | Research | Scope |
|---|---|---|---|
| 103 | 104 | [103-opt-in-keepalive-scheduler.md](../../research/20261028-skill-optimization/prepared-research/103-opt-in-keepalive-scheduler.md) | Single opt-in OS timer every 20 minutes for >=6 executable pending tasks; lease-safe recovery only on dead runner, automatic owned scheduler removal. |
| 105 | 106 | [105-frontier-model-routing-20261112.md](../../research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md) | Audit latest provider/model/effort catalogs and add sixth frontier L6/F6 above max; Fable 5.2, GPT-6 Astra and Antigravity Gemini 4 Carbon are conditional candidates. |

## Frozen decisions for implementers
1. **Timer threshold:** >=6 genuinely executable unfinished TODOs *when offered*; exactly one interactive opt-in prompt; unanswered/noninteractive defaults off. Once enabled, keep until terminal state even when fewer than six tasks remain. This is a cautious configurable heuristic and needs future empiric validation.
2. **No tokens for healthy polling:** adapt `keepalivectl.py` and `watchdogctl.py`; no new installed subskill or parallel orchestrator. Windows Task Scheduler, Linux systemd user timer or safe cron fallback, macOS launchd if supported; WSL guest cannot protect/wake Windows host.
3. **Recovery:** only dead/awaiting-next/expired-cooldown work with confirmed ownership and authorized resumable runner; no duplication, blind restart of live silent worker or human approval bypass; honor restart-loop budgets and stored flags.
4. **Cleanup:** un-register exactly the owned timer before deleting plan metadata on success/cancel/reset; if the plan disappeared, next tick self-removes or records an actionable safe failure. Power lease 101 lifecycle is a distinct mechanism, not a property of the 20-minute scheduler.
5. **Model hierarchy:** L1 economy, L2 standard, L3 advanced, L4 strong, L5 max, **L6 frontier**; preserve legacy contracts and make L6 optional. Actual IDs/effort must be observed in target CLI/account; compare validated quality per credit/cash, not marketing labels. No silent API billing or environment-fault escalation to frontier.
6. **Reviews/integration:** execute 103 then genuine 104, 105 then genuine 106, both before task 082; 083–086 remain the final gates. Tests and independent review evidence must name actual hashes, model/provider and platform limitations.
7. No provider authenticated execution, global OS change, installed-skill modification, npm publication, automatic force-restart, or high-cost model access is authorized by the mere existence of this plan amendment.

## Primary sources
- Microsoft Task Scheduler multiple instance policy: https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-multipleinstancespolicy-settingstype-element
- systemd timer scheduling: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- Linux inhibit: https://www.freedesktop.org/software/systemd/man/latest/systemd-inhibit.html
- macOS idle assertions: https://developer.apple.com/documentation/iokit/1557134-iopmassertioncreatewithname
- Claude Fable 5.2: https://platform.claude.com/docs/en/models/fable-5-2/overview
- OpenAI model catalog: https://developers.openai.com/api/docs/models
- Antigravity Gemini 4 Carbon launch: https://antigravity.google/blog/gemini-4-carbon-in-google-antigravity
- Google SRE monitoring: https://sre.google/sre-book/monitoring-distributed-systems/
