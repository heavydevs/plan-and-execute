# Portable model and provider routing

Load this reference only when choosing, escalating, or refreshing a model route. Durable plans use provider-neutral capability coordinates; concrete provider/model ids live in the plan-local model matrix and are resolved only when execution begins.

## Objective

Maximize **verified quality per completed task and per unit of spend**, not raw benchmark score or token price. Keep a plan executable when the user switches coding agents, subscriptions, providers, or model generations.

## 1. Portable coordinates

New plans use two independent axes.

| Coordinate | Meaning |
|---|---|
| `F1` | cheapest credible model family for exploration, mechanical edits, and cheap summaries |
| `F2` | normal implementation/debugging/test family |
| `F3` | strong family for subtle, risky, weakly verifiable, or evidence-heavy engineering |
| `F4` | frontier family for long-horizon work or repeated hard failures |
| `L1` | lowest useful reasoning/agent effort exposed by the chosen provider/model |
| `L2` | normal economical reasoning effort |
| `L3` | high reasoning effort |
| `L4` | very high reasoning effort |
| `L5` | highest currently supported useful effort |

`F` and `L` are not vendor names. A plan may say `F2/L2`; at execution that may resolve to one provider's standard model at medium effort, another provider's stronger inexpensive model at low effort, or a model variant when that provider has no independent reasoning knob.

Higher F means more model capability/cost budget. Higher L means more reasoning/agent effort. Adjacent F or L coordinates may map to the same concrete setting when a provider has fewer useful rungs.

Legacy `economy|standard|strong|max` and `low|medium|high|xhigh|max` routes remain supported for old plans, but do not write them into new plans.

## 2. Build the concrete matrix dynamically

For every ORCHESTRATED plan, read `MODEL_MATRIX.md` and refresh the provider mapping during planning.

Use current evidence in this order:

1. installed coding-agent CLI model/effort discovery or first-party CLI help;
2. current first-party model catalog, pricing/subscription, and compatibility documentation;
3. a recent independent coding-agent/repository/terminal benchmark when available;
4. conservative built-in routing fallbacks only when live discovery is unavailable.

Prefer evidence that measures completed coding-agent work, not isolated code-generation snippets. Compare success/quality, cost per completed task, latency when it matters, and quota/subscription economics. Do not assume the newest or most expensive model belongs in F4 if a cheaper current model dominates it on the relevant coding workload.

Persist the result through `modelmapctl.py` as `MODEL_MATRIX.json` plus `MODEL_MATRIX.md`. Include the providers that can realistically execute or resume the plan. Claude Code, Codex, Gemini, Qwen Code, and Muse Code are first-class routing targets; Kimi/Trae remain supported by the runner when configured.

Concrete model names must not be copied into TODO objectives, subtasks, dependencies, acceptance criteria, or durable route fields.

## 3. Classify the work before choosing F/L

1. **Deterministic lookup** — filename/symbol/text search, known build/test/lint commands, formatting, or other non-judgmental operations: use tools directly before spending an agent turn.
2. **Exploration** — broad repository/log/doc discovery, call-site/test inventory, dependency tracing, or initial study: usually `F1/L1` or `F1/L2`, preferably read-only.
3. **Bounded implementation** — ordinary features, focused refactors, routine debugging, tests, and well-scoped edits: usually `F2/L2`.
4. **Reasoning-sensitive work** — subtle debugging, architecture, security, concurrency, transactions, data integrity, compatible migrations, distributed behavior, or weakly verifiable decisions: usually `F3/L2` through `F3/L4`.
5. **Frontier/long-horizon work** — repeated hard failure with useful evidence, unusually broad reasoning, or long agent loops whose success rate benefits from frontier capability: `F4`, with the lowest L that remains credible.

A large parent request does not make every leaf F3/F4.

## 4. Verifiability changes the cheapest safe route

When deterministic validation is strong and failure is cheap to detect, prefer:

```text
lowest credible F/L -> deterministic validation
PASS -> stop
FAIL -> retain compact evidence -> raise L and/or F -> validate again
```

Examples of strong verification: compile, unit/integration tests, lint, type checks, schema checks, exact queries, snapshots, golden outputs, or reproducible benchmark commands.

When objective verification is weak, start one step stronger. Examples: architecture boundaries, security policy, destructive migrations, distributed consistency, ambiguous production diagnosis, or a small code change with no meaningful tests where silent semantic failure would be costly.

Do not interpret “no tests” as “always F4/L5.” Assess change size, reversibility, local inspectability, and blast radius.

## 5. Escalation order is semantic, not numeric ritual

Do not blindly walk every rung. A newer F4 model at L1/L2 can be cheaper and more capable than an older F3 model at L4/L5. The live matrix exists specifically so the executor can choose the economical concrete route behind the stable F/L contract.

Default escalation pattern:

```text
same F, +1 L
-> next F at an economical L
-> stronger L on that F
-> F4 only when evidence justifies frontier capability
```

Skip a rung when current benchmark/cost evidence shows it is dominated. Stop once acceptance criteria plus independent validation pass.

## 6. Provider switching must not rewrite the plan

New TODOs keep `provider: auto`. At dispatch time the runner chooses an installed/available provider and resolves the TODO's F/L through that provider's current row in `MODEL_MATRIX.json`.

Quota exhaustion, capacity errors, subscription-window limits, CLI interruption, or unavailable models are **availability failures**, not proof that more intelligence is required. Resume the same F/L on another compatible provider when possible.

The actual provider/model/native effort belongs in attempt history/results. It is execution provenance, not plan semantics.

If a task genuinely requires a provider-specific external capability, record that capability as an explicit task constraint. Do not encode a provider name merely because that provider happened to be available during planning.

## 7. Exploration is a separate economic problem

Repository discovery is often high-volume and low-risk. Optimize it independently from implementation:

- search/rank first;
- open focused ranges second;
- widen only from evidence;
- if exploration fans out, use the cheapest credible read-only route, normally F1;
- request only paths/symbols, relevance, tests/contracts found, unresolved questions, and minimal excerpts;
- parent/implementer verifies material findings before consequential changes;
- prefer at most two concurrent explorers unless branches are truly independent.

Never spend F4/L5 reading dozens of candidate files a cheaper worker can filter. Never spawn a worker for one grep or two obvious reads.

## 8. DIRECT mode keeps economical routing

DIRECT means **no planning harness**, not “one expensive model does everything.” Use the same F/L semantics mentally or in temporary routing decisions, but do not create `MODEL_MATRIX.*` merely for a tiny direct request. If direct work later promotes to ORCHESTRATED, create a fresh matrix at promotion/planning time.

## 9. Context economics are part of model economics

- Keep stable instructions before dynamic task data when caching can reuse prefixes.
- Defer or disable unused tool/MCP definitions when supported.
- Prefer batched deterministic queries over many model/tool round trips when safe.
- Keep full logs on disk; pass bounded failure excerpts plus paths to retries.
- Do not repeatedly summarize the same evidence.
- Final/status prose uses an F1 route when no difficult synthesis is required.

## 10. Static provider notes are compatibility references only

`MODEL_ROUTING_CODEX.md` and `MODEL_ROUTING_CLAUDE.md` may contain provider-specific CLI/behavior notes, but they are not authoritative model catalogs. Never copy their concrete model ids into a new plan without live validation. Gemini, Qwen, and Muse mappings are expected to come from the current model matrix rather than long-lived hardcoded documentation.
