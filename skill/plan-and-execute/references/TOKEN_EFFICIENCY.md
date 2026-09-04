# Token-efficiency contract

Use this reference when reviewing prompt/context cost or changing the harness. `ARTIFACT_WRITING.md` owns prose precision/budgets; this file owns **where tokens are spent**.

## Objective

Minimize tokens that do not improve an implementation decision.

A token is justified when it carries current-task requirements, evidence, a decision boundary, failure diagnosis, validation signal, or a durable handoff needed to resume. Everything else should remain in the current useful context, be retrieved later, referenced by id/path, stored outside model context, or omitted.

## 1. Avoid the harness when the harness does not pay for itself

Selective activation is the first and largest optimization.

- cohesive small/medium work stays DIRECT;
- file count and the word `implementation` are not orchestration triggers;
- uncertainty defaults to DIRECT because late promotion is available;
- full planning starts only when independent workstreams, broad study, cross-cutting risk, durable resume value, or isolation materially help.

A direct exit creates no `.ai-work` state and loads no orchestration references.

## 2. Keep useful shared context while it is useful

Fresh workers are not automatically cheaper. For one cohesive task, the current conversation can be the cheapest cache of decisions, repository findings, and validation history.

Use a fresh worker when context boundaries diverge or persistence/resume is valuable. Do not isolate sequential steps that strongly reuse the same reasoning merely to follow a process template.

## 3. Promote instead of restarting

When direct work becomes long-horizon, persist only a compact handoff:

- original goal;
- completed work;
- validated results;
- active decisions/invariants;
- relevant paths/symbols;
- blockers/risks;
- remaining outcomes;
- bounded repository status/diff stats.

Do not persist conversation narration or invent retroactive TODOs. The promoted plan covers remaining work only.

## 4. Spend model tokens only on judgment

Use deterministic code for lifecycle/state transitions, dependency scheduling, coverage checks, filesystem/path safety, validation execution, compact git evidence, log storage/tails, installer transforms, and cleanup.

Use models for ambiguity resolution, architecture, decomposition, implementation, debugging, and synthesis that genuinely require reasoning.

## 5. Progressive disclosure

The entrypoint is a small control plane. Load only the phase-specific reference:

- routing ambiguity -> `ROUTING.md`;
- late promotion -> `PROMOTION.md`;
- full orchestration -> `ORCHESTRATION.md`;
- study/planning/execution/model routing -> only their phase references.

Do not preload the reference directory.

## 6. Preserve request evidence; compress derived state

Never shorten authoritative user/request-file evidence merely to save tokens. Derived artifacts replace repeated prose with stable ids, paths, symbols, commands, mappings, compact validation state, and bounded completion memory.

Do not copy request paragraphs into study, requirements, plan, every task, and final summary.

## 7. Search first, read second

For repository work: search filenames/symbols/keywords, rank likely files, open focused ranges plus necessary dependencies/tests, then widen only when evidence requires it.

For external research, prefer authoritative targeted sources. Save conclusion + planning impact, not article text.

## 8. Minimize shared orchestrated context

Default to no `CONTEXT.md`. Create global/scoped context only for non-obvious facts truly reused by their assigned TODOs. Keep single-task facts in the task definition.

Reuse cross-task learnings only when they are expensive, validated, directional, and predeclared.

## 9. Preserve stable provider prefixes and logical routing

Keep stable execution rules before dynamic task data when provider caching can benefit. Avoid duplicating rules across system prompt, task file, worker prompt, and report schema.

Compile one immutable packet per task revision containing the task definition and only its assigned context/learning files. Include source paths and hashes for provenance. Point the worker at that single packet instead of asking it to perform repeated discovery reads.

Route each TODO to the cheapest tier/effort credibly able to solve that leaf. Keep logical `model_tier` portable across providers; escalate from concrete failure evidence, not overall request size.

## 10. Bound tool/report output

Full output belongs in logs. Model/state context gets only decision-relevant excerpts. Preserve current bounded completion summaries, validation details, failure reasons, risk/follow-up counts, learning guidance, and final repository-change summaries.

Do not copy full stack traces/build output into retries when an error excerpt + log path is sufficient.

The worker reports decisions and acknowledgements, not facts the host can measure. The host owns deterministic validation results, per-attempt changed-file deltas, token/cache/reasoning counts, cost when supplied by the provider, duration, and turn count. Never attribute the whole pre-existing dirty tree to the current attempt.

## 11. Final summary uses compact authoritative state

Never concatenate raw worker reports into final-summary input. Use goal, task completion summaries, changed files, deterministic validation status, remaining risks/follow-ups, and bounded repository change evidence.

## 12. Never optimize away quality anchors

Token reduction must not remove complete request evidence, requirement coverage for orchestrated remaining work, task scope/invariants, acceptance criteria, deterministic validation, material failure evidence, resume checkpoints, per-TODO model/effort routing, safety/path guards, or cleanup preservation.

When concision and correctness appear to conflict, first remove repetition and process narration. If a distinction still changes implementation or validation, keep it.
