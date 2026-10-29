# F027 / task 058 - Incremental log scanning, digest and artifact retention

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Preserve incremental cursors and explicit coverage gaps; add rotation recovery and owned retention rather than deleting logs to save prompt tokens.

## Questions addressed

- Measure cursor gaps, rotation/truncation, bounded summaries and missed-error risk.
- Prune owned stale artifacts without deleting active diagnostic evidence or rereading entire logs.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- log_watch.scan tracks file device/inode and byte offset, keeps incomplete trailing lines for the next sample and reports skipped bytes with exit2.
- digest reads a bounded prefix and reports truncation/omission. A small digest is not evidence that the entire source log was inspected.
- The scan output truncates matching lines before any shared secret redactor is applied in that function; model-facing consumers need a defined sanitation boundary.

### Read targets and integrity

- `skill/plan-and-execute/scripts/log_watch.py` (SHA-256 `114ea5c9c0ef6db6523e4fd7ea41faf2a8e9464968f3a8527738cec6321d3aaf`): `scan` L58-132; `digest` L135-211
- `skill/plan-and-execute/scripts/resource_watch.py` (SHA-256 `22ac707b846a428c832671c6cfc96d9e45b367f5b3a61963ac0258791a5c2184`): `register_artifact` L62-81; `cleanup_artifacts` L84-122
- `skill/plan-and-execute/scripts/observer.py` (SHA-256 `ad84f96624f85c860edd925ed5bf354dc805b726f943bf14a435f6ef5179b322`): `ObserverError` L37-38; `Unavailable` L41-44; `validate` L47-55; `options` L58-61

## External basis

- [E046] [File Log Receiver README](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/filelogreceiver) - OpenTelemetry; accessed 2026-10-28.
- [E044] [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) - OWASP; accessed 2026-10-28.
- [E045] [Logs data model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) - OpenTelemetry; accessed 2026-10-28.
- [E043] [Monitoring Distributed Systems, Site Reliability Engineering chapter 6](https://sre.google/sre-book/monitoring-distributed-systems/) - Google SRE; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Read full logs repeatedly or delete them after reading | Either wastes tokens/I/O or destroys diagnostic evidence. |
| recommended | Incremental coverage receipts plus guarded retention | Bounded work with explicit missed-data risk and reproducible diagnosis. |
| rejected | Optimize only for digest size | Can hide errors and produce attractive but meaningless token-reduction percentages. |

## Implementation instructions

1. Represent read coverage with start/end offsets, file identity, truncation/rotation events and omitted ranges. Do not convert a partial scan into a healthy result.
2. Test move/create and copytruncate rotation, same-size replacement, partial UTF-8 and very long lines. Choose explicit replay/deduplication policy for each case.
3. Apply sanitation before model-facing truncation and preserve bounded safe error signatures. Keep full raw logs only in owned access-controlled storage, not in prompts or packages.
4. Resume from cursor/digest checkpoints instead of rereading entire logs. Cursor corruption or uncertain identity should produce visible uncertainty and a bounded recovery path.
5. Prune only registered stale artifacts after acceptance and retention checks. Never let an observer delete active application logs or erase evidence needed by an unresolved failure.

## Acceptance tests to implement and run

- [ ] An error split across two writes is detected once the line completes.
- [ ] An omitted interval yields a coverage-gap status, never a claim of no errors.
- [ ] Rotation/replacement does not inherit an unrelated offset silently.
- [ ] A planted credential at a truncation boundary is absent from model-facing excerpts.
- [ ] Cleanup preserves active/unresolved evidence and rejects unregistered paths and symlinks.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure bytes actually read, duplicate bytes, omitted intervals, detection recall and digest size. The repository's synthetic >99% reduction is not a universal production saving.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Secret redaction is best effort, not a proof that arbitrary raw application output is safe to disclose. Sensitive logs may require stronger policy or no model access.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **058** now implements this recommendation; task **059** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
