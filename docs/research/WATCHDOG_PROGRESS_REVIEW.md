# Watchdog and progress whole-skill review

Review date: 2026-10-12. Baseline: `8882735` through the working tree, including new watchdog, signal and digest files. Applied `skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md`. No feature changes or commit are part of this review.

## Actionable findings

1. README observer descriptions promise no file writes, although `watchdogctl.watch` persists `.ai-work/watchdog/<hash>.json`. Distinguish read-only `status` from cached `watch`; neither changes plan/job/process state.
2. README/CHANGELOG digest descriptions present >99% token reduction as universal. `log_watch.digest` estimates tokens as `chars/4` and reads a bounded prefix. Qualify the synthetic benchmark and document truncation/omission evidence.
3. Routing references call a configured global preference a built-in default and prohibit Claude primary, contradicting `routing_config.load` / `provider_chain`. Preserve the illustrated Codex/Antigravity preference while documenting plan/task/CLI overrides, legacy snapshots, empty-tier handling and the host's Opus override of bootstrap Fable in `max`.
4. WATCHDOG idle wording implies that a zero task override inherits a positive plan value. `collect_plan` inherits the plan value only when the task field is absent; a present nonpositive value uses the 1800-second observation default.

## Checklist trace

| Item | Evidence and conclusion |
| --- | --- |
| Entrypoint/reference map | SKILL links WATCHDOG on demand; LIFECYCLE links observation and WORKFLOW links progress refactoring. No new eager reference loading. |
| Flow/contracts/state/cleanup | Traced watchdog status/watch through lifecycle leases, availability and read-only `jobctl.status_job`; watch writes only its selector cache. Signal parser/probe and digest have bounded reads/output. Existing scan cursor behavior is retained. Manifest v4 and completion fields remain unchanged. |
| Routes/fallback/resume | Provider chains honor configuration precedence and pinned routes; existing failure ladders retain environmental/ceiling handling. Watchdog only displays resume commands. Finding 3 requires documentation correction. |
| Concepts/links/examples | Searched affected concept/field references across README, CHANGELOG, skill references, scripts and validation wiring. Findings 1–4 require correction. |
| Tool affordances | Existing scripts implement observation, normalized fingerprints, progress probing and map progress-gap warnings. No additional script is needed. |
| Token surfaces | Worker progress guidance occurs in stable prompt rules and is covered by progress_runner tests. Digest outputs enums/counters/hashes with redacted messages; raw source logs remain available. Finding 2 requires qualification. |
| Resource/preflight/monitoring | Inspected only `.ai-work/SERVICE_MAP.md`; ALL maps to `npm run check`, with Python/Node prerequisites and no runtime services. New signal/digest/watchdog tests are in the full suite. This review changes documentation only. |
| Durable evidence/limits | Findings recorded here; final validation outcome and platform limits below. |

## Resolution and validation

All four findings are resolved:

- README (English/Portuguese) and CHANGELOG distinguish status from cached watch, qualify digest measurements and configured routing, and clarify validation probes versus worker activity evidence.
- ROUTING_CONFIG, MODEL_ROUTING, MODEL_MAPPING and WATCHDOG retain the illustrated global preference while restoring configuration precedence, empty-tier semantics and host-specific model overrides.
- WATCHDOG now describes task-field presence and the 1800-second fallback exactly as implemented.

Mapped ALL validation passed on Windows on 2026-10-12 (Python 3.13.15, Node 26.7.0):

```powershell
& 'C:\Users\luizc\AppData\Local\Programs\Python\Python313\python.exe' 'C:\Users\luizc\.claude\skills\plan-and-execute\scripts\resource_watch.py' run --repo-root . --map .ai-work/SERVICE_MAP.md --validation ALL
```

- `npm run check` exited 0; clean, skill validation, Node tests, Python skill self-tests and repository checks passed. The watcher reported `test_exit=0 health=healthy`.
- Node: 38 tests, 36 passed, 2 skipped. Watchdog: 17 tests passed. Signal: 5 check groups passed. Digest: 10,000 synthetic lines / 545,563 input characters became 6 lines / 453 characters, a 99.92% estimated reduction.
- Runtime evidence: `.ai-work/resource-watch/20261012T121433-ALL-19616-1791818073744417800.jsonl`. No historical validation logs were read.
- `git diff --check` passed for this review's documentation changes. The service map was fresh; this task changed no discovery/test/build/CI/container inputs, so no reconciliation stamp was needed.

## Unverified limits

- Review runs on Windows; Unix cron/nohup deployment and real Task Scheduler registration are not exercised.
- Synthetic provider sessions/jobs test observation semantics; live provider authentication, quota recovery, remote-host leases and multi-host scheduling are not exercised.
- Node unreadable-directory and installer symlink tests are skipped on Windows; Unix permissions, ACL-denied trees and installer symlink replacement are not independently exercised.
- Digest token counts use `chars/4`, not a provider tokenizer; reduction depends on corpus repetition, bounds and group count.
