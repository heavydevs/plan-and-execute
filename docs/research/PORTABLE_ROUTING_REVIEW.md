# Portable model routing: final maintenance review

Reviewed 2026-10-01 against base `12d9213` plus the uncommitted working tree, following `skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md` (items 1-8).

## Scope traced

Entrypoint `SKILL.md` -> `MODEL_ROUTING.md` (+ one provider guide) -> `MODEL_CATALOG.md` / `DELEGATION.md` / `ROUTING_CONFIG.md` / `TEST_RESOURCE_MONITORING.md`, then to `routingctl.py`, `routing_config.py`, `model_catalog.py`, `model_catalogctl.py`, `routing_telemetry.py`, `run_isolated.py`, `resource_watch.py`, `planctl.py`, `preplanctl.py`, their self-tests, and the repo tools (`doc_baseline.py`, `routing_eval.py`, `skill_benchmark.py`, `worktree_audit.py`, `run-repo-checks.js`).

Lazy loading holds: `SKILL.md` names `MODEL_CATALOG.md` and `DELEGATION.md` as load-on-demand. `MODEL_ROUTING.md` loads exactly one provider guide. The size budgets in `validate-skill.js` still pass (SKILL.md 6,969 of 7,167 chars; ORCHESTRATION.md 11,999 of 12,000).

## Findings repaired in this review

| # | Contradiction or stale reference | Repair |
|---|---|---|
| R1 | `SKILL.md` and `MODEL_ROUTING.md` said "do not preload **both** provider guides", but there are now five guides. | Changed to "other provider guides/files". Updated the pinned text in `tools/validate-skill.js` and `model_routing_self_test.py`. |
| R2 | `MODEL_ROUTING.md` said "the runner does not call `select` yet", but `ROUTING_CONFIG.md` documents `routing.auto_select: shadow/on`, which the runner implements. | Now says: no `select` call only while `auto_select: off` (the default), and points to `ROUTING_CONFIG.md`. |
| R3 | The `MODEL_ROUTING.md` §4 tier table and `ORCHESTRATION.md` listed four tiers. Code, `PLAN_SPEC.md` and the catalog use five, including `advanced`. | Added the `advanced` row and the skip-upward rule. |
| R4 | `PLAN_SPEC.md` and `PLANNING_PROTOCOL.md` said concrete ids always come from the catalog snapshot. By default (`model_resolution: config`) they come from provider `models`. | Both now name config as the default and the snapshot as opt-in. |
| R5 | `MODEL_CATALOG.md` described the bootstrap as Claude/Codex only, at `bootstrap-v1`, and omitted optional schema fields. | Now lists all five bootstrap providers and points to the live `catalog_version`. Documents `effort_map`, `thinking`, `cached_input_per_mtok`, `plan_credits` and `off_peak`. |
| R6 | `MODEL_ROUTING_GLM.md` and `MODEL_ROUTING_MUSE.md` hard-coded `bootstrap-v3`; the code is at `v4`. | Both now refer to the current version in `model_catalog.py`, so they cannot go stale again. |
| R7 | The plan-local `MODEL_MATRIX.json` snapshot, `status/diff/refresh --plan`, `reclassify` and the `model_resolution` key were not in any reference. | New section in `MODEL_CATALOG.md`; `model_resolution` section in `ROUTING_CONFIG.md`. |
| R8 | `DELEGATION.md` cited "TODO 015", an ephemeral plan id. | Now cites `scripts/routing_telemetry.py` and `telemetry/attempts.jsonl`. |
| R9 | The monitor artifact registry (`registry.jsonl`) and `resource_watch.py cleanup` were undocumented. | New subsection in `TEST_RESOURCE_MONITORING.md`. |
| R10 | `expected_quiet_seconds`/`progress_regex` read as if they applied on every host, but the in-run stall monitor is POSIX-only. | Added a POSIX-only note. |
| R11 | The configure text listed four tiers, but the wizard derives tiers from configured models, including `advanced`. | Text now matches the code. |

## New behavior: trigger, default, persisted evidence, recovery

| Behavior | Trigger | Default | Persisted evidence | Recovery outcome |
|---|---|---|---|---|
| Shared model catalog cache | `model_catalogctl.py refresh`; a facet past ttl; CLI version change | Fresh cache makes zero source calls; empty cache falls back to bootstrap and writes nothing | `<cache root>/<provider>/catalog.json` with revision, digest and provenance | A failing or invalid source keeps the last valid cache and warns; lock goes stale after 120 s; a crash before replace leaves the old file |
| Plan snapshot `MODEL_MATRIX` | `planctl create`; `refresh --plan`; `reclassify` | Captured at create; runner ignores it unless `model_resolution: snapshot` | `MODEL_MATRIX.json/.md`, audit (last 50 entries), manifest events `model_matrix_created/skipped`, `task_reclassified` | Catalog failure leaves the plan valid. A stale snapshot only warns. An invalid model id triggers one refresh and a redispatch, then `plan_defect`. A provider missing from the snapshot needs a fresh cache, otherwise the runner stops with guidance |
| Candidate selector `routingctl select` | Explicit CLI call or `auto_select` shadow/on | Pure, opt-in | Explanation stages in output | No candidate: the ladder route runs |
| Auto-selection rollout | `routing.auto_select` | `off`; `on` runs only for allowlisted segments that pass the gates, on first attempts | `telemetry/shadow.jsonl` with `auto.reason` | Selector or gate errors fall back to the ladder; retries stay on the evidence ladder; the committed report passes no segment |
| Delegation decision `routingctl delegate` | Called before spawning a worker | `MAX_DEPTH=1`, overhead cap 0.25, fan-out 4 read-only / 2 write | Output only (`delegation-decision/1`) | Capability gap with no candidate: blocked, and the worker reports `semantic` |
| Attempt telemetry | Every runner attempt | On; metadata only | `<plan>/telemetry/attempts.jsonl` (registered `keep`) | Write failures are printed and never stop execution; missing usage stays null |
| Provider profiles (gateway, GLM, DeepSeek) | `<provider>.profile` in config | None; argv unchanged without a profile | Env-var names only in config | A missing variable fails before spawning and names the variable |
| Muse native provider | `muse` configured | Not in `provider_order`; permission flags off | Normal results/logs | Summary fails closed and falls back to the deterministic summary |
| `advanced` tier, F/L aliases | Plan or TODO tier | Claude and Codex have no `advanced` model | Only canonical names are stored | Empty tier skips upward, never downward |
| Stall policy keys | `expected_quiet_seconds`, `progress_regex` per validation | 0 / none | Watcher log, process snapshot | Invalid regex is a configuration error before the test starts; POSIX only |
| FailureEvidencePacket | Any failed validation | 4 KiB budget | `logs/<task>-attempt-<n>-evidence.json` (`on-task-end`) | Stale map gives `block_scope=service_map`; assistant output is advice only |
| Monitor artifact registry | Watcher and telemetry writes | Scope `temporary` outside the runner | `.ai-work/resource-watch/registry.jsonl` | Task scope is cleaned on completion and plan scope at plan end; files on failed tasks are kept for diagnosis |
| Preplan working-set / density triggers; `prepare` rollback | `preplanctl assess/prepare` | Duplicate blocks counted once; density >= 40 at >= 8k tokens | `SOURCE_INDEX.json`, package | A failed primary-plan creation removes the package so `prepare` can be retried |
| Windows `spawnable()` | Any watcher command on Windows | Resolves PATHEXT shims via `shutil.which` | None | Missing executable is recorded as unhealthy |

## Checklist items 5-7

- **Tooling (5):** each new script has one bounded job and a JSON CLI: catalog validation, cache/snapshot control, telemetry rollup, doc baseline, eval, benchmark and worktree audit. No model is asked to rediscover catalog or route facts.
- **Token surfaces (6):** worker prompts never include snapshot paths, economics or telemetry (see the `run_isolated.py` comments and the `DELEGATION.md` brief rules). The latest-failure capsule replaces raw logs, and only the immediately preceding log may be opened.
- **Map and cleanup (7):** `service_map.py check` reports only changed paths. This review edited `model_routing_self_test.py`, then re-ran `stamp --confirm-reconciled`; validation ids and resources are unchanged. Plan cleanup removes the plan scope and then the plan directory; `SERVICE_MAP.md` and the shared catalog cache survive.

## WORKTREE_AUDIT keep hunks

Later TODOs edited `resource_watch.py` and `run_isolated.py`, so four audited headers no longer match `git diff` exactly. The content is still present:

| Audited header | Current location |
|---|---|
| `resource_watch.py @@ -9,6 +9,7 @@` (`import shutil`) | `resource_watch.py:13`, now in hunk `@@ -11,0 +13 @@` |
| `run_isolated.py @@ -597,6 +597,31 @@` (`antigravity_schema_text`) | `run_isolated.py:996` |
| `run_isolated.py @@ -659,7 +684,7 @@` (antigravity `--json-schema`) | `run_isolated.py:1086` |
| `run_isolated.py @@ -883,7 +908,7 @@` (status string check) | `run_isolated.py:1325` |

`tools/worktree_audit.py check` (validation `WORKTREE_AUDIT`) still fails until someone regenerates those headers. The fix belongs to the owner of the audit file, not to this review.

## Open findings (not repaired: behavior or code outside the review scope)

- `routing_telemetry.append_record` registers `attempts.jsonl` with `keep` retention inside the plan directory. Plan cleanup deletes the file, but `cleanup_artifacts` never removes `keep` entries, so `registry.jsonl` keeps accumulating dangling lines.
- `cleanup_artifacts` drops eligible registry entries outside `.ai-work/` without deleting the files. This is safe, but those files are then untracked.
- `model_resolution` and `routing_shadow` are top-level config keys that `routing_config.py` does not validate. Unknown `model_resolution` values silently behave as `config`.
- Code comments and docstrings cite plan-local ids (`PAT003`, `PAT004`) in `routing_telemetry.py`, `run_isolated.py` and `delegation_self_test.py` ("TODO 015").

## Unverified platform and provider limits

- **Windows:** `resource_watch.py` has no process-group CPU sampling and no in-run stall monitor (`progress_monitor_enabled` is POSIX-only). `no_progress_timeout_seconds`, `expected_quiet_seconds` and `progress_regex` do not terminate a hung test there. Only cross-attempt signature aging and the framework's own timeouts apply.
- **Windows:** `LongPathsEnabled=0` limits deep temporary paths in tests. Tests mock executable resolution instead of relying on host CLI shims.
- **Live providers:** no live call was made. Unverified: the Muse CLI argv and envelope; Z.AI and DeepSeek Anthropic/OpenAI-compatible endpoints; the DeepSeek off-peak window (16:30-00:30 UTC); GLM credit multipliers; Codex rollout-budget abort wording (falls back to `unknown`); invalid-model error wording across providers (`INVALID_MODEL` regex).
- **Economics:** bootstrap prices and ranks are dated 2026-09-30/10-01 evidence. Selector cost ranking and gate verdicts depend on them until a refresh.
- **Rollout:** no segment passes the committed gates, so `auto_select: on` behaves like `shadow`. Real gains are unmeasured.
