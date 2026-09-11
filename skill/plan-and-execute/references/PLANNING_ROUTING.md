# Planning-stage model routing

Use this reference when selecting capability for **planning work itself**. It complements `MODEL_ROUTING.md`, which owns provider-independent model economics for execution.

Planning is not automatically performed at the root agent's current model/effort. Route each planning leaf by semantic difficulty, verification strength, and cost of a silent planning error — and obtain that route by **delegation** (`MODEL_ROUTING.md` §3), never by switching the root session's model.

## 1. Route planning stages independently

| Planning work | Default logical route | Raise capability when |
|---|---|---|
| byte/character/token estimate, hashing, source splitting, index generation | deterministic tool | never use a model when code can prove it |
| bounded source extraction, classification, evidence map | `economy`, low/medium | the fragment contains ambiguous multi-hop constraints or dense technical contracts |
| requirement normalization and bounded cross-fragment synthesis | `standard`, medium | contradictions, migrations, security, data integrity, or weak verification make omission costly |
| architecture, task boundaries, dependency graph, migration/compatibility strategy | `strong`, low/medium | verification is weak, blast radius is high, or the architecture spans many coupled domains |
| fresh plan review | normally same tier as the hardest material planning decision, fresh context | increase one step when the reviewer must detect subtle cross-domain omissions with little deterministic evidence |
| frontier/max planning | `max` only from evidence | repeated strong-route failure or genuinely frontier/long-horizon reasoning leaves a plausible capability gap |

A huge source document is **not** a reason to feed the whole document to a frontier model. Size and semantic difficulty are separate axes. Mechanical volume belongs in deterministic preprocessing or cheap bounded workers; difficult decisions receive stronger models only after the relevant evidence has been localized.

## 2. Small root model: delegate the stage, never attempt it

The root session may be Haiku/Luna or any model the user chose. That is not a ceiling:

1. triage (root, cheap in tokens): name each planning stage's signals with the `SKILL.md` §4 table or `routingctl.py route`;
2. if the root tier is below a stage's floor, dispatch that stage to a fresh worker at the floor tier with a minimal prompt (evidence ids/paths, the question, the output schema) and consume only its compact output;
3. stages at or below the root tier run in the root, reusing its cache;
4. record the route actually used (`hard_decisions[].route_used`, primary-plan task routes) so a resumed session does not redo the work at the wrong tier.

Never load a stronger reference or a bigger context "to compensate" for a weak root; delegate instead.

## 3. Decision-first planning (difficulty-triggered staging)

PRIMARY_PLAN stages by **input size**. When the input is manageable but a few decisions are hard and most of the plan is mechanical, stage by **difficulty** instead of planning everything at the strongest tier:

1. **Inventory** (`economy`/root): list `hard_decisions[]` — architecture choices, contradictions, compatibility or data-integrity questions whose answer changes TODO boundaries — each with the evidence ids that bear on it;
2. **Resolve** (`strong`, fresh worker per decision or per tightly coupled group): input = the decision, its evidence, the constraints; output = one decision <= 240 chars, rationale <= 240 chars, resulting constraints; no plan writing;
3. **Compose** (`standard`): requirements, TODO graph, context, patterns from the resolved decisions and the ordinary evidence;
4. **Review** (fresh, tier of the hardest decision): coverage, atomicity, dependencies, routing plausibility.

Record the outcome in `request_analysis.hard_decisions` (`PLAN_SPEC.md`). Skip the staging when the whole plan is hard (one strong planner is cheaper than the handoffs) or when no decision is hard (one standard planner suffices). Antigravity's `/boost` and Claude Code's "draft a plan from several angles" workflows follow the same shape: strategy by a strong orchestrator, bounded parallel work, synthesis with verification.

## 4. The final plan owns final task routing

Routes used while preparing or planning do not bind implementation:

```text
primary-plan task route != final-planning route != implementation TODO route
```

The final planner recalculates each implementation TODO's `provider`, `model_tier`, and `reasoning_effort` from that leaf's semantic risk and verifiability, and may add `design_route` to a `high` leaf whose implementation volume justifies a separate strong design pass. Never copy primary-plan or decision-resolution routes into the final plan merely because they already exist.

## 5. Oversized-request economics

When the input itself threatens to exhaust credits/context before a durable final plan exists:

1. measure first with deterministic tooling;
2. if the request crosses the primary-plan gate, persist immutable fragments before semantic summarization;
3. use bounded cheap workers to extract source-referenced planning facts;
4. use stronger capability only for cross-fragment architecture/decomposition/review that actually requires it;
5. persist each completed primary-plan checkpoint so provider/quota interruption can resume without rereading the whole source;
6. hand a compact prepared package to normal final planning.

This intentionally spends more orchestration steps to reduce expensive repeated input and to create a resumable state **before** frontier planning begins.

## 6. Fresh review is not a copy-edit pass

A fresh reviewer receives the complete compact requirement/graph proposal plus only the evidence necessary to challenge it. It checks coverage, atomicity, dependency correctness, pattern assignment, validation strength, unresolved contradictions, and model-routing plausibility (including whether `design_route`/`hard_decisions` were used where the leaf signals justify them).

Do not make the reviewer read every raw source fragment by default. It should sample or retrieve evidence for material claims and expand only when findings justify it.

## 7. Provider-specific resolution

Logical tiers stay portable. Resolve a concrete provider/model only when the planning worker is dispatched:

1. read `MODEL_ROUTING.md`;
2. load exactly one active provider mapping;
3. choose the cheapest concrete route that satisfies this planning leaf;
4. record the actual route in durable state when the host supports isolated planning workers.

Quota/rate-limit exhaustion is provider availability, not evidence that planning needs a stronger model.

The research behind this policy is summarized for maintainers in `docs/RESEARCH_BASIS.md`; do not load it during ordinary execution.
