# P067 — Manager-tier delegation for plan supervision

**Architecture decision for future implementation (2026-11-20).** This is not code, a test, a benchmark or an independent review. Load it only for tasks 131/132. No model was called and no new external research was done to prepare it; every claim below is checked against files in this repository.

## 1. Problem

Today the skill elevates plan *leaves*: `MODEL_ROUTING.md` section 3 ("Elevate by delegation. Never switch the root session") and `routingctl.py delegate` (rule 2, capability gap) send a leaf whose floor is above the root tier to a fresh stronger worker, and the runner routes worker tasks itself. The plan *manager's* own mid-run decisions are not covered. When a task blocks (runner exit 4), a gate or plan defect appears, a replan is needed, two reviews conflict, or a high-impact manifest mutation is proposed, `run_isolated.py`, `watchdogctl.py` and `keepalivectl.py` only report (`WATCHDOG.md`: "Blocked is a decision, not a crash"). If the root is a small model (Sonnet 5.5 = `standard`, Haiku 5.5 = `economy`), that root makes a decision whose floor is `strong` or `max` — the same capability gap the leaf rule forbids.

## 2. Decision

Treat each supervisory decision as a read-only leaf and reuse the existing gate. Add one deterministic entry point, `routingctl.py supervise`, built on `delegate_decision`, `select_route`, `frontier_policy`, the availability classes and `check_worker_result`. Do not add a second router, selector, watchdog, scheduler or availability classifier. A separate `supervisorctl.py` was rejected: it would duplicate the floor table, the provider chain and the budget accounting that `routingctl.py` already owns. Extending `watchdogctl` suggestions alone was rejected: the watchdog must stay model-free and must never select a provider.

## 3. Contracts (checkpoints S001-S007 of task 131)

**C1 Manager tier.** `routing_policy.manager_tier` takes `auto | economy | standard | advanced | strong | max`. `auto` resolves to `standard`: a manager of unknown strength is assumed to be below `strong`, so hard decisions are delegated. `routing_config.py` validates the key; the catalog refresh in `routingctl.py` (which rebuilds `routing_policy` and today carries over only `frontier`) must carry it over too. A `--manager-tier` CLI value overrides the config for one call. The effective tier and its source (`cli | config | auto_default`) are recorded in the decision, the diagnosis-request record and the telemetry row. The root session's model or effort is never switched (section 3 of `MODEL_ROUTING.md`).

**C2 Supervisory decision.** Input: an event, the manager tier, configured providers, current availability, the failure capsule path and blocker fingerprint, and the task's recorded failure history. Event table (signals are existing `PRIMARY_SIGNALS`; no new floor is invented):

| Event | Signals | Floor | Role | Phase chain |
| --- | --- | --- | --- | --- |
| `blocked_task` | `subtle_debugging`, `silent_failure_costly` | strong/high | analyst | review: Codex > Claude |
| `plan_defect` | `architecture_decision` | strong/high | analyst | architecture: Codex > Claude |
| `gate_defect` | `silent_failure_costly` | strong/high | verifier | review: Codex > Claude |
| `replan` | `architecture_decision`, `cross_cutting_risk` | strong/high | analyst | architecture: Codex > Claude |
| `review_conflict` | `repeated_strong_failure` | max/xhigh | verifier | review: Codex > Claude |
| `manifest_mutation` | `cross_cutting_risk` | strong/high | analyst | architecture: Codex > Claude |
| `extreme_architecture_review` | `extreme_architecture` | max/xhigh, frontier-eligible | analyst | architecture: Codex > Claude |

Output schema `supervision-decision/1`: `decision` (`keep_root` when the manager tier is at or above the floor, `delegate`, `report_only`, `duplicate`), `reasons`, `event`, `floor`, `role`, `read_only: true`, `route` (from `delegate_decision`), `provider_chain` (ordered, with skipped providers and reasons), `repair_chain` (`antigravity > codex > claude`, informational: an implementation repair is created only through task 091), `frontier` (`allowed`, `reason`, `auto_dispatch: false`), `brief`, `result_schema`, `budget`, `manager` (`tier`, `source`) and `root_model_switch: false`.

**C3 Block record and surfacing.** On a functional block (`semantic`, `mechanical`, `plan_defect`, `ladder_exhausted`) `run_isolated.py` atomically writes `results/<task>-diagnosis-request.json` (`diagnosis-request/1`: task id, event, failure class, failure-capsule path and sha256, blocker fingerprint, source fingerprint, manager tier, `status: requested`, the `routingctl.py supervise` command). Fingerprint = sha256 of canonical JSON over task id, event, failure class, normalized blocker reason, capsule sha256 and source fingerprint. The same fingerprint is never written twice. `watchdogctl.py` reports it as `ANOMALY:diagnosis_requested:delegate_diagnosis <plan>/<task> <record path>`; `keepalivectl.py` prints the same line and never relaunches for it. The runner, watchdog and keepalive never edit the manifest, never resolve a blocker and never dispatch a worker, least of all a frontier route. Resolution goes through task 091's lease-safe, replayable graph mutation, called by the manager after it reads the diagnosis result.

**C4 Availability is not capability.** `quota`, `credits_exhausted`, `billing`, `auth`, `environmental`, `budget` and `timeout`/`timeout_ceiling` blocks, and `unknown` causes (consistent with task 099), write no record, spend nothing and escalate nothing: `supervise` returns `report_only` with reason `availability_fault`. When Codex credits are exhausted, Codex is skipped in `provider_chain` with reason `availability` and the decision goes to Claude (Opus 5.5) at the same floor. No escalation or capability failure is recorded (`MODEL_REFRESH_20261120.md`, owner policy).

**C5 Read-only boundary.** Diagnosis roles are `analyst` or `verifier` only, so `changed_files` must be empty. A diagnosis is dispatched only through the adapter-pinned read-only argv in `run_isolated.py` (Claude `--permission-mode plan`, Codex `--sandbox read-only`; an adapter without a provable read-only mode fails closed and is skipped with reason `no_read_only_mode`). This holds even though implementers run full-access (task 093).

**C6 Accounting.** Each dispatched diagnosis is one telemetry row of the existing kind `diagnostic` (`routing_telemetry.KINDS`), carrying the event, manager tier and fingerprint. `delegation_accounting` already charges every kind against `token_budget`. Bounded budget: at most 2 diagnoses per task and 8 per plan run, plus the token budget. Beyond either limit `supervise` returns `report_only` with reason `diagnosis_budget_exhausted`.

**C7 Frontier.** Fable 5.2 / Astra 6.2 are used only under the owner's existing rules. Way (1): `extreme_architecture_review` on a read-only analyst while `routing_policy.frontier.enabled` is true. Way (2): `min_top_failures` (default 2) functional failures (`semantic`, `mechanical`, `unknown`) at the max/xhigh rung recorded for the same task, for a diagnosis event in the review/architecture phase. Never for quota, auth, environment, budget or timeout. In both cases `frontier.auto_dispatch` stays `false`: the manager dispatches explicitly.

## 4. Brief and result

Brief (at most `BRIEF_MAX_TOKENS = 2000`): event, task id, goal question, failure-capsule path and sha256, blocker and source fingerprints, acceptance ids, allowed reads (capsule, task definition, named source paths), validation commands, `read_only: true`. It never carries transcripts, raw logs, telemetry or unrelated task context. Result: the compact schema of `DELEGATION.md` (`check_worker_result`), with `changed_files: []`, plus a required `recommendation` in `retry_same_route | repair_task | replan | owner_decision | no_action`, at most `RESULT_MAX_BYTES = 4000`.

## 5. Legacy compatibility

When `routing_policy.manager_tier` is absent, the runner writes no diagnosis-request record, and the output and exit codes of the watchdog and keepalive stay byte-identical. Schema 1-4 manifests load unchanged. `supervise` stays callable by hand and then treats the manager as `auto`.

## 6. Required test cases (`test/optimization/manager_delegation_self_test.py`, offline)

1. Sonnet 5.5 manager (`standard`) with a semantic `blocked_task`: `delegate` to a read-only Opus 5.5 / Sol 6.2 analyst at strong/high.
2. Haiku 5.5 manager (`economy`): `delegate` for every event.
3. Manager at the floor (`strong` for `blocked_task`): `keep_root`.
4. Codex credits exhausted: the chain skips Codex (availability) and Claude is chosen; no escalation is recorded.
5. Quota or environment block: `report_only`, no record, no dispatch.
6. Duplicate fingerprint: one record and one diagnosis, then `duplicate`; the budget limit returns `report_only`.
7. Frontier is never chosen for diagnosis unless way (1) or the repeated-failure rule holds; `auto_dispatch` is always false.
8. No root model switch: `root_model_switch` is false and the manager tier is never rewritten in config.
9. A legacy plan without `manager_tier`: no record, and watchdog/keepalive output is unchanged.

## 7. Ordering and scope

Write scope: `routingctl.py`, `routing_config.py`, `watchdogctl.py`, `run_isolated.py` (block record only), `keepalivectl.py` (surfacing only), `routing_telemetry.py`, `DELEGATION.md`, `WATCHDOG.md`, `MODEL_ROUTING.md`, `ROUTING_CONFIG.md` and the new test. Shared-file rule (review A8): task 131 runs after the accepted earlier writers of those files, which are reviews 088, 092, 100, 104, 106, 108, 116, 120 and 130. Its independent review 132 gates integration 082. Routing: implementation at `strong`/`high` (Antigravity > Codex > Claude), review at `max`/`xhigh` (Codex > Claude).

## 8. Limitations

Nothing here is measured. Diagnosis savings, the token cost per diagnosis and decision quality by manager tier are unknown until real runs exist. Model facts follow `docs/research/MODEL_REFRESH_20261120.md`.

## Sources (internal, read 2026-11-20)

- `skill/plan-and-execute/references/MODEL_ROUTING.md` section 3; `DELEGATION.md` (rules, accounting, compact result schema); `WATCHDOG.md` (classes, keepalive safety rules, watcher routing); `ROUTING_CONFIG.md` (frontier level).
- `skill/plan-and-execute/scripts/routingctl.py` (`PRIMARY_SIGNALS`, `delegate_decision`, `delegation_accounting`, `check_worker_result`, `routing_policy` rebuild); `run_isolated.py` (read-only adapter table, exit 4 path); `routing_telemetry.py` (`KINDS`); `routing_config.py` (`_frontier`).
- `docs/research/MODEL_REFRESH_20261120.md` (owner policy); `docs/research/20261028-skill-optimization/PLAN_ARCHITECTURE_REVIEW_20261120.md` (A3, A8, A9); plan tasks 087, 091, 099, 105, 115.
