# Token-efficiency contract

Use this reference when reviewing prompt/context cost or changing the harness. `ARTIFACT_WRITING.md` owns prose precision/budgets; this file owns **where tokens are spent**.

## Objective

Minimize tokens that do not improve the implementation decision.

A token is justified when it carries current-task requirements, evidence, a decision boundary, failure diagnosis, or validation signal. Everything else should be retrieved later, referenced by id/path, stored outside model context, or omitted.

## 1. Spend model tokens only on judgment

Use deterministic code for:

- lifecycle/state transitions;
- dependency scheduling;
- requirement coverage checks;
- character/list budgets and high-confidence vague-word checks;
- filesystem/path safety;
- validation command execution;
- log storage and tail selection;
- cleanup.

Use models for ambiguity resolution, architecture, decomposition, implementation, debugging, and synthesis that genuinely require reasoning.

## 2. Progressive disclosure beats one large prompt

Load only the current phase reference:

- intake -> `INTAKE.md`;
- study -> `ADAPTIVE_STUDY.md`;
- planning -> `PLANNING_PROTOCOL.md`, then context/spec references when needed;
- execution -> `WORKFLOW.md` and routing only when selecting/escalating a route.

Do not preload the whole skill reference directory.

## 3. Preserve the request; compress derived state

Never shorten the user's original request merely to save tokens. Preserve it verbatim when imported.

Derived artifacts must be smaller because they replace repeated prose with:

- stable `P...` / `R...` / TODO ids;
- atomic fields;
- paths/symbols/commands;
- requirement -> TODO mappings;
- compact completion memory.

Do not copy request paragraphs into study, requirements, PLAN.md, and every task file.

## 4. Search first, read second

For repository work:

1. search filenames/symbols/keywords;
2. rank likely files;
3. open focused ranges/files plus necessary dependencies/tests;
4. widen only when evidence requires it.

For external research, prefer authoritative targeted sources. Save the conclusion + planning impact, not article text.

## 5. Fresh workers are cheaper than polluted long histories

One TODO starts one fresh worker. Pass only:

- one task-definition path;
- exact assigned context files;
- exact assigned validated-learning files;
- repository root and compact execution rules.

Never pass parent chat, full plan, study, future tasks, logs, or previous raw worker reports.

Persist resume state in the manifest/subtasks, not conversational history.

## 6. Minimize shared context

Default to no `CONTEXT.md`.

Create global/scoped context only when the same non-obvious fact is required by all assigned TODOs. Prefer source references to repeated explanation. Keep single-task facts in that task definition.

A relevant fact is not automatically a necessary shared fact.

## 7. Reuse only expensive validated discoveries

`learning_targets` are sparse and directional. Publish a learning only after source deterministic validation and only if a future declared target would otherwise spend meaningful effort rediscovering it.

Prefer:

`validation — Reproduce vendor timeout with test X before changing retry order. (refs: test symbol, command)`

Avoid broad “what we learned” summaries.

## 8. Preserve stable prefixes for provider prompt caching

Keep stable execution rules before dynamic repository/task/route data when provider caching can benefit. Avoid timestamps, task-specific prose, or volatile state in the stable prefix.

Do not duplicate the same rule in the system/default prompt, task file, worker prompt, and report schema. Assign one authoritative layer whenever possible.

## 9. Bound tool and report output

Full output belongs in plan logs. Model/state context gets only the portion needed to decide the next action.

Current concise contract:

- validation `output_tail`: <= 800 chars;
- persisted failure reason: <= ~1,400 chars;
- completion summary: <= 360 chars;
- validation detail: <= 600 chars;
- risks/follow-ups: <= 8 x 240 chars;
- reusable learning guidance: <= 320 chars;
- final repository-change summary: bounded git status/diff stat.

Do not copy stack traces or full build output into a retry prompt when an error excerpt + log path is enough.

## 10. Final summary uses compact authoritative state

Never concatenate worker reports into the final summarizer input.

`SUMMARY_INPUT.json` should contain only:

- goal;
- task id/title + compact completion summary;
- changed files;
- deterministic validation status;
- recorded remaining risks/follow-ups;
- bounded repository change summary.

The raw result/log files remain available for debugging before cleanup but are not re-consumed by default.

## 11. Route proportionally

Start with the cheapest tier/effort plausibly capable of the TODO. Escalate from concrete technical evidence, not because the overall request was large.

Large plans often contain many low/medium leaves. Do not force every leaf onto the model used for planning.

## 12. Never optimize away these quality anchors

Token reduction must not remove:

- complete user-request evidence;
- requirement coverage/traceability;
- task scope/invariants;
- observable acceptance criteria;
- deterministic validation commands/results;
- material failure evidence;
- resume checkpoints;
- safety/path/cleanup guards.

When concision and correctness appear to conflict, first remove repetition and process narration. If a distinction still matters to implementation or validation, keep it.

## Research basis

The contract reflects converging evidence:

- OpenAI model guidance favors lean prompts, stating each instruction once and exposing only relevant tools/examples; internal coding-agent evaluations report directional quality/token/cost improvements from simplification. https://developers.openai.com/api/docs/guides/latest-model
- Anthropic recommends finding the smallest set of high-signal tokens and using progressive disclosure / just-in-time retrieval. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- `Lost in the Middle` shows that more long-context input does not guarantee better use of information. arXiv:2307.03172
- RepoCoder/Repoformer support selective repository retrieval; CodePlan supports explicit dependency-aware planning; Agentless shows strong value from structured localization + repair + deterministic validation.
- NASA/INCOSE/EARS requirements guidance supports atomic, concise, unambiguous, verifiable derived requirements; see `ARTIFACT_WRITING.md`.

Treat reported vendor/paper percentages as directional. Validate this skill with its own regression suite and representative real requests.
