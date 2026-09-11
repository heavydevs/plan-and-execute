# Planning-stage model routing

Use this reference when selecting capability for **planning work itself**. It complements `MODEL_ROUTING.md`, which owns provider-independent model economics for execution.

Planning is not automatically performed at the root agent's current model/effort. Route each planning leaf by semantic difficulty, verification strength, and cost of a silent planning error.

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

## 2. The final plan owns final task routing

Routes used while preparing or planning do not bind implementation:

```text
primary-plan task route != final-planning route != implementation TODO route
```

The final planner recalculates each implementation TODO's `provider`, `model_tier`, and `reasoning_effort` from that leaf's semantic risk and verifiability. Never copy primary-plan routes into the final plan merely because they already exist.

## 3. Oversized-request economics

When the input itself threatens to exhaust credits/context before a durable final plan exists:

1. measure first with deterministic tooling;
2. if the request crosses the primary-plan gate, persist immutable fragments before semantic summarization;
3. use bounded cheap workers to extract source-referenced planning facts;
4. use stronger capability only for cross-fragment architecture/decomposition/review that actually requires it;
5. persist each completed primary-plan checkpoint so provider/quota interruption can resume without rereading the whole source;
6. hand a compact prepared package to normal final planning.

This intentionally spends more orchestration steps to reduce expensive repeated input and to create a resumable state **before** frontier planning begins.

## 4. Fresh review is not a copy-edit pass

A fresh reviewer receives the complete compact requirement/graph proposal plus only the evidence necessary to challenge it. It checks coverage, atomicity, dependency correctness, pattern assignment, validation strength, unresolved contradictions, and model-routing plausibility.

Do not make the reviewer read every raw source fragment by default. It should sample or retrieve evidence for material claims and expand only when findings justify it.

## 5. Provider-specific resolution

Logical tiers stay portable. Resolve a concrete provider/model only when the planning worker is dispatched:

1. read `MODEL_ROUTING.md`;
2. load exactly one active provider mapping;
3. choose the cheapest concrete route that satisfies this planning leaf;
4. record the actual route in durable state when the host supports isolated planning workers.

Quota/rate-limit exhaustion is provider availability, not evidence that planning needs a stronger model.

## 6. Evidence basis

The policy follows converging findings:

- context engineering should maximize useful signal per model-visible token through progressive disclosure and just-in-time retrieval;
- deterministic filtering/aggregation should move outside model context when possible;
- long-context models can still underuse information depending on its position in a large prompt;
- repository-scale work benefits from explicit planning, dependency analysis, localized context, and incremental validation;
- long-running agent harnesses benefit from durable structured artifacts between fresh contexts.

See the research basis in `PRIMARY_PLANNING.md` and `ARTIFACT_WRITING.md`; do not preload those references only to repeat citations during ordinary execution.
