# Token-efficiency contract

Use this reference when reviewing prompt/context cost or changing the harness. `ARTIFACT_WRITING.md` owns prose precision/budgets; this file owns **where tokens are spent**.

## Objective

Minimize tokens that do not improve an implementation decision while preserving or improving verified quality. A token is justified when it carries current-task requirements, evidence, a decision boundary, failure diagnosis, validation signal, or durable handoff needed to resume.

## 1. Avoid the harness when the harness does not pay for itself

Selective activation is the first and largest optimization.

- cohesive small/medium work stays DIRECT;
- file count and the word `implementation` are not orchestration triggers;
- uncertainty defaults to DIRECT because late promotion is available;
- full planning starts only when independent workstreams, broad study, cross-cutting risk, durable resume value, or isolation materially help.

A direct exit creates no `.ai-work` state, but adaptive model-economy rules still apply.

## 2. Keep useful shared context while it is useful

Fresh workers are not automatically cheaper. For one cohesive task, the current conversation can be the cheapest cache of decisions, repository findings, and validation history.

Use a fresh worker when context boundaries diverge, disposable exploration would pollute expensive context, independent verification helps, or persistence/resume is valuable. Do not isolate sequential steps that strongly reuse the same reasoning merely to follow a process template.

## 3. Make exploration cheap before making reasoning cheap

Repository discovery is often high-volume but low-risk. Optimize it separately from implementation:

1. deterministic filename/symbol/text search first;
2. rank likely paths and inspect focused ranges;
3. when discovery fans out, use the active provider's `economy` read-only worker;
4. return only a compact evidence map: paths/symbols, relevance, tests/contracts, unresolved questions;
5. let the parent/implementer verify material findings and make consequential decisions.

Do not spend strong/max tokens reading dozens of files that may be irrelevant. Conversely, do not spawn a subagent for one grep or two obvious reads; startup and duplicated instructions are overhead too.

Default exploratory concurrency is at most two. Increase only for genuinely independent branches whose parallelism offsets multiplied context/output cost.

## 4. Direct work without strong tests needs semantic routing

DIRECT does not imply cheap implementation at all costs. If a cohesive small task has weak or no deterministic validation:

- keep exploration cheap;
- estimate reversibility, blast radius, and how easily a human/model review can detect a semantic mistake;
- use the standard route for ordinary local changes;
- move one capability step stronger when silent failure is materially plausible;
- do not create a plan solely to obtain a stronger model.

This separates two costs that are often confused: reading the repository can remain cheap even when the final edit deserves a stronger implementer.

## 5. Promote instead of restarting

When direct work becomes long-horizon, persist only a compact handoff:

- original goal;
- completed work and validated results;
- active decisions/invariants;
- relevant paths/symbols;
- blockers/risks;
- remaining outcomes;
- bounded repository status/diff stats.

Do not persist conversation narration or invent retroactive TODOs. The promoted plan covers remaining work only.

## 6. Spend model tokens only on judgment

Use deterministic code for lifecycle/state transitions, dependency scheduling, coverage checks, filesystem/path safety, validation execution, compact git evidence, log storage/tails, installer transforms, and cleanup.

Use models for ambiguity resolution, architecture, decomposition, implementation, debugging, and synthesis that genuinely require reasoning.

A deterministic operation that can run once should not be replaced by a model conversation. Batch safe independent queries when a program/tool can do so without injecting every intermediate result into model context.

## 7. Progressive disclosure

The entrypoint is a small control plane. Load only the phase-specific reference:

- routing ambiguity -> `ROUTING.md`;
- late promotion -> `PROMOTION.md`;
- full orchestration -> `ORCHESTRATION.md`;
- generic model selection -> `MODEL_ROUTING.md`;
- concrete model selection -> **only** `MODEL_ROUTING_CODEX.md` or `MODEL_ROUTING_CLAUDE.md` for the provider actually executing the work;
- study/planning/execution -> only their phase references.

Do not preload the reference directory or both provider model files. If provider fallback happens later, load the fallback provider file then.

## 8. Preserve request evidence; compress derived state

Never shorten authoritative user/request-file evidence merely to save tokens. Derived artifacts replace repeated prose with stable ids, paths, symbols, commands, mappings, compact validation state, and bounded completion memory.

Do not copy request paragraphs into study, requirements, plan, every task, and final summary.

## 9. Search first, read second

For repository work: search filenames/symbols/keywords, rank likely files, open focused ranges plus necessary dependencies/tests, then widen only when evidence requires it.

For external research, prefer authoritative targeted sources. Save conclusion + planning impact, not article text. Search/retrieval outputs that do not change a decision should not be propagated downstream.

## 10. Minimize shared orchestrated context

Default to no `CONTEXT.md`. Create global/scoped context only for non-obvious facts truly reused by assigned TODOs. Keep single-task facts in the task definition.

Reuse cross-task learnings only when they are expensive, validated, directional, and predeclared.

## 11. Preserve stable provider prefixes and logical routing

Keep stable execution/provider rules before dynamic task data when provider caching can benefit. Avoid duplicating rules across system prompt, task file, worker prompt, and report schema.

When the host/provider supports it:

- defer or disable unused MCP/tool definitions rather than loading a large catalog into every turn;
- preserve stable prompt prefixes so cached input can be reused;
- prefer tool search/on-demand loading for large tool catalogs;
- compact or clear stale tool results after important decisions/evidence are durably captured;
- avoid toggling model/effort/tool configuration repeatedly when doing so destroys useful cache reuse without a quality benefit.

These are provider capabilities, not requirements: never emulate them with more model prose when the host lacks support.

## 12. Route by verified task cost, not price per token

Route each semantic leaf to the cheapest model/effort credibly able to solve it. Newer models at lower effort can dominate older models at higher effort, while stronger models can also finish hard work in fewer retries. Price-per-token alone is insufficient.

Use cheap-first when failure is objectively detectable and cheap. Start stronger for high-blast-radius decisions with weak validation. Let the skill select and escalate routes from evidence; do not maintain a user-selected model ceiling.

## 13. Bound tool/report output

Full output belongs in logs. Model/state context gets only decision-relevant excerpts. Preserve current bounded completion summaries, validation details, failure reasons, risk/follow-up counts, learning guidance, and final repository-change summaries.

Do not copy full stack traces/build output into retries when an error excerpt + log path is sufficient.

## 14. Final summary uses compact authoritative state

Never concatenate raw worker reports into final-summary input. Use goal, task completion summaries, changed files, deterministic validation status, remaining risks/follow-ups, and bounded repository change evidence.

Final/status prose uses an economy route when no difficult synthesis is required.

## 15. Never optimize away quality anchors

Token reduction must not remove complete request evidence, requirement coverage for orchestrated remaining work, task scope/invariants, acceptance criteria, deterministic validation, material failure evidence, resume checkpoints, per-TODO model/effort routing, safety/path guards, or cleanup preservation.

When concision and correctness appear to conflict, first remove repetition, disposable exploration context, and process narration. If a distinction still changes implementation or validation, keep it.
