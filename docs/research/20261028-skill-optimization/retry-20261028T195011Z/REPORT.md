# Plan 1 retry and pre-review evidence

Date: 2026-10-28. Source version: 0.11.0.

**Status: native execution paused; 0/86 tasks completed.**
This is a preparatory evidence packet, not an independent review or a completed task.

## What was actually run

- Restored the previous checkpoint without changing the product code.
- Native `planctl_concise.py validate` and `audit`: exit 0.
- Native `run_concise.py --no-wait --no-cleanup`: exit 75.
- Post-attempt lifecycle status: 86 pending, no active runner.
- No worker attempts and no functional failures.
- Provider command discovery: claude, codex, agy, gemini, qwen, kimi, trae-cli and muse absent from PATH.
- The conventional Claude/Codex/Gemini authentication files and the checked provider API-key variables are absent. No credential values were inspected or recorded.

Runner message:

```text
PAUSED: Task 001 pending: no allowed provider for implementation/max (claude:missing_cli, codex:missing_cli). Resume after availability recovers or update configuration.
```

## Additional local evidence (no model calls)

The attached `pre_review_probe.py` replays 10 scenarios against the real routing code.
It constructs but **never runs** provider command lines. Availability is a synthetic
fixture, model names are fixture labels, and this does not verify real model availability,
quality, prices, subscription quota or savings. No global user configuration is loaded.

| User-equivalent fixture | Observed result | Exact repeated command signatures |
|---|---|---:|
| strong/high, unknown | 8 attempts; Antigravity never dispatched | 5 |
| max/high, semantic | Stops at ladder_exhausted before Claude is dispatched | 2 |
| standard/medium, unknown | 6 attempts dispatch a provider different from the intent provider | 4 |
| standard/medium, mechanical | Codex never dispatched; 4 intent/dispatch mismatches | 6 |
| advanced/high, unknown | AvailabilityError for codex/advanced before first dispatch | 0 |

Command signatures are SHA-256 hashes of the complete builder-generated argv with a
constant prompt and normalized temporary paths. A repetition is an additional occurrence
of the same argv; this is more precise than comparing only the logical tier label.
These are characterization results for the old code, **not passing tests of a fix**.

## Read code and causal links

- `run_isolated.py:301-347`: intent chain is selected from the declared tier; global
  failure count chooses a provider slot; accumulated failure classes select that provider's rung.
- `availability.py:116-173`: dispatch rebuilds the chain from the escalated tier and
  applies the failure slot again, without preserving the intent provider.
- `run_isolated.py:2152-2169`: accumulated classes can exhaust the last provider's ladder
  before that provider has run.
- `workload_routing.py:121-162`: the disabled-workload path raises for an empty tier in
  any provider in the chain, rather than lifting that provider to the next available tier.
- `routingctl.py:214-264`: tier lifting exists, while escalation is capped on logical rungs;
  deduplication of effective command signatures is not performed in this path.
- `runner_contract.py:80`: calls `failure_context(task)` without the available plan directory.

The code hashes and detailed traces are in `pre-review-routing-probe.json`.

## Why all formal tasks are still pending

The saved graph makes all 85 other tasks transitively depend on task 001, an initial
independent max-model review. The original request explicitly requires a code review
at the end of each topic; it does not explicitly require blocking the initial code audit
on that first review. The global initial barrier was introduced in the planning design.

A possible local amendment is to stage author work while retaining independent review
as a mandatory acceptance gate. This is a proposal, not an applied change: no dependency,
review requirement, task status or global provider setting was altered in this retry.
The protocol still governs native execution. No reviewer identity or session was invented.

## Integrity and limits

All 135 tracked files under `skill/`, `bin/` and `lib/` match local HEAD `6e6ba53`.
The 188 tracked baseline files remain present. Source changes: none.
The full npm suite was **not rerun in this retry**; the earlier full-suite logs remain
in the checkpoint and are not relabeled as fresh test results.
No commit, push, PR, npm publication, skill installation or paid provider execution occurred.

## Reproduce the diagnostic only

```bash
python docs/research/20261028-skill-optimization/retry-20261028T195011Z/pre_review_probe.py \
  --repo-root . --output-dir /tmp/pae-routing-evidence
```

Replace retry-20261028T195011Z with this directory's actual name. This command performs only the
fixture replay and writes evidence; it does not resume or complete the plan.
