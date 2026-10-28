# Plan 1 source checkpoint

This checkpoint preserves the verified work available on 2026-10-28. It is not a
completed implementation of Plan 1 or Plan 2.

- Product baseline: version 0.11.0, remote main commit `193fefd96a3a8d9f2b4a655f237071fdf7c211f8`.
- Plan 1: `.ai-work/20261028-skill-study-provider-switch/`, all 86 tasks pending.
- Preserved work: native plan and task definitions, requirements, research protocols,
  delivery-checking tools and their tests, source inventory, routing reproduction
  scripts, execution logs and diagnostic evidence.
- Latest native runner outcome: exit 75, paused at task 001 because neither allowed
  maximum-tier provider CLI was available. No independent review was fabricated.
- Product files under `skill/`, `bin/` and `lib/` are unchanged from the baseline.
- Plan 2 has not been generated. `PLAN2_CONTRACT.md` specifies the future delivery.
- The complete-suite pass preserved under `execution-20261028/` is historical
  evidence for the baseline, not validation of new functionality or a fresh run.

The plan directory is intentionally versioned for the requested handoff despite
`.ai-work/` being ignored by default. Empty required `logs/` and `learnings/`
directories have `.gitkeep` files so a Git checkout preserves them. No live runner
lease, credentials, dependency directories or bytecode cache are included.

The native manifest contains its original absolute workspace path. Follow
[PORTABILITY.md](PORTABILITY.md) on another host; do not edit statuses manually.
The chronological preparation and retry reports remain unchanged, including
statements that no commit or push had happened at the time they were written.

This publication changes only a new checkpoint branch; it does not merge into
`main`, publish an npm release, install skills or execute authenticated models.
