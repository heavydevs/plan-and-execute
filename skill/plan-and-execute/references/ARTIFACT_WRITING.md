# Precise, concise planning artifacts

Use this contract for every **derived** planning/execution text: study findings, request parts, requirements, plan summaries, TODO definitions, context items, learning files, worker reports, review notes, and final handoff.

Do **not** rewrite or truncate the user's original request. `REQUEST.md` remains verbatim evidence. Concision starts when the request is transformed into structured planning state.

## Goal

Maximize semantic signal per token without weakening requirements, traceability, acceptance criteria, failure evidence, or validation.

Concise means **brief enough that removing another word would risk changing meaning**. It does not mean vague, telegraphic, or lossy.

## Writing rule: one field, one job

Each line or list item should carry one primary semantic unit:

- requirement: observable obligation or constraint;
- finding: evidence-backed fact;
- impact: what the fact changes in planning/validation;
- rationale: why a boundary/decision exists;
- risk: concrete failure mode plus affected outcome when useful;
- acceptance criterion: observable success condition;
- guidance: implementation-specific instruction not already obvious from scope/code;
- context item: cross-task invariant required by every assigned TODO;
- learning: validated discovery that saves a later TODO from expensive rediscovery.

Do not mix requirement + rationale + implementation history in one paragraph. Split only when each part is independently useful.

## Precision rules

1. **Name the actor/object.** Prefer `TokenService rejects expired refresh tokens` to `They should be rejected`.
2. **Use an observable verb.** Prefer `returns 401`, `persists one row`, `keeps API signature X`, `passes test Y`.
3. **State the condition when it changes behavior.** Example: `When refresh token validation fails, the endpoint returns 401 without issuing a new token.`
4. **Use stable nouns, ids, paths, symbols, commands, versions, and thresholds.** References are cheaper and less ambiguous than repeated explanations.
5. **One thought per requirement/criterion.** If two clauses can fail independently, split them.
6. **Separate what from why.** Requirement text states the contract; rationale/impact fields explain why only when the schema asks for it.
7. **Prefer positive statements.** Use negative wording only when the prohibition itself is the contract.
8. **Never add filler to satisfy a perceived minimum.** Short precise text is preferred to a padded explanation.

## Vague wording rejected in derived artifacts

Replace qualitative placeholders with observable conditions. High-confidence smells include:

- `as appropriate`, `as needed`, `when required`, `if required`;
- `etc.`, `and/or`, `but not limited to`;
- `user-friendly`, `adequate`, `sufficient`, `robust`, `quickly`, `easily`;
- Portuguese equivalents such as `conforme apropriado`, `quando necessário`, `se necessário`, `e/ou`, `adequado`, `suficiente`, `robusto`, `rapidamente`, `facilmente`.

A word may be valid in the **original request**. The derived requirement must resolve it into a measurable or explicitly bounded meaning before autostart.

## Derived-text budgets

Budgets are guardrails, not writing targets. Use less when less is enough.

| Artifact field | Maximum |
|---|---:|
| Plan/task title | 120 chars |
| Goal/plan summary | 320 |
| Request part | 280 |
| Requirement | 280 |
| Repository/research finding | 320 |
| Research decision | 240 |
| Assumption/risk/open question | 240 |
| Decomposition strategy | 320 |
| Global constraint | 240 |
| Review note | 240 |
| Task objective | 320 |
| Atomicity/context-boundary rationale | 320–360 |
| Scope item | 200 |
| Implementation guidance | 240 |
| Acceptance criterion | 240 |
| Subtask title / objective | 120 / 280 |
| Learning target reason | 280 |
| Learning topic | 80 |
| Reusable learning guidance | 320 |
| Study rationale | 280 |
| Study synthesis item | 260 |

Validation commands are code-like evidence and may be longer; they are not subject to prose-smell checks.

## Requirements: use controlled natural language when useful

Use an EARS-like shape when it improves precision:

- ubiquitous: `<system/component> shall <observable response>`;
- event-driven: `When <trigger>, <system/component> shall <observable response>`;
- state-driven: `While <state>, <system/component> shall <observable response>`;
- unwanted behavior: `If <failure condition>, <system/component> shall <safe response>`;
- optional feature: `Where <feature/configuration applies>, <system/component> shall <observable response>`.

Do not mechanically force `shall` into every implementation task. The purpose is the structure: condition + responsible object + testable outcome.

### Bad

`The application should robustly handle invalid tokens as appropriate and provide a user-friendly response.`

### Better

`When the access token is invalid, the API returns HTTP 401 with error code INVALID_TOKEN and does not invoke the protected handler.`

## Study artifacts

Record evidence once, not a narrative of the research process.

Prefer:

`I003 src/auth/token.py:88 — refresh tokens expire after 30 days -> migration must preserve the 30-day contract.`

Avoid:

`During our analysis of the repository, we inspected the token implementation and found that there is currently a mechanism which appears to...`

Rules:

- one source finding = fact + planning impact;
- omit search history, dead ends, and generic observations;
- external evidence records publisher/title/version/date/URL plus the conclusion that changes the plan;
- stop when more evidence is unlikely to change architecture, compatibility, task boundaries, risk, or validation.

## Plan and TODO definitions

Keep planning evidence and execution instructions separate.

`manifest.json` is authoritative for traceability, routing, history, context-boundary review evidence, and state. The worker task file should contain only what that worker needs to implement correctly:

- objective;
- assigned context and validated learnings;
- resumable checkpoints;
- scope and expected files;
- non-obvious implementation guidance;
- acceptance criteria;
- validation commands;
- narrow future learning topics when applicable.

Do not repeat in the worker file:

- plan-wide request inventory;
- atomicity rationale already reviewed during planning;
- long isolation prose already present in the worker prompt;
- provider/model routing metadata that the worker cannot change;
- separate requirement/dependency sections when compact metadata already carries the ids.

## Context and learning files

Use references instead of explanation whenever the target can cheaply inspect the source.

A context line should normally fit this shape:

`G001 constraint — API v2 response field 'id' remains a string. (source: R004)`

A learning line should normally fit this shape:

`validation — Reproduce timeout with test X before changing retry order. (refs: tests/x.py::test_timeout, command...)`

Do not include:

- worker transcripts;
- logs;
- broad task summaries;
- generic framework knowledge;
- findings that the target can retrieve cheaply from its own files.

## Worker reports and validation

The report is a machine handoff, not a retrospective.

- summary: what changed and the resulting behavior, normally 1–3 sentences;
- validation result: command/status plus only a bounded diagnostic detail when useful;
- risks/follow-ups: one concrete item per line; empty is preferred to boilerplate;
- full tool output stays in log files;
- failure evidence in state is a bounded excerpt plus a log reference when possible.

The orchestrator reruns deterministic validation, so do not spend report tokens re-explaining successful test output.

## Final summary

Build the final handoff from compact authoritative state:

- plan goal;
- task summaries;
- changed files/areas;
- deterministic validation status;
- recorded remaining risks/follow-ups;
- bounded diff stat.

Never concatenate raw worker reports into the summarizer prompt.

## Review checklist

Before approving a derived artifact, ask:

1. Does every sentence add a requirement, decision, fact, boundary, risk, or verification signal?
2. Can any sentence be replaced by an id/path/symbol/command reference without losing meaning?
3. Is any fact repeated in another field that is already authoritative?
4. Does a qualitative word hide a missing threshold/condition?
5. Does one line contain multiple independently failing obligations?
6. Would a fresh worker interpret the text in only one materially relevant way?
7. Can this field be shorter without losing a necessary distinction?

## Research basis

This contract combines converging guidance rather than relying on one style rule:

- **NASA Systems Engineering Handbook, Appendix C — How to Write a Good Requirement**: active voice, consistent terminology, concise/simple statements, one thought/subject/predicate, testability, traceability, and rejection of ambiguous/unverifiable terms. https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/
- **INCOSE Guide for Writing Requirements, v4 (2023)**: characteristics, rules, patterns, and requirement-quality checks for clear, verifiable requirements. https://www.incose.org/publications/products/requirements-guide
- **Mavin et al., EARS, IEEE RE 2009**: a small controlled-natural-language rule set addressing ambiguity, vagueness, complexity, duplication, wordiness, implementation leakage, and untestability. DOI: 10.1109/RE.2009.9
- **Veizaga, Shin & Briand, IEEE TSE 2024, Automated Smell Detection and Recommendation in Natural Language Requirements**: industrial evaluation of automated requirement-smell detection and controlled-language recommendations. DOI: 10.1109/TSE.2024.3361033
- **Wiegers & Beatty, Software Requirements, 3rd ed.**: practical requirement quality, traceability, prioritization, validation, and specification discipline.
- **Robertson & Robertson, Mastering the Requirements Process**: atomic requirements and structured requirement shells.
- **OpenAI model guidance**: lean prompts, state each instruction once, keep only relevant tools/examples; internal coding-agent evals reported directional quality and token/cost gains from leaner system prompts. https://developers.openai.com/api/docs/guides/latest-model
- **Anthropic, Effective context engineering for AI agents (2025)**: seek the smallest set of high-signal tokens; use progressive disclosure and just-in-time retrieval. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **Liu et al., Lost in the Middle (TACL 2024)**: long-context utilization can degrade depending on position and amount of context. arXiv:2307.03172
- **RepoCoder (EMNLP 2023), Repoformer (ICML 2024), CodePlan (2023), Agentless (FSE 2025)**: repository-level coding benefits from selective localization/retrieval, explicit planning, and deterministic validation instead of blindly supplying the whole repository or preserving long agent histories.

Treat vendor token/cost figures as directional. Validate this skill with its own regression tests and representative real requests.
