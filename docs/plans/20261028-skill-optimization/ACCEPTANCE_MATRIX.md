# Provider-switch acceptance matrix

This is a required future test matrix, not a record of completed implementation tests.
Every case is pending. Exact requirements remain in `REQUEST_ORIGINAL.md`.

| Case | Required observable result | Implementation/design tasks | Independent review |
|---|---|---|---|
| A01 | Disabled option preserves legacy assertions, argv goldens and reference sequences. The ten offline baseline scenarios are stored; new behavior is not implemented. | 070, 072, 074, 078, 080 | 071, 073, 075, 079, 081 |
| A02 | A useful top in the first provider moves the next eligible attempt to the second provider without waiting for the old failure bucket. Define and test mechanical/budget retry exceptions explicitly. | 072, 074 | 073, 075 |
| A03 | Embedded-effort Antigravity slugs and Claude strong=max aliases do not create duplicate effective top attempts. Compare resolved model plus actual dispatched effort, not logical labels alone. | 072 | 073 |
| A04 | The final eligible provider runs before ladder_exhausted in claude/codex and codex/claude fixtures. Persist evidence per provider/phase; do not replay prior-provider classes blindly. | 074 | 075 |
| A05 | The third strong-chain provider is reachable at max_attempts=8, or a validated and documented budget rule rejects the impossible case. A budget exception must be explicit; no silent success claim. | 070, 074 | 071, 075 |
| A06 | Escalation ladder and actual dispatch use a coherent chain without hidden provider changes or skipped candidates. Include standard-to-strong transitions under the user-equivalent fixture. | 070, 074 | 071, 075 |
| A07 | A missing destination tier lifts upward or skips the provider with a recorded reason, never lowers the floor. Disposition the existing advanced-tier failure outside switching separately. | 072, 074 | 073, 075 |
| A08 | Quota/capacity fallback and exit 75 stay separate from functional failures; fallback-disabled remains pinned. Exercise provider, quota_pool and model cooldown identities. | 074 | 075 |
| A09 | Available-predecessor handoff is redacted before truncation, bounded, validated, unverified and valid for exactly the next attempt. Inject synthetic sk-token and Authorization headers; preserve byte-stable prompt prefixes. | 076, 078 | 077, 079 |
| A10 | Missing, invalid or unavailable predecessor output falls back to deterministic evidence without a model call. Crash, timeout and quota fixtures must retain useful current work-tree evidence. | 076, 078 | 077, 079 |
| A11 | Manifest schemas 1-4, absent failure_classes, full v1 config snapshots and existing availability ledgers remain compatible. Include design-phase counters, reset, snapshots and strict report schema adapters. | 074, 078 | 075, 079 |
| A12 | Switch reason and handoff cost telemetry contain no secrets and preserve rollup/benchmark contracts. Unknown native usage is null; deterministic replay is not measured real-world cost. | 080 | 081 |

Final validation belongs to TODO 080: affected self-tests, `npm ci`, `npm run check`, and
`npm pack --dry-run`, each with actual command, exit code and retained log. TODO 081 reviews
the evidence and exceptions. TODO 086 is the last whole-skill review.

The preparation ran an offline dependency install and three focused routing checks.
Its attempted full baseline ended at the host command timeout, not at a verified suite exit.
No broad validation, new-feature test or real-provider result is marked passed here.
