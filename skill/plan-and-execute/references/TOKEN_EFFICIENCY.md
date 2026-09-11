# Token-efficiency contract

Use this reference when reviewing prompt/context cost or changing the harness. `ARTIFACT_WRITING.md` owns prose precision/budgets; `MODEL_ROUTING.md` owns route selection, exploration economics, and escalation; this file owns **where tokens are spent**.

## Objective

Minimize tokens that do not improve an implementation decision while preserving or improving verified quality. A token is justified when it carries current-task requirements, evidence, a decision boundary, failure diagnosis, validation signal, or durable handoff needed to resume.

## 1. Avoid the harness when the harness does not pay for itself

Selective activation is the first and largest optimization: cohesive small/medium work stays DIRECT; file count and the word `implementation` are not orchestration triggers; uncertainty defaults to DIRECT because late promotion is available; full planning starts only when independent workstreams, broad study, cross-cutting risk, durable resume value, or isolation materially help.

A direct exit creates no `.ai-work` state, but adaptive model-economy rules still apply.

## 2. Keep useful shared context while it is useful

Fresh workers are not automatically cheaper. For one cohesive task, the current conversation can be the cheapest cache of decisions, repository findings, and validation history.

Use a fresh worker when context boundaries diverge, disposable exploration would pollute expensive context, independent verification helps, a leaf needs a different tier than the root (see §4), or persistence/resume is valuable. Do not isolate sequential steps that strongly reuse the same reasoning merely to follow a process template.

## 3. Exploration and routing are defined once

`MODEL_ROUTING.md` §1–§3 own: search-first/read-second, the explorer contract (compact evidence map, read-only, at most two concurrent), the leaf-signal floors, and the rule that a small hard edit with weak validation deserves a stronger implementer while its exploration stays cheap. Do not restate them here or in phase references; link to the section.

## 4. Elevation is delegation, not a root switch

Prompt caches are keyed by model and (on most models) by effort level. Switching the root session's model or effort re-reads the entire conversation uncached; Anthropic measured an Opus->Haiku mid-session switch as *more* expensive than staying. The cheap way to obtain a different tier is a fresh worker with a minimal prompt whose result returns as a few hundred tokens. This is also what lets a small root model run the skill: it delegates every stage above its tier instead of attempting it.

## 5. Promote instead of restarting

When direct work becomes long-horizon, persist only a compact handoff: original goal; completed work and validated results; active decisions/invariants; relevant paths/symbols; blockers/risks; remaining outcomes; bounded repository status/diff stats. Do not persist conversation narration or invent retroactive TODOs. The promoted plan covers remaining work only.

## 6. Spend model tokens only on judgment

Use deterministic code for lifecycle/state transitions, dependency scheduling, coverage checks, filesystem/path safety, validation execution, compact git evidence, log storage/tails, installer transforms, cleanup, routing floors (`routingctl.py route`), and escalation from recorded failure classes.

Use models for ambiguity resolution, architecture, decomposition, implementation, debugging, and synthesis that genuinely require reasoning. Batch safe independent queries when a program/tool can do so without injecting every intermediate result into model context.

## 7. Progressive disclosure

The entrypoint is a small control plane. Load only the phase-specific reference: routing ambiguity -> `ROUTING.md`; late promotion -> `PROMOTION.md`; full orchestration -> `ORCHESTRATION.md`; model selection -> `MODEL_ROUTING.md` plus **only** the active provider file; study/planning/execution -> their phase references. If provider fallback happens later, load the fallback provider file then. Maintainer material (research basis, publishing) lives under `docs/` and is never loaded at runtime.

## 8. Preserve request evidence; compress derived state

Never shorten authoritative user/request-file evidence merely to save tokens. Derived artifacts replace repeated prose with stable ids, paths, symbols, commands, mappings, compact validation state, and bounded completion memory. Do not copy request paragraphs into study, requirements, plan, every task, and final summary.

## 9. Search first, read second

For repository work the order is search filenames/symbols/keywords, rank likely files, open focused ranges plus necessary dependencies/tests, then widen only when evidence requires it (`MODEL_ROUTING.md` §3). For external research prefer authoritative targeted sources. Save conclusion + planning impact, not article text. Search/retrieval outputs that do not change a decision should not be propagated downstream.

## 10. Minimize shared orchestrated context

Default to no `CONTEXT.md`. Create global/scoped context only for non-obvious facts truly reused by assigned TODOs. Keep single-task facts in the task definition. Reuse cross-task learnings only when they are expensive, validated, directional, and predeclared.

## 11. Preserve stable provider prefixes and logical routing

Claude Code (API/subscription):

- the cached prefix is system prompt + project context + conversation; a change anywhere earlier recomputes everything after it;
- **invalidates**: model switch, effort change (except Fable 5.1 on API/subscription), MCP servers loaded into the prefix, plugin MCP changes, `/compact`, fast-mode toggle, denying a whole tool;
- **keeps**: skill/command invocation, plan mode, output style, permission mode, editing repository files, editing CLAUDE.md mid-session, spawning subagents (they warm their own cache);
- subagents, workflows, and forks get a 5-minute TTL by default; `subagentPromptCacheTtl: 1h` for long orchestrations;
- workflow fan-outs share a sibling's prefix when model/effort/tools/schema/cwd match, so digest-style batches should use one uniform route.

Codex: cached reads ~10% of input; Codex charges no cache writes and no long-context multiplier; `tool_output_token_limit` bounds retained tool output; `model_auto_compact_token_limit` controls compaction.

Runner consequences: worker prompts keep static rules first and per-task values last; every fresh `claude -p`/`codex exec` worker starts cold, so keep its prompt minimal and let the task file carry the detail; never toggle route configuration between attempts of the same worker.

## 12. Route by verified task cost, not price per token

Route each semantic leaf to the cheapest model/effort credibly able to solve it. Newer models at lower effort can dominate older models at higher effort, while stronger models can finish hard work in fewer retries. Use cheap-first when failure is objectively detectable and cheap; start stronger for high-blast-radius decisions with weak validation. Escalate only from recorded `failure_class` evidence (`MODEL_ROUTING.md` §6); do not maintain a user-selected model ceiling.

## 13. Bound tool/report output

Full output belongs in logs. Model/state context gets only decision-relevant excerpts: bounded completion summaries, validation details, failure reasons plus class, risk/follow-up counts, learning guidance, and final repository-change summaries. Do not copy full stack traces/build output into retries when an error excerpt + log path is sufficient. Optional per-worker budgets (`claude.max_turns`, `codex.rollout_token_budget`) turn runaway workers into resumable `budget` failures.

## 14. Final summary uses compact authoritative state

Never concatenate raw worker reports into final-summary input. Use goal, task completion summaries, changed files, deterministic validation status, remaining risks/follow-ups, and bounded repository change evidence. Final/status prose uses an economy route when no difficult synthesis is required.

## 15. Never optimize away quality anchors

Token reduction must not remove complete request evidence, requirement coverage for orchestrated remaining work, task scope/invariants, acceptance criteria, deterministic validation, material failure evidence, resume checkpoints, per-TODO model/effort routing, safety/path guards, or cleanup preservation.

When concision and correctness appear to conflict, first remove repetition, disposable exploration context, and process narration. If a distinction still changes implementation or validation, keep it.
