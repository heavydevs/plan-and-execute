# External source register

Access date: 2026-10-28. Each record states what was actually read; this is not a claim of authenticated provider testing or of reading entire books.

## E001 - Agent Skills specification

Publisher: Agent Skills. Type: official_documentation.

URL: https://agentskills.io/specification

Finding: The skill entrypoint and on-demand resources provide a small discovery surface without requiring all reference material in every invocation.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E002 - Building effective agents

Publisher: Anthropic. Type: engineering_article.

URL: https://www.anthropic.com/research/building-effective-agents

Finding: Workflow patterns should earn their complexity; routing, parallelization and evaluator loops have different purposes.

Verification scope: Read the engineering discussion of workflow patterns and complexity; not a benchmark of this repository.

## E003 - Effective context engineering for AI agents

Publisher: Anthropic. Type: engineering_article.

URL: https://www.anthropic.com/research/effective-context-engineering-for-ai-agents

Finding: Context selection, compact summaries and retrieval are engineering choices; more accumulated material is not automatically better.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E004 - Rethinking skills and prompts for GPT-6 Astra

Publisher: OpenAI. Type: engineering_article.

URL: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

Finding: Precise selection criteria and lightweight, focused instructions avoid imposing unnecessary process on every request.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E005 - Evaluating skills

Publisher: OpenAI. Type: engineering_article.

URL: https://developers.openai.com/blog/eval-skills

Finding: Evaluate observable behavior on task cases rather than treating a plausible response as proof of skill quality.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E006 - Lost in the Middle: How Language Models Use Long Contexts

Publisher: Liu et al. / arXiv. Type: research_paper.

URL: https://arxiv.org/abs/2307.03172

Finding: The experiments show position-sensitive retrieval in the studied long-context tasks; the result is not a universal threshold for current models.

Verification scope: Read parsed paper text and experimental framing; no independent replication.

## E007 - Effective harnesses for long-running agents

Publisher: Anthropic. Type: engineering_article.

URL: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents

Finding: Durable progress artifacts, incremental changes and explicit tests support work that crosses context windows.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E008 - Agents, adapted from AI Engineering

Publisher: Chip Huyen. Type: book_excerpt.

URL: https://huyenchip.com/2025/01/07/agents.html

Finding: Planning, tools and evaluation introduce their own failure modes and costs; agent quality needs end-to-end measurement.

Verification scope: Read the author-published agents chapter excerpt. The complete AI Engineering book was not accessed.

## E009 - AI engineering pitfalls

Publisher: Chip Huyen. Type: engineering_article.

URL: https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html

Finding: Prefer deterministic solutions where sufficient and evaluate before increasing system complexity.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E010 - Reflexion: Language Agents with Verbal Reinforcement Learning

Publisher: Shinn et al. / arXiv. Type: research_paper.

URL: https://arxiv.org/abs/2303.11366

Finding: The paper studies verbal feedback and episodic memory with task feedback; it does not establish that an unverified failure narrative is correct.

Verification scope: Read parsed paper sections; no reproduction or generalization of reported benchmark percentages.

## E011 - Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models

Publisher: Zhang et al. / arXiv. Type: research_paper.

URL: https://arxiv.org/abs/2510.04618

Finding: Incremental context curation is evaluated as an alternative to repeatedly compressing an entire evolving playbook.

Verification scope: Read parsed paper framing and mechanism; no replication and no claim of gains for this skill.

## E012 - FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance

Publisher: Chen, Zaharia and Zou / arXiv. Type: research_paper.

URL: https://arxiv.org/abs/2305.05176

Finding: Cascades can trade model cost against task quality when evaluated on a defined workload.

Verification scope: Read paper abstract and method framing; published savings are not measurements of this repository.

## E013 - RouteLLM: Learning to Route LLMs from Preference Data

Publisher: Ong et al. / arXiv. Type: research_paper.

URL: https://arxiv.org/abs/2406.18665

Finding: Learned routing uses workload evidence; preference labels and software acceptance are different targets.

Verification scope: Read parsed paper sections; no model training or reproduction.

## E014 - AutoMix: Automatically Mixing Language Models

Publisher: Aggarwal et al. / arXiv. Type: research_paper.

URL: https://arxiv.org/abs/2310.12963

Finding: Noisy self-verification can support routing policies, but its assumptions require evaluation and do not replace deterministic software tests.

Verification scope: Read parsed paper mechanism and evaluation framing; not a live routing trial.

## E015 - Claude Code CLI reference

Publisher: Anthropic. Type: official_documentation.

URL: https://code.claude.com/docs/en/cli-reference

Finding: Print-mode session persistence, structured output, permissions and effort are explicit CLI options; disabling persistence prevents normal session resumption.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E016 - Create custom subagents

Publisher: Anthropic. Type: official_documentation.

URL: https://code.claude.com/docs/en/sub-agents

Finding: Subagents have separate context and configurable model/tool boundaries; isolation and permissions must be selected explicitly.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E017 - Manage costs effectively

Publisher: Anthropic. Type: official_documentation.

URL: https://code.claude.com/docs/en/costs

Finding: Usage and billing depend on the execution route; subscription consumption and API accounting must not be conflated.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E018 - Prompt caching

Publisher: Anthropic. Type: official_documentation.

URL: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

Finding: Caching depends on prefix structure, model and cache policy; write/read economics and lifetimes are not universal constants.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E019 - Non-interactive mode

Publisher: OpenAI. Type: official_documentation.

URL: https://learn.chatgpt.com/docs/non-interactive-mode

Finding: Codex non-interactive execution exposes structured output and ephemeral operation; CLI events and the final task artifact are separate concerns.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E020 - Security

Publisher: OpenAI. Type: official_documentation.

URL: https://learn.chatgpt.com/docs/security

Finding: Sandbox boundaries and approval policies determine tool authority; a prompt saying read-only is not a security boundary.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E021 - Prompt caching

Publisher: OpenAI. Type: official_documentation.

URL: https://developers.openai.com/api/docs/guides/prompt-caching

Finding: Cache eligibility depends on the effective prefix and supported cache policy; use observed cache counters and current billing instead of historical universal pricing rules.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E022 - Antigravity CLI reference

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/cli/reference/

Finding: The CLI documents model discovery, conversation controls and model-dependent effort. A listed effort value is not proof every model accepts it.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E023 - Headless mode

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/cli/headless/

Finding: Headless execution has explicit output and lifecycle controls that need a version-specific adapter contract.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E024 - Permissions

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/permissions/

Finding: Permission approval and execution confinement are distinct controls; observation must use a verified restricted execution path.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E025 - Models

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/models/

Finding: Available model choices are a provider-maintained catalog, not a timeless correspondence between model names and logical skill tiers.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E026 - Plans

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/plans

Finding: Plan limits and credit policies vary; account-specific available quotas must be discovered rather than inferred solely from brand names.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E027 - Usage command

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/cli/commands/usage

Finding: The CLI exposes usage inspection; capability and quota observations should carry retrieval time and account/profile scope.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E028 - Gemini CLI migration

Publisher: Google. Type: official_documentation.

URL: https://antigravity.google/docs/cli/gcli-migration/

Finding: Migration guidance exists, but legacy Gemini and Antigravity remain distinct command contracts for compatibility testing.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E029 - Headless mode

Publisher: Qwen Code. Type: official_documentation.

URL: https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/

Finding: Qwen provides headless output, session and budget controls; permission automation does not itself establish sandbox confinement.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E030 - kimi command, current documentation

Publisher: Moonshot AI. Type: official_documentation.

URL: https://moonshotai.github.io/kimi-code/en/reference/kimi-command

Finding: Current documentation makes --prompt non-interactive and rejects combining it with --yolo, --auto or --plan. Adapter selection must be version-aware.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E031 - kimi command, legacy documentation

Publisher: Moonshot AI. Type: official_documentation.

URL: https://moonshotai.github.io/kimi-cli/en/reference/kimi-command.html

Finding: Older documentation uses --print and different non-interactive permission semantics; do not mix its flags with the current command contract.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E032 - Trae Agent README and CLI examples

Publisher: ByteDance. Type: official_code.

URL: https://github.com/bytedance/trae-agent

Finding: The open-source Trae Agent CLI configures underlying model providers and can write trajectories; it is not the TRAE IDE protocol.

Verification scope: Read the official repository README/CLI examples; no installed CLI or authenticated execution.

## E033 - Muse Code configuration

Publisher: Meta. Type: official_documentation.

URL: https://dev.meta.ai/docs/muse-code/configuration

Finding: Muse headless execution and session logging have explicit controls, including disabling session logs; persistence is a deliberate operational choice.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E034 - Extending Muse Code

Publisher: Meta. Type: official_documentation.

URL: https://dev.meta.ai/docs/muse-code/extending

Finding: Child execution does not imply an isolated checkout; worktree and session choices need explicit configuration.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E035 - Claude Code integration

Publisher: Z.AI. Type: official_documentation.

URL: https://docs.z.ai/devpack/tool/claude

Finding: Claude Code model aliases can map to GLM endpoints and models. The host binary or alias does not identify the underlying inference provider.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E036 - Anthropic API compatibility

Publisher: DeepSeek. Type: official_documentation.

URL: https://api-docs.deepseek.com/guides/anthropic_api/

Finding: An Anthropic-compatible endpoint is an API adaptation, not proof of identical thinking, model or billing semantics.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E037 - Thinking mode

Publisher: DeepSeek. Type: official_documentation.

URL: https://api-docs.deepseek.com/guides/thinking_mode/

Finding: Thinking and reasoning controls are provider/model specific and must be translated using supported native parameters.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E038 - Fallbacks and provider failover

Publisher: LiteLLM. Type: official_documentation.

URL: https://docs.litellm.ai/docs/proxy/reliability

Finding: Retry counts, cooldown and fallback order are explicit reliability controls; transport recovery is not software correctness validation.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E039 - Failover and fallbacks explained

Publisher: OpenRouter. Type: engineering_article.

URL: https://openrouter.ai/blog/insights/reliability-failover/

Finding: Provider failover and switching models are separate policies; a successful HTTP response does not establish that an answer is correct.

Verification scope: Read official search excerpt on failover and model order; not provider benchmark or account configuration.

## E040 - Timeouts, retries, and backoff with jitter

Publisher: Amazon Builders Library. Type: engineering_article.

URL: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/

Finding: Retries can amplify failures and repeat side effects; bounded backoff, jitter and idempotency are separate reliability decisions.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E041 - subprocess module

Publisher: Python Software Foundation. Type: official_documentation.

URL: https://docs.python.org/3/library/subprocess.html

Finding: Subprocess timeout, pipe draining, cleanup and memory use require explicit handling; communication buffers are not an unbounded-log solution.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E042 - Job Objects

Publisher: Microsoft. Type: official_documentation.

URL: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

Finding: Job Objects group Windows processes and can terminate associated descendants, subject to documented breakaway behavior.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E043 - Monitoring Distributed Systems, Site Reliability Engineering chapter 6

Publisher: Google SRE. Type: book_chapter.

URL: https://sre.google/sre-book/monitoring-distributed-systems/

Finding: Monitoring distinguishes internal signals from externally observable behavior and should surface actionable problems rather than noise.

Verification scope: Read the public chapter; not the entire SRE book.

## E044 - Logging Cheat Sheet

Publisher: OWASP. Type: official_documentation.

URL: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

Finding: Logs should exclude or protect secrets, sanitize untrusted data, restrict access and follow an explicit retention policy.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E045 - Logs data model

Publisher: OpenTelemetry. Type: official_documentation.

URL: https://opentelemetry.io/docs/specs/otel/logs/data-model/

Finding: Event time, observed time, severity, resource and trace correlation are distinct log attributes.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E046 - File Log Receiver README

Publisher: OpenTelemetry. Type: official_code.

URL: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/filelogreceiver

Finding: File identity, offsets and truncation/rotation policy determine what a tailer has actually read.

Verification scope: Read official receiver documentation, including rotation and copytruncate behavior; no collector integration was installed.

## E047 - Persistence

Publisher: LangChain. Type: official_documentation.

URL: https://docs.langchain.com/oss/python/langgraph/persistence

Finding: Thread checkpoints and cross-thread stores have distinct lifetimes; durable state is not the same as a conversation transcript.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E048 - package.json files field

Publisher: npm. Type: official_documentation.

URL: https://docs.npmjs.com/cli/v11/configuring-npm/package-json/

Finding: The files allowlist and ignore rules determine tarball membership; some entries have special inclusion rules.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E049 - npm pack

Publisher: npm. Type: official_documentation.

URL: https://docs.npmjs.com/cli/v11/commands/npm-pack/

Finding: Dry-run and JSON output let packaging tests inspect the actual proposed file list without publishing.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E050 - Visual comparisons

Publisher: Microsoft Playwright. Type: official_documentation.

URL: https://playwright.dev/docs/test-snapshots

Finding: Screenshot regression needs a controlled rendering environment; matching pixels alone does not prove usability.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E051 - Web Content Accessibility Guidelines 2.2

Publisher: W3C. Type: official_documentation.

URL: https://www.w3.org/TR/WCAG22/

Finding: Accessibility criteria provide testable product requirements distinct from subjective visual preference.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E052 - Structured model outputs

Publisher: OpenAI. Type: official_documentation.

URL: https://developers.openai.com/api/docs/guides/structured-outputs

Finding: Structured output constrains shape but does not certify task success; supported schema subsets require adapter-specific validation.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E053 - Evaluation best practices

Publisher: OpenAI. Type: official_documentation.

URL: https://developers.openai.com/api/docs/guides/evaluation-best-practices

Finding: Task-specific, representative evaluations and continuous regression checks are preferable to anecdotal success.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E054 - Work with sessions, Agent SDK

Publisher: Anthropic. Type: official_documentation.

URL: https://code.claude.com/docs/en/agent-sdk/sessions

Finding: Sessions persist conversation history, not filesystem state; replay/resume and source changes must be handled independently.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E055 - GITHUB_TOKEN permissions

Publisher: GitHub. Type: official_documentation.

URL: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token

Finding: Workflow tokens should have only the permissions required by the job.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E056 - os.replace and operating-system interfaces

Publisher: Python Software Foundation. Type: official_documentation.

URL: https://docs.python.org/3/library/os.html#os.replace

Finding: Atomic replacement is a filesystem operation with platform constraints, not a guarantee of an entire multi-file transaction surviving every crash.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E057 - JSON Schema object reference

Publisher: JSON Schema. Type: official_documentation.

URL: https://json-schema.org/understanding-json-schema/reference/object

Finding: Property validation, required keys and rejection of additional properties are distinct schema controls.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E058 - Semantic Versioning 2.0.0

Publisher: SemVer. Type: official_documentation.

URL: https://semver.org/

Finding: Compatibility must be described against a declared public contract; version labels alone do not migrate persisted state.

Verification scope: Relevant parsed documentation sections; not an authenticated CLI experiment.
