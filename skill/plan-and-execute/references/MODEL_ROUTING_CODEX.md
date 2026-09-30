# Codex model routing

Read only when Codex will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy.

## Current capability map

Concrete ids live in `scripts/routingctl.py` `CURRENT_MODELS` (map version 2026-09-30-v5); this table must match it. Verify what an installation actually serves with `codex debug models` (live catalog; `~/.codex/models_cache.json` can be stale).

| Tier | Model | Catalog description | Typical starting effort |
|---|---|---|---|
| `economy` | `gpt-6-luna` | "Fast and affordable model for easier tasks" | `low` |
| `standard` | `gpt-6-sol` | GPT-6 workhorse (previous generation to Astra) | `medium` |
| `strong` | `gpt-6-astra` | "Frontier intelligence for the most demanding work" | `low` or `medium` |
| `max` | `gpt-6-astra` | same | `xhigh` only when long-horizon evidence justifies it; `max` is exceptional |

The GPT-5.6 line (`gpt-5.6-luna`/`-terra`/`-sol`) is listed as *older* in the catalog and is not a default route anywhere. There is no GPT-6 Terra, so Sol takes the balanced standard slot that Terra held. No published benchmark separates GPT-6 Sol from GPT-6 Astra: the ladder below keeps the shape calibrated on GPT-5.6 (a demonstrated capability gap goes to Astra Low before any High-effort retry on the standard model) until a project eval says otherwise.

Do **not** use a High-effort standard-model retry as the default difficult-work route. OpenAI's calibration (GPT-5.6, carried over) places Astra Low/Medium above the previous strong model at High (Astra Low outperforms it at a fraction of the tokens). Use **Astra Medium as the safer difficult-work baseline when verification is weak**, and Astra Low when the task is bounded and objectively verifiable. Astra always reasons (no `none` effort). Efforts accepted (from the catalog): Luna `low`..`max`; Sol and Astra `low`..`max` plus `ultra`. The skill never selects `ultra`: it is above the ladder's `xhigh` ceiling and has no evidence-based trigger; a project may opt in through its own configuration after measuring it.

Codex charges no cache writes and no long-context multiplier, and cached reads cost ~10% of input, so stable worker prefixes are cheap to reuse; `tool_output_token_limit` bounds how much tool output is kept in history.

## Elevation mechanics (how a route is actually obtained)

The skill never changes the thread's model (`/model` is the user's); it obtains a different tier by **delegation**:

| Need | Mechanism |
|---|---|
| Cheap read-only discovery | `spawn_agent` with the built-in `explorer` role and `model: gpt-6-luna` (`model_reasoning_effort: low`; `medium` only for multi-hop tracing). Explorers run `sandbox_mode: read-only`. |
| Stronger leaf from a smaller root | `spawn_agent` with the `worker` role, `model: gpt-6-astra`, and an explicit `model_reasoning_effort`; a minimal prompt (task, paths/symbols, acceptance, validation). |
| Reusable roles | `.codex/agents/<name>.toml` with `model`, `model_reasoning_effort`, `sandbox_mode`, `developer_instructions`; a custom agent named like a built-in overrides it. |
| Session-wide subagent defaults | `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort` in `config.toml`; explicit spawn values win. Concurrency: `agents.max_concurrent_threads_per_session`. |
| Strong plan, cheap execution | `plan_mode_reasoning_effort` gives `/plan` its own effort; the skill's planning-stage routing achieves the same split by delegating planning leaves. |
| Budget guard | `features.rollout_budget.enabled` + `features.rollout_budget.limit_tokens` (the runner sets them from `codex.rollout_token_budget`). Enforcement (aborting the turn via `CodexErr::TurnAborted`) shipped 2026-06-19; the exact surfaced wording is not published, so the runner's pattern match is best-effort and an unmatched phrasing is classified `unknown` (safe: +1 rung) rather than `budget`. |

Subagent workflows consume more tokens than one agent doing the same work; spawn only when isolation, parallelism, or a different tier pays for itself.

## DIRECT mode

Small or medium-small work stays without a plan when it is cohesive. Model routing still applies:

- one-off lookup/build/test/lint -> deterministic tool, no subagent;
- broad read-only discovery -> Luna Low explorer; Luna Medium only for bounded multi-hop tracing;
- tiny mechanical edit with obvious local review or deterministic validation -> keep current useful context; delegate to Luna only when isolation actually saves context;
- normal bounded implementation with good validation -> Sol Medium;
- normal implementation that exposes a reasoning gap -> Astra Low (semantic gap), not Sol High;
- small but subtle change with weak/no tests -> Astra Low when silent semantic failure would be materially costly; otherwise Sol Medium plus focused review is cheaper;
- difficult but strongly verifiable debugging/implementation -> Astra Low first, then Astra Medium from concrete failure evidence;
- high-blast-radius or weakly verifiable architecture/security/concurrency/migration decisions -> Astra Medium or High directly.

Do not create an ORCHESTRATED plan merely to obtain Astra. DIRECT can choose any justified route.

## ORCHESTRATED tasks

Choose the logical tier per TODO, not per parent request:

- `economy`: Luna Low; Medium only when the exploration itself requires multi-hop reasoning;
- `standard`: Sol Medium; a semantic failure moves to Astra Low rather than Sol High;
- `strong`: Astra Low when deterministic validation is strong, otherwise Astra Medium; High for high-risk/weak-verification work or evidence that Medium under-reasoned;
- `max`: Astra High/XHigh for genuinely demanding long-running work; Max only when lower efforts leave a plausible capability gap.

A failed compiler command does not automatically justify Astra. A wrong architecture decision may justify Astra before any retry.

## Exploration subagents

Use Luna explorers to protect expensive context from disposable discovery: a narrow question and the minimum starting paths/symbols; a compact evidence map, not narration or full files; read-only unless the task is explicitly mechanical and independently verifiable; at most two simultaneous explorers. The parent verifies material findings before consequential edits.

## Escalation ladder (runner default)

Climbed from `failure_class` evidence (`MODEL_ROUTING.md` §6), starting at the TODO's declared route:

```text
Luna Low
  -> Luna Medium
  -> Sol Medium
  -> Astra Low             (semantic from Sol jumps here; Sol High is never a rung)
  -> Astra Medium
  -> Astra High
  -> Astra XHigh
```

Do not burn several high-effort Sol retries when one Astra Low attempt is more likely to solve a demonstrated capability gap.

## Older catalogs and quota

The Claude/Codex model ids are fixed in `CURRENT_MODELS` and re-applied on every config load, so a per-plan `orchestrator.config.json` edit of `codex.models` is overwritten. A Codex installation whose catalog predates GPT-6 Luna/Sol (`codex debug models` lacks them) should update Codex; an unknown model id is rejected by the CLI as a configuration error, not rotated as quota. Availability/quota failure is not evidence to increase reasoning effort.

## Runner flags

Workers run as `codex exec --ephemeral --sandbox <mode> --model <id> -c model_reasoning_effort="<effort>" --output-schema ... --output-last-message ...`; the summary uses `--sandbox read-only`.

`--output-schema` receives a derived copy of `completion-report.schema.json` written per attempt to `<plan>/results/codex-output-schema.json`: OpenAI structured outputs reject `uniqueItems` and require strict objects (every property in `required`, `additionalProperties: false`), so the runner strips the unsupported keywords, marks optional fields required (workers return `null`/`[]`), and deduplicates the unique-list fields on ingestion instead. The canonical schema is unchanged for the other providers.
