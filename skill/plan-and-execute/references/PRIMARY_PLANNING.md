# Primary planning for oversized requests

**Load this file only after the entry gate has selected `PRIMARY_PLAN`.** Normal final planning must not read it.

The primary plan is a resumable preprocessing plan whose only product is a compact, traceable input package for the ordinary final-planning workflow. It never implements product code and never decides final implementation routes.

Read `PLANNING_INPUT_CONTRACT.md` and `PLANNING_ROUTING.md` after this file. Do not preload the ordinary full orchestration workflow merely to create the primary plan.

## 1. Why this path exists

A large specification can exhaust expensive-model credits or attention before a durable implementation plan exists. Feeding the entire source repeatedly to a frontier model also wastes input tokens and makes resume/provider switching fragile.

The primary path creates durable state **before** expensive architectural synthesis:

```text
large source
  -> deterministic assessment
  -> immutable semantic fragments + source index
  -> resumable PRIMARY PLAN
       -> bounded extraction/digests
       -> cross-fragment pattern/contract synthesis
       -> coverage/contradiction review
       -> compact FINAL_PLAN_INPUT
  -> ordinary FINAL PLAN
  -> implementation
```

## 2. Route by working-set pressure, not maximum context size

Use `scripts/preplanctl.py assess` before reading the complete request into a planning model whenever the request is a file or can be persisted cheaply.

The defaults are **economic guardrails**, not claims about model context limits:

- `direct_final`: estimated request <= 12,000 tokens and no strong breadth signal;
- `primary_plan`: estimated request >= 24,000 tokens;
- between those bounds, choose `primary_plan` when structural breadth suggests many independently constrainable sections (default: >= 30 detected headings at >= 8,000 estimated tokens), or when the host/provider credit budget makes one-shot planning unsafe;
- callers may override thresholds for a provider/project-specific measured budget.

Never classify solely from file count. A 30k-token repetitive log can be mechanically filtered; a smaller architecture document with many interacting normative sections may deserve staged preparation.

The router should inspect **metadata and structure only**. Its result must not echo the entire request into model context.

## 3. Split deterministically before asking a model to summarize

Run `preplanctl split` (or `prepare`, which includes splitting). Prefer natural section boundaries and then bounded size. The splitter must:

- preserve source text faithfully inside each fragment;
- assign stable fragment ids (`F001`, `F002`, ...);
- preserve source order and heading ancestry when available;
- record source block/paragraph anchors and SHA-256 hashes;
- target compact fragments (roughly 3k–6k estimated tokens) and split oversized sections without silently dropping text;
- never paraphrase, deduplicate, or resolve contradictions during mechanical splitting.

For `.docx`, extraction may use OOXML paragraph/style information without invoking a model. For unsupported binary formats, export/materialize readable text first rather than using an expensive model as a byte parser.

Immutable fragments are the anti-loss layer. All later summaries must point back to them.

## 4. Create the primary plan

`preplanctl prepare` creates the prepared-package skeleton and a schema-v4 primary plan through the existing deterministic `planctl` state engine.

A primary plan is intentionally composed from bounded semantic stages rather than one giant planning prompt:

### A. Fragment digest tasks

Create one TODO per bounded batch of fragments. Default route: `economy` low/medium; raise to `standard` only when the batch itself contains dense ambiguous contracts.

Each digest records, with source fragment ids:

- atomic user obligations/constraints;
- actors/entities/interfaces/data contracts;
- explicit technology/compatibility decisions;
- acceptance/validation implications;
- dependencies and ordering constraints;
- candidate cross-cutting patterns;
- contradictions/material questions found inside the batch.

The digest is not allowed to invent architecture that the source does not state. It is a high-recall planning extraction.

### B. Cross-fragment synthesis task

Default route: `standard` medium. It reads the compact digests first and opens raw fragments only to resolve material ambiguity.

It creates/updates:

- `PATTERN_SEEDS.json` for repeated normative contracts;
- compact domain/workstream index;
- cross-fragment dependency relationships;
- contradiction/open-question inventory.

Escalate to `strong` when this synthesis itself contains high-blast-radius architecture, security, migration, data-integrity, or weakly verifiable decisions.

### C. Coverage and consistency review

Use a fresh context. Default route: `strong` low/medium because silent omission at this stage can poison the entire final plan.

The reviewer verifies:

- every immutable fragment has a completed digest;
- every material source section is represented in the compact index;
- pattern seeds cite at least two real source/task domains or a clear cross-cutting normative source;
- contradictions are recorded rather than silently reconciled;
- no digest has become a lossy replacement for primary evidence;
- the final handoff can be consumed without loading all fragments.

Write `COVERAGE_REVIEW.json`. Unresolved material contradictions block automatic final-plan autostart.

### D. Final-package handoff

Default route: `economy` low. Create `FINAL_PLAN_INPUT.md` from validated compact state. It contains pointers, not copied raw documents.

The primary plan is complete only when `preplanctl validate-package` succeeds.

## 5. Primary-plan model routing is independent

Every primary TODO still declares `provider`, `model_tier`, and `reasoning_effort`. Route by the leaf, not by the user's initially selected model.

Example:

```text
F001-F003 digest        economy / medium
F004-F006 digest        economy / medium
cross-fragment synthesis standard / medium
coverage review          strong / medium
final handoff             economy / low
```

A user starting the skill from a frontier/max model does not mean those extraction tasks should burn frontier credits.

The ordinary final planner later recalculates model routes for implementation TODOs from scratch. It may legitimately choose a stronger or cheaper route than the corresponding primary-plan extraction task.

## 6. Prepared package is outside the disposable primary plan

Primary control state lives under `.ai-work/<primary-plan-id>/`. Prepared evidence lives under `.ai-work/prepared/<package-id>/` so ordinary primary-plan cleanup cannot erase the handoff before the final plan consumes it.

Do not make the prepared package a permanent implementation artifact. After the final implementation plan completes and traceability is no longer needed for resume, guarded cleanup may remove it unless the user requested retention.

## 7. Cross-cutting pattern seeds

Large specifications often state one normative pattern once and expect many features to follow it. Examples include:

- one frontend REST Resource facade convention;
- one Admin list/toolbar/action/modal interaction pattern;
- one SCSS/token/BEM composition convention;
- one API error contract;
- one persistence/idempotency rule.

Digest workers tag such clauses as candidates instead of duplicating them into every feature digest. Cross-fragment synthesis merges only semantically identical candidates and preserves all source refs.

The final planner promotes relevant seeds into live versioned patterns using `SHARED_PATTERNS.md`. Seeds themselves are immutable preparation evidence; live pattern contracts may evolve during implementation.

## 8. Do not create a summary pyramid that loses requirements

Each semantic compression layer must keep stable references downward:

```text
FINAL_PLAN_INPUT
  -> digest ids / pattern seed ids
      -> fragment ids
          -> source anchors + hashes
```

If a final planner needs exact wording, it retrieves the fragment. Do not repeatedly summarize summaries without retained provenance.

## 9. Resume and provider switching

The primary plan uses the same durable checklist/subtask state as implementation plans. On quota exhaustion or process loss:

- preserve completed fragment digests and package files;
- resume the next incomplete primary TODO from disk;
- do not re-read already processed raw batches unless validation evidence says they are defective;
- provider fallback uses the equivalent logical tier; quota exhaustion is not a semantic failure.

This is the main safety property the staged route adds: credits may run out, but the system should already have a durable checkpoint before that happens.

## 10. Host-native fan-out (optional dispatch path)

Digest tasks are independent, uniform, and schema-checked, which is exactly what host fan-out primitives are built for. When the host offers them, the orchestrator may dispatch primary-plan stages through them instead of one fresh CLI process per TODO; the durable checklist, `validate-digest`, coverage review, and `validate-package` remain the authority, so a fan-out only replaces the *dispatch*, never the state:

- **Claude Code dynamic workflows**: `pipeline(fragmentBatches, batch => agent(digestPrompt(batch), {model: 'haiku', schema: DIGEST_SCHEMA}))`, then one `agent(..., {model: 'sonnet'})` synthesis and one fresh `agent(..., {model: 'opus'})` coverage review. Same-prefix siblings share the prompt cache (uniform model/effort/tools/schema/cwd); `schema` output is validated with retries; intermediate results stay outside the conversation; runs are resumable within the session. Draft the script with the `/workflow-authoring` skill; keep it under `.claude/workflows/` only if the project will reuse it.
- **Codex subagents**: `spawn_agent` per batch with the `explorer` role, `model: gpt-5.6-luna`, `model_reasoning_effort: low`, bounded by `agents.max_concurrent_threads_per_session`; synthesis on Terra; review on Astra Low/Medium.
- **Antigravity**: `invoke_subagent` with `model: flash` per batch and `model: pro` for review.

Each worker must still write its digest to the package and pass `preplanctl validate-digest`; the orchestrator marks TODOs complete only from those files. Do not use a fan-out when the host lacks it or when fewer than three batches exist — the portable runner is cheaper than the orchestration overhead.

Codex note: Codex charges no cache writes and no long-context multiplier, so the 12k/24k thresholds there are about attention and resumability, not price; recalibrate from measured digest quality rather than token cost alone.

The research behind this protocol is summarized for maintainers in `docs/RESEARCH_BASIS.md`; do not load it during ordinary execution. The exact token thresholds are tunable operational defaults, not universal model limits.
