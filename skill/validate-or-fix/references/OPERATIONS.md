# Standalone validation operations

Load only for map maintenance, supervision policy, recovery or cleanup. No planning references are required.

## Map the actual test

```bash
python <skill-dir>/scripts/service_map.py check --repo-root .
python <skill-dir>/scripts/service_map.py init --repo-root .
```

`init` creates a draft only when absent. Inspect the relevant package/build/test/container inputs, discover the command and its services, then edit the JSON block of `.ai-work/SERVICE_MAP.md`. Keep existing validations; never replace the whole inventory with this example:

```json
{
  "id": "UNIT",
  "name": "Unit tests without external services",
  "command": ["python", "-m", "unittest", "discover"],
  "resources": [],
  "toolchains": ["PYTHON"],
  "no_progress_timeout_seconds": 300,
  "expected_duration_seconds": 600
}
```

This example assumes Python and no external dependency after review. Add a matching toolchain entry with `id: PYTHON` and `command: ["python", "--version"]`. Map real database/browser/server dependencies instead of copying `resources: []` blindly. Mark `inventory_reviewed: true` only after discovery is complete, then:

```bash
python <skill-dir>/scripts/service_map.py stamp --repo-root . --confirm-reconciled
python <skill-dir>/scripts/service_map.py list --repo-root . --validation UNIT
python <skill-dir>/scripts/validatectl.py run --repo-root . --validation UNIT
```

The stamp records reviewed input fingerprints; it does not discover resources or prove the inventory correct. The list command emits only the selected validation's prerequisites.

## Supervision and progress

Supervise from invocation, not after five minutes. The existing resource watcher owns the test process tree, performs bounded toolchain/health probes, and distinguishes resource failure from implementation failure.

- `no_progress_timeout_seconds`: sliding per-command idle window, not total test-set duration; `0` disables. Meaningful output, configured progress signals/files/probes and supported process-tree activity renew it.
- `validation_hard_timeout_seconds`: separate explicit ceiling; `0` disables. Reaching it blocks for review, not model escalation.
- `expected_duration_seconds > 300`: prompts the host to instrument long work; it does not change a timeout.
- `stop_on_unhealthy: true`: opt-in cancellation of the owned test tree after a mapped resource check is unhealthy beyond its grace period. The default remains false. Configure trustworthy targeted checks; a word like ERROR in unrelated logs is not proof the test must be killed.

For long jobs, emit flushed completed-work counters such as `PROGRESS stage=tests done=12 total=80 seq=12`. Repeated heartbeats prove liveness only. Prefer a real increasing counter or completed-work event over noisy timestamps; CPU activity alone can also be a busy loop. Add observability before repeatedly increasing timeouts.

Do not launch a second supervisor for an already-running plan validation. Plan runners keep their own acceptance, retry and checkpoint authority. This standalone controller is for a validation without a plan.

## Receipts, logs and bounded evidence

Only `.ai-work/validation/<ID>/` is owned by this controller, with `.validate-or-fix` provenance and `state.json`. No `manifest.json`, `TODO.md`, `.orchestrator-plan` or `.active-plan.json` is created.

Raw stdout/stderr capture keeps an 8 MiB prefix by default and a 64 KiB rolling tail. `--max-log-bytes` accepts 64 KiB through 64 MiB. Output continues to be drained after the retention limit; omitted byte counts are explicit. Structured watcher reports record policy/progress/health evidence separately. External service logs are read-only and never truncated here.

```bash
python <skill-dir>/scripts/validatectl.py status --validation UNIT
python <skill-dir>/scripts/validatectl.py inspect --validation UNIT
```

`status` does not advance a cursor or call an AI. `inspect` returns a roughly 4 KiB packet of redacted, hash-deduplicated evidence; its bounded tail scan does not reread a whole log. After rotation/new run, the cursor uses the new receipt generation. Large omitted regions remain an evidence limitation, not proof no earlier error exists. Redaction is best effort: review confidentiality before enabling external AI advice.

Repair routing uses the canonical logical tier ladder. Successful validation resets the attempt budget; changed map fingerprints start a new contract. Environmental errors, interrupted hosts, quota and explicit ceilings do not raise model intelligence. Unknown/technical failures follow evidence-based escalation, with a configurable `--max-attempts` default of five. The controller recommends a repair route but never dispatches an implementation model or executes an inferred fix.

## Recovery and cleanup

A live owner or supervisor prevents duplicate execution. A remote owner is treated conservatively. To recover a dead local controller without starting any test:

```bash
python <skill-dir>/scripts/validatectl.py recover --validation UNIT
```

Review preserved evidence before `recover --reset-attempts`; this is an explicit retry-budget reset, not a fix. A stale observer lock is fail-closed: confirm its process has ended before removing that specific lock; never use a broad cleanup command to override a live owner.

After validation passes and the user-facing outcome has also been checked:

```bash
python <skill-dir>/scripts/validatectl.py cleanup --validation UNIT
```

Cleanup preflights recognized files, rejects symlinks, refuses failed/active/interrupted evidence and does not accept paths from logs or model output. It removes only owned run logs/reports and evidence/observer cursors; it preserves the compact receipt, reusable map, product source, tests and unrelated files. It never cleans application logs or invokes `git clean`. Ordinary plan lifecycle commands do not mistake this directory for a plan.

## Limits

The host must run the controller and perform authorized repairs. The library does not schedule itself, keep this chat running, or guarantee durable disk storage across hosts. Native Windows and paid provider behavior must be checked in the deployment environment; offline adapter tests are not live-account validation. Unknown CLI permissions or protocol drift cause a safe skip, not relaxed permissions.
