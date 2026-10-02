# Delegation policy and role contracts

Load this reference only when deciding whether to spawn a worker. The decision is deterministic and costs no model tokens:

```bash
python scripts/routingctl.py delegate --request request.json [--telemetry <plan-dir>] [--catalog catalog.json]
```

Output schema `delegation-decision/1`: `decision` (`tool` | `keep_root` | `delegate`), `reasons`, `blocked`, `floor`, `role`, `route` (provider/model/tier/effort from the selector), `sticky` (selector signal), `fan_out`, `depth`, `budgets`, `write_scopes` (one per worker) and `accounting`.

## Request

`signals` (leaf signals as for `route`), `providers` (configured ids in preference order), `agent_tier` (tier of the agent asking; root at depth 0), optional `depth` (0), `independent_units` (1), `read_only` (false), `write_scopes` (one non-empty path list per unit when writing), `unit_tokens` (estimated work per unit, 0), `token_budget`, `rollup`, `role`, `previous_route`, `cache_affinity`, `required_capabilities`, `availability`, `billing`.

## Rules, in order

1. Floor from `minimum_route`. A `tool` floor returns `tool`: run the deterministic command, spawn no worker.
2. Capability gap: the floor tier is above `agent_tier`. The work must be delegated; overhead, affinity and sticky rules do not apply, and the agent never keeps it (that would lower the floor).
3. Depth: `MAX_DEPTH = 1` — the root (depth 0) spawns workers; workers do not spawn. The only depth>1 exception: a depth-1 worker facing a capability gap may spawn exactly one read-only worker at `EXCEPTION_DEPTH = 2`, never deeper. Otherwise a depth limit returns `keep_root`, or a blocked `delegate` when there is a gap (the worker reports a `semantic` failure for escalation).
4. Without a gap, keep the work at the agent when the selector applies sticky routing (`sticky_route`: warm cache on the current route), when one sequential unit has high cache affinity (`high_affinity_sequential`), or when coordination overhead dominates. Per-worker overhead is `WORKER_OVERHEAD_TOKENS = 3000` (brief 2000 + compact result 1000); delegate only while `overhead / (overhead + unit_tokens)` stays at or below `COORDINATION_OVERHEAD_MAX = 0.25`, i.e. `unit_tokens >= 9000`.
5. Route comes from `select_route`, so floors, configured providers and empty tiers follow the selector: no candidate keeps the work (no gap) or blocks it (gap). Providers outside the request are never listed.
6. Limits: fan-out `read_only: 4`, `write: 2` workers, and 1 at the exception depth. Overlapping write scopes collapse to one worker owning their union. `tokens_per_worker = min(unit_tokens + 3000, MAX_WORKER_TOKENS = 200000)`; fan-out also shrinks to `remaining_tokens // tokens_per_worker`, and zero affordable workers keeps the work (no gap) or blocks (gap).

## Token accounting

`accounting` reads the `scripts/routing_telemetry.py` rollup of the plan's `telemetry/attempts.jsonl` (`--telemetry <plan-dir>` or a `rollup` object) and charges `input_tokens + cache_write_tokens + output_tokens` across every worker kind: `root`, `subagent`, `retry`, `diagnostic`, `summary`. Cached reads stay visible in the rollup but are not charged. A rollup missing a kind is rejected; a truncated rollup falls back to its totals. Unreported usage stays null and is never estimated; units stay native.

## Role contracts

| Role | Writes | Contract |
|---|---|---|
| `scout` | no | Read-only discovery; return located facts with file/line evidence. |
| `analyst` | no | Read-only decision or risk analysis; return one recommendation with evidence. |
| `verifier` | no | Independent validation; run the named checks and report pass/fail evidence. |
| `implementer` | own scope | Bounded edit inside its write scope; run its validation. |
| `debugger` | own scope | Reproduce, fix and validate one defect inside its write scope. |

The brief carries the goal, role, write scope, validation and budgets only (at most 2000 tokens); never telemetry, transcripts or unrelated context.

## Compact result schema

Every worker returns exactly these keys, at most `RESULT_MAX_BYTES = 4000` serialized bytes:

```json
{"status": "done", "role": "scout", "summary": "<= 360 chars",
 "findings": [{"file": "path", "line": 1, "claim": "..."}],
 "changed_files": [], "validations": [{"command": "...", "passed": true}],
 "blocked_reason": null}
```

`status` is `done` or `blocked`; `blocked_reason` is set exactly when blocked. Limits: 8 findings, 8 validations, 50 changed files, all inside the worker's write scope (read-only roles change nothing). `routingctl.check_worker_result` enforces this before the root consumes a result.
