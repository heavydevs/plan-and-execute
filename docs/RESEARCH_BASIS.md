# Research basis

Maintainer reference for the routing, staging, and artifact-writing policies in `skill/plan-and-execute/references/`. It is intentionally outside the skill directory so it is never loaded into model context during ordinary execution. Treat vendor token/cost figures as directional and re-validate the skill with its own regression suites (`routing-evals.json`, `tier-evals.json`) and representative real requests.

## Host mechanics the skill leverages (verified September 2026)

### Claude Code

- **Model/effort** — aliases `haiku`, `sonnet`, `opus`, `fable`, `opusplan` (Opus in plan mode, Sonnet for execution). Effort levels `low|medium|high|xhigh|max` on Opus 5 / Sonnet 5 / Fable 5.1; Opus 5, Sonnet 5, and Fable 5.1 default to adaptive effort; Haiku accepts no effort parameter. Effort shapes thoroughness (files read, tools used, verification before returning), not only thinking time. Anthropic's diagnostic: "did it not *know* enough (bigger model) or not *try* hard enough (more effort)?" — https://code.claude.com/docs/en/model-config, https://claude.com/blog/claude-model-and-effort-level-in-claude-code
- **Subagents** — per-invocation `model` (`sonnet|opus|haiku|fable`), frontmatter `model:`/`effort:`, `CLAUDE_CODE_SUBAGENT_MODEL`, `isolation: worktree`, background execution, resumable via `SendMessage`. The built-in `Explore` agent inherits the main conversation's model (capped at Opus) — it is only cheap when the call names `model: "haiku"`. — https://code.claude.com/docs/en/sub-agents
- **Prompt caching** — cache is keyed by model and (on most models) effort; switching either mid-session re-reads the whole conversation. Skills, plan mode, output style, permission mode, and subagent spawns keep the cache. Subagent/workflow/fork requests get a 5-minute TTL by default (`subagentPromptCacheTtl: 1h`). Anthropic: switching Opus→Haiku mid-session "would actually be more expensive" than staying. — https://code.claude.com/docs/en/prompt-caching, https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
- **Dynamic workflows** — a script (`agent()`, `pipeline()`, `parallel()`, `schema`) orchestrates dozens to hundreds of subagents with intermediate results outside the conversation; same-prefix siblings share the cache; per-stage models; resumable within a session; `ultracode` = xhigh + automatic workflows. — https://code.claude.com/docs/en/workflows

### OpenAI Codex

- **Models** — GPT-5.6 Luna (economy), Terra (standard), Sol (previous strong), GPT-6 Astra (strong/max, released 2026-09-03). OpenAI's calibration: Astra Low outperforms Sol High; users happy with Sol High should move to Astra Low/Medium. Astra always reasons (no `none`). Codex adds no long-context multiplier and no cache-write charge. — https://openai.com/index/gpt-5-6/, https://ustechautomations.com/resources/blog/gpt-6-astra-vs-5-sol-for-codex-token-efficiency-2026
- **Config** — `model`, `model_reasoning_effort` (`minimal|low|medium|high|xhigh`), `plan_mode_reasoning_effort`, `agents.default_subagent_model`, `agents.default_subagent_reasoning_effort`, `agents.max_concurrent_threads_per_session`, `tool_output_token_limit`, `model_auto_compact_token_limit`, `features.rollout_budget.*`. — https://learn.chatgpt.com/docs/config-file/config-reference
- **Subagents** — `.codex/agents/*.toml` (`model`, `model_reasoning_effort`, `sandbox_mode`, `developer_instructions`); built-in roles `default`, `worker`, `explorer`; explicit spawn values override `[agents]` defaults which override the parent. "Subagent workflows consume more tokens than comparable single-agent runs." — https://learn.chatgpt.com/docs/agent-configuration/subagents

### Google Antigravity

- **Planning vs Fast mode**; artifacts (task list, implementation plan, walkthrough, recordings) as human review checkpoints with a "Request review / Always proceed" policy. — https://antigravity.google/docs/artifact-review/
- **Subagents** — `invoke_subagent` with `model: inherit|flash|pro`, isolated context, workspace `inherit|branch|share`, nesting limit 10. — https://antigravity.google/docs/subagents/
- **/boost** — user-triggered pipeline: orchestrator strategy → parallel specialised subagents in isolated scopes → synthesis with multi-round verification. — https://antigravity.google/docs/boost/
- **Managed agent API** — `max_total_tokens` budget returning `status: incomplete` that resumes by `interaction_id`/`environment_id`; compaction at ~135k tokens; 50–70% of input typically cached. — https://ai.google.dev/gemini-api/docs/antigravity-agent
- The Gemini CLI was sunset on 2026-06-18 and replaced by the Antigravity CLI. — https://www.analyticsvidhya.com/blog/2026/05/google-antigravity-2-0/
- **Antigravity CLI headless contract** (`agy`): `-p`/`--print`/`--prompt <prompt>`, `--output-format text|json|stream-json` (JSON envelope: `response`, `conversation_id`, `status`, `usage`, `structured_output` with `--json-schema <schema|file>`), `--model <slug>`, `--effort low|medium|high`, `--dangerously-skip-permissions`, `--sandbox`, `--print-timeout` (default `5m`), `--continue`/`--conversation` for resume. — https://antigravity.google/docs/cli/headless/ ; known early bug: stdout dropped under non-TTY in 1.0.0 — https://github.com/google-antigravity/antigravity-cli/issues/76

## Routing and cascades

- Chen, Zaharia & Zou, **FrugalGPT** (2023/2024): LLM cascades that query cheaper models first and escalate when a quality signal is insufficient — the skill's deterministic validation is that signal.
- Ong et al., **RouteLLM** (2024) and Song et al., **IRT-Router** (2025): learned routers predicting query difficulty vs model ability; the skill's leaf-signal table is a hand-written, auditable equivalent.
- **Cluster, Route, Escalate** (2026, arXiv 2606.27457) and **CascadeDebate** (2026, arXiv 2604.12262): escalation should spend extra computation where uncertainty is highest — the origin of the `failure_class` rule (semantic jumps a tier; mechanical repeats the rung).
- Anthropic, **Building effective agents** (2024): routing "easy/common questions to smaller models and hard/unusual questions to more capable models" is a first-class workflow.
- Anthropic, **How we built our multi-agent research system** (2025): scale effort to query complexity; subagents persist artifacts and return lightweight references; token usage explains most of the performance variance.
- Anthropic, **Effective harnesses for long-running agents** (2025) and **Effective context engineering for AI agents** (2025): initializer/worker phases, structured persistent artifacts, progressive disclosure, just-in-time retrieval.
- OpenAI, **The builder's guide to GPT-5.6** (2026): reuse prior work, decompose appropriately, move deterministic filtering/aggregation into code.

## Long context and repository-scale coding

- Liu et al., **Lost in the Middle**, TACL 2024 (arXiv 2307.03172): long-context utilization degrades with the position/amount of relevant information.
- Bairi et al., **CodePlan**, FSE 2024: repository-scale interdependent changes benefit from explicit planning, dependency/change-impact analysis, and localized LLM calls.
- Zhang et al., **RepoCoder**, EMNLP 2023; **Repoformer**, ICML 2024; **Agentless**, FSE 2025: selective localization/retrieval and deterministic validation beat unselective whole-repository context or long agent histories.

## Requirement writing (ARTIFACT_WRITING.md)

- NASA Systems Engineering Handbook, Appendix C — How to Write a Good Requirement. https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/
- INCOSE Guide for Writing Requirements, v4 (2023). https://www.incose.org/publications/products/requirements-guide
- Mavin et al., **EARS**, IEEE RE 2009. DOI: 10.1109/RE.2009.9
- Veizaga, Shin & Briand, IEEE TSE 2024, Automated Smell Detection and Recommendation in Natural Language Requirements. DOI: 10.1109/TSE.2024.3361033
- Wiegers & Beatty, *Software Requirements*, 3rd ed.; Robertson & Robertson, *Mastering the Requirements Process*.
- OpenAI model guidance on lean prompts (state each instruction once; keep only relevant tools/examples). https://developers.openai.com/api/docs/guides/latest-model
- Anthropic, **Effective context engineering for AI agents** (2025). https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

## Incremental invalidation (SHARED_PATTERNS.md)

Build-system research defines minimal rebuilding as rerunning only tasks that transitively depend on changed inputs; contract-compatibility workflows re-verify consumers on incompatible changes; ADR practice supersedes decisions rather than rewriting history. A pattern revision is a changed input and its signatory TODOs are the dependents.
