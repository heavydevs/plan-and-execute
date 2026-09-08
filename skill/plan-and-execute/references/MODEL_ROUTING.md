# Model and provider routing

Load this reference only when choosing or escalating a model route. It defines provider-independent policy. Then read **exactly one** concrete provider reference for the provider that will actually execute the work:

- Codex -> `MODEL_ROUTING_CODEX.md`
- Claude Code -> `MODEL_ROUTING_CLAUDE.md`

Do not preload both provider files. A fallback provider loads its own reference only when fallback actually occurs.

## Objective

Maximize **verified quality per credit/token and per completed task**, not raw benchmark score or price per token. Use the cheapest route credible for the current semantic leaf; spend more when weak verification, high blast radius, or concrete failure evidence makes stronger reasoning economically safer.

## 1. Classify the work before choosing a model

1. **Deterministic lookup** — filename/symbol/text search, a known build/test/lint command, formatting, or other non-judgmental operation: use tools directly.
2. **Exploration** — broad repository/log/doc discovery, call-site/test inventory, dependency tracing, or initial study: use a cheap read-only worker when delegation avoids loading substantial disposable context into the main agent.
3. **Bounded implementation** — ordinary features, focused refactors, routine debugging, tests, and well-scoped edits: use a standard route.
4. **Reasoning-sensitive work** — subtle debugging, architecture, security, concurrency, transactions, data integrity, compatible migrations, distributed behavior, or weakly verifiable decisions: use a strong route.
5. **Frontier/long-horizon work** — repeated hard failure with useful evidence, unusually broad reasoning, or long agent loops whose success rate benefits from frontier effort: use max/frontier routing.

A large parent request does not make every leaf strong/max.

## 2. Verifiability changes the cheapest safe route

When deterministic validation is strong and failure is cheap to detect, prefer:

```text
cheapest credible route -> deterministic validation
PASS -> stop
FAIL -> retain compact evidence -> increase effort/model capability -> validate again
```

Examples of strong verification: compile, unit/integration tests, lint, type checks, schema checks, exact queries, snapshots, golden outputs, or reproducible benchmark commands.

When objective verification is weak, start one step stronger. Examples: architecture boundaries, security policy, destructive migrations, distributed consistency, ambiguous production diagnosis, or a small code change with no meaningful tests where silent semantic failure would be costly.

Do not interpret “no tests” as “always use the strongest model.” First assess change size, reversibility, local inspectability, and blast radius.

## 3. DIRECT mode keeps economical routing

DIRECT means **no planning harness**, not “one expensive model does everything.” For cohesive small and medium-small requests:

- keep the current conversation when its context is already useful;
- use deterministic search before model-based exploration;
- delegate only discovery that would fan out or pollute main context;
- return a compact evidence map from explorers instead of full files/search narration;
- implement in the current context when the edit is cohesive;
- if validation is weak or absent, raise the implementation route based on semantic risk rather than creating a plan just to obtain a stronger model;
- promote to ORCHESTRATED only when scope, independence, research, resumability, or context isolation begins to justify the harness.

For a tiny mechanical edit, a subagent can cost more than it saves. For a small but subtle edit with no tests, spending more on the implementer/reviewer can be cheaper than a failed cheap-first loop.

## 4. Exploration is a separate economic problem

Repository discovery is often high-volume and low-risk. Optimize it independently from implementation:

- search/rank first;
- open focused ranges second;
- widen only from evidence;
- if exploration fans out, use the provider's cheapest credible read-only worker;
- request only paths/symbols, relevance, tests/contracts found, unresolved questions, and minimal excerpts;
- parent/implementer verifies material findings before consequential changes;
- prefer at most two concurrent explorers unless branches are truly independent.

Never spend a frontier model reading dozens of candidate files that a cheaper worker can filter. Never spawn a worker for one grep or two obvious reads.

## 5. Logical tiers remain portable

| Tier | Meaning |
|---|---|
| `economy` | exploration, mechanical/narrow work, cheap summaries |
| `standard` | ordinary bounded implementation/debugging/tests |
| `strong` | difficult, subtle, high-risk, or weakly verifiable engineering |
| `max` | frontier/long-horizon escalation after semantic need or failure evidence |

Concrete models are provider-specific. Do not assume that a newer frontier model must run at high effort: model generation and reasoning effort are independent axes, and a newer model at low/medium effort can dominate an older model at high effort.

## 6. Effort is adaptive, not tied blindly to tier names

Use the provider-specific reference for exact defaults. General rules:

- `low`: exploration, mechanical work, or a newer strong model on a bounded/verifiable task when its low-effort capability is already sufficient;
- `medium`: default cost/quality balance for normal implementation and many difficult but verifiable tasks;
- `high`: weak verification, high blast radius, difficult debugging, or evidence that medium under-reasoned;
- `xhigh`: demanding long-running coding/agent loops or repeated hard failures;
- `max`: only when the task justifies unconstrained reasoning spend and lower efforts have a plausible capability gap.

Escalate because of evidence, not because the overall request is large. Skip cheap rungs when failure would be expensive or hard to detect.

## 7. Provider fallback is not a technical escalation signal

Quota/rate-limit exhaustion, temporary capacity, CLI interruption, or unavailable models do not prove the task needs more intelligence. Preserve current task state and select the equivalent logical route on the fallback provider. Load that provider's routing reference at that point.

## 8. Context economics are part of model economics

- Keep stable instructions before dynamic task data when caching can reuse prefixes.
- Defer or disable unused tool/MCP definitions when supported.
- Prefer batched deterministic queries over many model/tool round trips when safe.
- Keep full logs on disk; pass bounded failure excerpts plus paths to retries.
- Do not repeatedly summarize the same evidence.
- Final/status prose uses an economy route when no difficult synthesis is required.

## 9. Stop when verified quality is reached

A stronger model is not a reward for surviving more retries. Stop as soon as acceptance criteria and available independent validation pass. If repeated failure reveals a planning/decomposition defect, replan instead of blindly increasing model effort.
