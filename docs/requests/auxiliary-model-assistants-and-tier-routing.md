# Request: auxiliary model assistants + configurable tier→provider routing

Status: draft request, not yet planned. Intended as a **direct** final-planning input
(`references/PLANNING_INPUT_CONTRACT.md`) — small enough that it should not need primary-plan
staging. A future `plan-and-execute` session on this repo can consume it as-is.

## Summary

Two related capabilities, both about who does the work on a TODO, not what the work is:

1. **Auxiliary assistant models**: let a secondary model help the model that owns a TODO —
   starting with validation-failure triage — instead of every provider call being either "the
   worker" or nothing. Default assistant provider: **Antigravity**.
2. **Configurable, working tier→provider routing**: let a person globally configure which
   provider is primary for each logical tier (`economy`/`standard`/`strong`/`max`) and what its
   fallback chain is, through an **interactive multiple-choice flow** — one question per setting,
   never one bundled question. This also has to actually implement provider fallback on
   availability failure, which today is documented but not wired up (evidence below).

## Evidence this request is grounded in

Found while operating the skill on a real plan (`talepace`, plan
`20260924-004347-pend-ncias-adaptive-learning-v2-livro-progressivo-offline-proteg`), not
speculative:

- **README.md §"Per-TODO model routing" and `references/MODEL_ROUTING.md` §6** document that
  "Provider fallback (quota, rate limit, capacity, CLI interruption) is availability, not
  evidence: state is preserved and the equivalent logical rung runs on the fallback provider."
  This is not what the code does.
- `scripts/run_isolated.py::fail_task` path for `rate_limited=True` only increments
  `task["rate_limit_events"]`; it never touches `functional_failures`/`failure_classes`
  (`planctl.py` ~3178-3185).
- `scripts/run_isolated.py::choose_route` picks the provider slot from
  `functional_failures // functional_failures_per_provider` only (~204-207). Since a rate-limit
  event never increments `functional_failures`, a provider that is rate-limited is **never**
  rotated away from within one `run_concise.py` invocation.
- `scripts/run_isolated.py::wait_after_rate_limit` (~1092-1103) only sleeps and retries the exact
  same command; `scripts/run_isolated.py::execute_one_task` (~1176-1190) either loops back to that
  same wait, or raises `RunnerError` (`auto_wait: false`), ending the run. Neither path calls
  `choose_route` with a different candidate set.
- Net effect, observed live: when the primary provider (Codex) hit its usage limit mid-plan
  (`ERROR: You've hit your usage limit...`), the runner stopped with `Rate/usage limit stopped
  task NNN; rerun the command to resume` every time, requiring a human to relaunch with an
  explicit `--provider` override to make progress. This happened repeatedly across one plan's
  history (7+ manual resumes in its logs).
- Antigravity is already a first-class provider (`README.md` §"Supported AI workers",
  `orchestrator.config.json`'s `antigravity` block, `run_isolated.py`'s antigravity command
  branch), but its config ships with `"models": {"economy": "default", ...}` placeholders, and
  some real Antigravity model ids bake the effort level into the id itself (`agy models`:
  `claude-opus-4-6-thinking`, `gemini-3.8-flash-low`, etc.). Passing `--effort` alongside such a
  model id is rejected by `agy` (`error: invalid model selection (...): --effort is not supported
  for model "claude-opus-4-6-thinking"`) unless the id is listed in that provider's
  `models_without_effort` (`routingctl.py::model_supports_effort`). Any auto-configuration flow
  that lets someone pick concrete Antigravity models must account for this per-model quirk, not
  just per-provider.

## Requirement 1 — Auxiliary assistant role

- Add a provider role distinct from "the worker for this TODO": an **assistant** that reads
  bounded evidence for a task and returns an advisory finding, never a codebase edit and never the
  authoritative `failure_class`.
- First concrete use: **validation-failure triage**, inserted in `WORKFLOW.md` step 6 ("Validate
  independently"), after a mapped validation fails and before the orchestrator calls
  `planctl_concise.py fail --failure-class ...`. Inputs stay inside the skill's existing bounded-
  evidence discipline: the validation id/command from the service map, the existing output tail,
  a window around the first failure match, non-healthy resource-watch samples, `log_watch`
  excerpts, and the repeated-failure signature/age — never the full plan, other tasks, or raw full
  logs.
- Output is a small structured report (suggested `failure_class`, confidence, a short hypothesis,
  and evidence locators/quotes) that gets attached to the orchestrator's decision and to the next
  worker's failure capsule, labeled as advisory/unverified. The orchestrator (or the strict
  runner's deterministic classifier) keeps the final say.
- Must be **opt-in and gated**, not run on every validation: skip trivial/deterministic
  validations (lint, typecheck, formatting-diff checks) where the tool output already is the
  diagnosis; fire only above a configurable repetition/unhealthy-sample/stall threshold, so it
  does not add latency/cost to the common case.
- Default provider for this role: **Antigravity**. Must be overridable per the routing
  configuration in Requirement 2. The invocation profile for this role must default to
  **no write access** (`skip_permissions: false` / a real sandboxed, read-only mode), which is
  different from Antigravity's existing coding-worker profile
  (`skip_permissions: true`, `sandbox: false`) — an assistant that only reads bounded evidence
  handed to it in the prompt needs no repo write access.
- Out of scope for the first version: replacing deterministic test execution
  (`resource_watch.py`) with a model, and letting the assistant's output silently become the
  final `failure_class` without the orchestrator/runner retaining override.

## Requirement 2 — Global, working tier→provider routing

- Let a person configure, once, for the whole skill installation (with a per-plan
  `orchestrator.config.json` override, same as today's per-plan config already allows), which
  provider is **primary** for each of the four logical tiers (`economy`, `standard`, `strong`,
  `max`), and an **ordered fallback chain** per tier for when the primary is unavailable.
- "Unavailable" must include what MODEL_ROUTING.md §6 already promises and the code does not yet
  do: a rate-limit/quota/capacity/CLI-interruption event on the current provider must be able to
  move the *next* attempt to the next configured fallback provider **at the equivalent logical
  rung**, without waiting out the quota window and without counting as `failure_class` evidence
  (`rate_limit_events` stays the bookkeeping field; this must not touch
  `functional_failures`/`failure_classes`). This closes the gap in the Evidence section above.
- Must keep the existing, working `functional_failures`-based rotation for actual failure
  evidence — this is an additional path, not a replacement.
- Must remain compatible with per-task `"provider": "auto"` and explicit per-task
  `"provider": "<name>"` + `allow_provider_fallback` — a task-level explicit provider should still
  be able to opt out of the global chain the same way it does today.
- Should validate that a chosen concrete model for a tier is compatible with that provider's
  `models_without_effort` list (see Evidence) and warn/reject an obviously-invalid combination at
  configuration time rather than failing at dispatch time.

## Requirement 3 — Interactive multiple-choice configuration flow

- Add a configuration entry point (a `pae configure` command, or an in-skill flow invoked from
  chat — final planning decides the concrete mechanism) that walks a person through setting up
  Requirement 2 (and, if enabled, Requirement 1's assistant provider).
- **One multiple-choice question per setting, never a bundled question.** At minimum, per tier:
  one question for "which provider is primary for this tier" (single choice among configured/
  detected providers), and one separate question for "which providers can be its fallback, in
  order" (multiple choice, ordered). Plus one separate question for "enable the auxiliary
  assistant role, and with which provider" (default: Antigravity).
- The concrete question-asking mechanism is host-dependent (e.g. Claude Code's structured
  multiple-choice tool) and must degrade gracefully to plain numbered-list prompts on hosts/
  providers that cannot render structured multiple-choice UI, since this skill is
  provider-agnostic (`README.md` §"Supported AI workers" — Codex, Gemini, Qwen, Kimi, Trae).
- Detect which provider CLIs are actually installed/authenticated (the skill already has
  `executable_available()` in `run_isolated.py`) and only offer those as answer options, rather
  than listing every provider the skill knows about unconditionally.
- Persist the result into `orchestrator.config.json` (`provider_order`,
  `allow_provider_fallback`, per-provider `models`, and the new assistant-role config), and print
  a summary of what was written before exiting.

## Non-goals

- Not a general multi-agent debate/voting system between providers for the same TODO.
- Not a change to the evidence-based escalation ladder (`mechanical`/`semantic`/`environmental`/
  `budget`/`plan_defect`) — that stays as documented; this request only fixes provider
  *availability* fallback and adds the assistant role alongside it.
- Not a requirement to build the assistant role for anything beyond validation-failure triage in
  the first version; a generic "assistant" hook is enough if it is reused later.

## Suggested starting points for planning

- `skill/plan-and-execute/scripts/run_isolated.py` (`candidate_providers`, `choose_route`,
  `execute_one_task`, `wait_after_rate_limit`, `effort_args`, `is_provider_availability_failure`)
- `skill/plan-and-execute/scripts/routingctl.py` (`model_supports_effort`, the model catalog)
- `skill/plan-and-execute/scripts/planctl.py` (`fail_task`)
- `skill/plan-and-execute/references/MODEL_ROUTING.md`, `WORKFLOW.md`,
  `TEST_RESOURCE_MONITORING.md`
- `README.md` §"Supported AI workers", §"Per-TODO model routing"
- `orchestrator.config.json` schema (per-provider blocks, `provider_order`,
  `allow_provider_fallback`, `rate_limit`)
