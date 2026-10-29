# Source register - research revision 2

W-prefixed records were inspected in this revision through web search or page reads. Their scope is stated individually. E-prefixed records preserve previous research and are not all newly rechecked. Source counts are provenance, not a measure of research quality.

Original publications, vendor documentation and public author resources support bounded claims. No full-book reading, live account qualification or independent code review is asserted.

## E001 - Agent Skills specification

Publisher: Agent Skills. Access date: 2026-10-28. Research round: 1.

Source: https://agentskills.io/specification

Finding: The skill entrypoint and on-demand resources provide a small discovery surface without requiring all reference material in every invocation.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E002 - Building effective agents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://www.anthropic.com/research/building-effective-agents

Finding: Workflow patterns should earn their complexity; routing, parallelization and evaluator loops have different purposes.

Reading scope: Read the engineering discussion of workflow patterns and complexity; not a benchmark of this repository.

## E003 - Effective context engineering for AI agents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://www.anthropic.com/research/effective-context-engineering-for-ai-agents

Finding: Context selection, compact summaries and retrieval are engineering choices; more accumulated material is not automatically better.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E004 - Rethinking skills and prompts for GPT-6 Astra

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

Finding: Precise selection criteria and lightweight, focused instructions avoid imposing unnecessary process on every request.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E005 - Evaluating skills

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://developers.openai.com/blog/eval-skills

Finding: Evaluate observable behavior on task cases rather than treating a plausible response as proof of skill quality.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E006 - Lost in the Middle: How Language Models Use Long Contexts

Publisher: Liu et al. / arXiv. Access date: 2026-10-28. Research round: 1.

Source: https://arxiv.org/abs/2307.03172

Finding: The experiments show position-sensitive retrieval in the studied long-context tasks; the result is not a universal threshold for current models.

Reading scope: Read parsed paper text and experimental framing; no independent replication.

## E007 - Effective harnesses for long-running agents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents

Finding: Durable progress artifacts, incremental changes and explicit tests support work that crosses context windows.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E008 - Agents, adapted from AI Engineering

Publisher: Chip Huyen. Access date: 2026-10-28. Research round: 1.

Source: https://huyenchip.com/2025/01/07/agents.html

Finding: Planning, tools and evaluation introduce their own failure modes and costs; agent quality needs end-to-end measurement.

Reading scope: Read the author-published agents chapter excerpt. The complete AI Engineering book was not accessed.

## E009 - AI engineering pitfalls

Publisher: Chip Huyen. Access date: 2026-10-28. Research round: 1.

Source: https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html

Finding: Prefer deterministic solutions where sufficient and evaluate before increasing system complexity.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E010 - Reflexion: Language Agents with Verbal Reinforcement Learning

Publisher: Shinn et al. / arXiv. Access date: 2026-10-28. Research round: 1.

Source: https://arxiv.org/abs/2303.11366

Finding: The paper studies verbal feedback and episodic memory with task feedback; it does not establish that an unverified failure narrative is correct.

Reading scope: Read parsed paper sections; no reproduction or generalization of reported benchmark percentages.

## E011 - Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models

Publisher: Zhang et al. / arXiv. Access date: 2026-10-28. Research round: 1.

Source: https://arxiv.org/abs/2510.04618

Finding: Incremental context curation is evaluated as an alternative to repeatedly compressing an entire evolving playbook.

Reading scope: Read parsed paper framing and mechanism; no replication and no claim of gains for this skill.

## E012 - FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance

Publisher: Chen, Zaharia and Zou / arXiv. Access date: 2026-10-28. Research round: 1.

Source: https://arxiv.org/abs/2305.05176

Finding: Cascades can trade model cost against task quality when evaluated on a defined workload.

Reading scope: Read paper abstract and method framing; published savings are not measurements of this repository.

## E013 - RouteLLM: Learning to Route LLMs from Preference Data

Publisher: Ong et al. / arXiv. Access date: 2026-10-28. Research round: 1.

Source: https://arxiv.org/abs/2406.18665

Finding: Learned routing uses workload evidence; preference labels and software acceptance are different targets.

Reading scope: Read parsed paper sections; no model training or reproduction.

## E014 - AutoMix: Automatically Mixing Language Models

Publisher: Aggarwal et al. / arXiv. Access date: 2026-10-28. Research round: 1.

Source: https://arxiv.org/abs/2310.12963

Finding: Noisy self-verification can support routing policies, but its assumptions require evaluation and do not replace deterministic software tests.

Reading scope: Read parsed paper mechanism and evaluation framing; not a live routing trial.

## E015 - Claude Code CLI reference

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://code.claude.com/docs/en/cli-reference

Finding: Print-mode session persistence, structured output, permissions and effort are explicit CLI options; disabling persistence prevents normal session resumption.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E016 - Create custom subagents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://code.claude.com/docs/en/sub-agents

Finding: Subagents have separate context and configurable model/tool boundaries; isolation and permissions must be selected explicitly.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E017 - Manage costs effectively

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://code.claude.com/docs/en/costs

Finding: Usage and billing depend on the execution route; subscription consumption and API accounting must not be conflated.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E018 - Prompt caching

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

Finding: Caching depends on prefix structure, model and cache policy; write/read economics and lifetimes are not universal constants.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E019 - Non-interactive mode

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://learn.chatgpt.com/docs/non-interactive-mode

Finding: Codex non-interactive execution exposes structured output and ephemeral operation; CLI events and the final task artifact are separate concerns.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E020 - Security

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://learn.chatgpt.com/docs/security

Finding: Sandbox boundaries and approval policies determine tool authority; a prompt saying read-only is not a security boundary.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E021 - Prompt caching

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://developers.openai.com/api/docs/guides/prompt-caching

Finding: Cache eligibility depends on the effective prefix and supported cache policy; use observed cache counters and current billing instead of historical universal pricing rules.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E022 - Antigravity CLI reference

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/cli/reference/

Finding: The CLI documents model discovery, conversation controls and model-dependent effort. A listed effort value is not proof every model accepts it.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E023 - Headless mode

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/cli/headless/

Finding: Headless execution has explicit output and lifecycle controls that need a version-specific adapter contract.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E024 - Permissions

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/permissions/

Finding: Permission approval and execution confinement are distinct controls; observation must use a verified restricted execution path.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E025 - Models

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/models/

Finding: Available model choices are a provider-maintained catalog, not a timeless correspondence between model names and logical skill tiers.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E026 - Plans

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/plans

Finding: Plan limits and credit policies vary; account-specific available quotas must be discovered rather than inferred solely from brand names.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E027 - Usage command

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/cli/commands/usage

Finding: The CLI exposes usage inspection; capability and quota observations should carry retrieval time and account/profile scope.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E028 - Gemini CLI migration

Publisher: Google. Access date: 2026-10-28. Research round: 1.

Source: https://antigravity.google/docs/cli/gcli-migration/

Finding: Migration guidance exists, but legacy Gemini and Antigravity remain distinct command contracts for compatibility testing.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E029 - Headless mode

Publisher: Qwen Code. Access date: 2026-10-28. Research round: 1.

Source: https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/

Finding: Qwen provides headless output, session and budget controls; permission automation does not itself establish sandbox confinement.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E030 - kimi command, current documentation

Publisher: Moonshot AI. Access date: 2026-10-28. Research round: 1.

Source: https://moonshotai.github.io/kimi-code/en/reference/kimi-command

Finding: Current documentation makes --prompt non-interactive and rejects combining it with --yolo, --auto or --plan. Adapter selection must be version-aware.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E031 - kimi command, legacy documentation

Publisher: Moonshot AI. Access date: 2026-10-28. Research round: 1.

Source: https://moonshotai.github.io/kimi-cli/en/reference/kimi-command.html

Finding: Older documentation uses --print and different non-interactive permission semantics; do not mix its flags with the current command contract.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E032 - Trae Agent README and CLI examples

Publisher: ByteDance. Access date: 2026-10-28. Research round: 1.

Source: https://github.com/bytedance/trae-agent

Finding: The open-source Trae Agent CLI configures underlying model providers and can write trajectories; it is not the TRAE IDE protocol.

Reading scope: Read the official repository README/CLI examples; no installed CLI or authenticated execution.

## E033 - Muse Code configuration

Publisher: Meta. Access date: 2026-10-28. Research round: 1.

Source: https://dev.meta.ai/docs/muse-code/configuration

Finding: Muse headless execution and session logging have explicit controls, including disabling session logs; persistence is a deliberate operational choice.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E034 - Extending Muse Code

Publisher: Meta. Access date: 2026-10-28. Research round: 1.

Source: https://dev.meta.ai/docs/muse-code/extending

Finding: Child execution does not imply an isolated checkout; worktree and session choices need explicit configuration.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E035 - Claude Code integration

Publisher: Z.AI. Access date: 2026-10-28. Research round: 1.

Source: https://docs.z.ai/devpack/tool/claude

Finding: Claude Code model aliases can map to GLM endpoints and models. The host binary or alias does not identify the underlying inference provider.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E036 - Anthropic API compatibility

Publisher: DeepSeek. Access date: 2026-10-28. Research round: 1.

Source: https://api-docs.deepseek.com/guides/anthropic_api/

Finding: An Anthropic-compatible endpoint is an API adaptation, not proof of identical thinking, model or billing semantics.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E037 - Thinking mode

Publisher: DeepSeek. Access date: 2026-10-28. Research round: 1.

Source: https://api-docs.deepseek.com/guides/thinking_mode/

Finding: Thinking and reasoning controls are provider/model specific and must be translated using supported native parameters.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E038 - Fallbacks and provider failover

Publisher: LiteLLM. Access date: 2026-10-28. Research round: 1.

Source: https://docs.litellm.ai/docs/proxy/reliability

Finding: Retry counts, cooldown and fallback order are explicit reliability controls; transport recovery is not software correctness validation.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E039 - Failover and fallbacks explained

Publisher: OpenRouter. Access date: 2026-10-28. Research round: 1.

Source: https://openrouter.ai/blog/insights/reliability-failover/

Finding: Provider failover and switching models are separate policies; a successful HTTP response does not establish that an answer is correct.

Reading scope: Read official search excerpt on failover and model order; not provider benchmark or account configuration.

## E040 - Timeouts, retries, and backoff with jitter

Publisher: Amazon Builders Library. Access date: 2026-10-28. Research round: 1.

Source: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/

Finding: Retries can amplify failures and repeat side effects; bounded backoff, jitter and idempotency are separate reliability decisions.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E041 - subprocess module

Publisher: Python Software Foundation. Access date: 2026-10-28. Research round: 1.

Source: https://docs.python.org/3/library/subprocess.html

Finding: Subprocess timeout, pipe draining, cleanup and memory use require explicit handling; communication buffers are not an unbounded-log solution.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E042 - Job Objects

Publisher: Microsoft. Access date: 2026-10-28. Research round: 1.

Source: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

Finding: Job Objects group Windows processes and can terminate associated descendants, subject to documented breakaway behavior.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E043 - Monitoring Distributed Systems, Site Reliability Engineering chapter 6

Publisher: Google SRE. Access date: 2026-10-28. Research round: 1.

Source: https://sre.google/sre-book/monitoring-distributed-systems/

Finding: Monitoring distinguishes internal signals from externally observable behavior and should surface actionable problems rather than noise.

Reading scope: Read the public chapter; not the entire SRE book.

## E044 - Logging Cheat Sheet

Publisher: OWASP. Access date: 2026-10-28. Research round: 1.

Source: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

Finding: Logs should exclude or protect secrets, sanitize untrusted data, restrict access and follow an explicit retention policy.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E045 - Logs data model

Publisher: OpenTelemetry. Access date: 2026-10-28. Research round: 1.

Source: https://opentelemetry.io/docs/specs/otel/logs/data-model/

Finding: Event time, observed time, severity, resource and trace correlation are distinct log attributes.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E046 - File Log Receiver README

Publisher: OpenTelemetry. Access date: 2026-10-28. Research round: 1.

Source: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/filelogreceiver

Finding: File identity, offsets and truncation/rotation policy determine what a tailer has actually read.

Reading scope: Read official receiver documentation, including rotation and copytruncate behavior; no collector integration was installed.

## E047 - Persistence

Publisher: LangChain. Access date: 2026-10-28. Research round: 1.

Source: https://docs.langchain.com/oss/python/langgraph/persistence

Finding: Thread checkpoints and cross-thread stores have distinct lifetimes; durable state is not the same as a conversation transcript.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E048 - package.json files field

Publisher: npm. Access date: 2026-10-28. Research round: 1.

Source: https://docs.npmjs.com/cli/v11/configuring-npm/package-json/

Finding: The files allowlist and ignore rules determine tarball membership; some entries have special inclusion rules.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E049 - npm pack

Publisher: npm. Access date: 2026-10-28. Research round: 1.

Source: https://docs.npmjs.com/cli/v11/commands/npm-pack/

Finding: Dry-run and JSON output let packaging tests inspect the actual proposed file list without publishing.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E050 - Visual comparisons

Publisher: Microsoft Playwright. Access date: 2026-10-28. Research round: 1.

Source: https://playwright.dev/docs/test-snapshots

Finding: Screenshot regression needs a controlled rendering environment; matching pixels alone does not prove usability.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E051 - Web Content Accessibility Guidelines 2.2

Publisher: W3C. Access date: 2026-10-28. Research round: 1.

Source: https://www.w3.org/TR/WCAG22/

Finding: Accessibility criteria provide testable product requirements distinct from subjective visual preference.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E052 - Structured model outputs

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://developers.openai.com/api/docs/guides/structured-outputs

Finding: Structured output constrains shape but does not certify task success; supported schema subsets require adapter-specific validation.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E053 - Evaluation best practices

Publisher: OpenAI. Access date: 2026-10-28. Research round: 1.

Source: https://developers.openai.com/api/docs/guides/evaluation-best-practices

Finding: Task-specific, representative evaluations and continuous regression checks are preferable to anecdotal success.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E054 - Work with sessions, Agent SDK

Publisher: Anthropic. Access date: 2026-10-28. Research round: 1.

Source: https://code.claude.com/docs/en/agent-sdk/sessions

Finding: Sessions persist conversation history, not filesystem state; replay/resume and source changes must be handled independently.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E055 - GITHUB_TOKEN permissions

Publisher: GitHub. Access date: 2026-10-28. Research round: 1.

Source: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token

Finding: Workflow tokens should have only the permissions required by the job.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E056 - os.replace and operating-system interfaces

Publisher: Python Software Foundation. Access date: 2026-10-28. Research round: 1.

Source: https://docs.python.org/3/library/os.html#os.replace

Finding: Atomic replacement is a filesystem operation with platform constraints, not a guarantee of an entire multi-file transaction surviving every crash.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E057 - JSON Schema object reference

Publisher: JSON Schema. Access date: 2026-10-28. Research round: 1.

Source: https://json-schema.org/understanding-json-schema/reference/object

Finding: Property validation, required keys and rejection of additional properties are distinct schema controls.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## E058 - Semantic Versioning 2.0.0

Publisher: SemVer. Access date: 2026-10-28. Research round: 1.

Source: https://semver.org/

Finding: Compatibility must be described against a declared public contract; version labels alone do not migrate persisted state.

Reading scope: Relevant parsed documentation sections; not an authenticated CLI experiment.

## W-SKILLS - Agent Skills specification

Publisher: Agent Skills. Access date: 2026-10-28. Research round: 2.

Source: https://agentskills.io/specification

Finding: Progressive loading separates skill metadata, instructions and supporting resources. The published size recommendations are guidance, not a guarantee of reliable activation.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-EVALSKILLS - Testing Agent Skills Systematically with Evals

Publisher: OpenAI. Access date: 2026-10-28. Research round: 2.

Source: https://developers.openai.com/blog/eval-skills

Finding: Skill quality needs repeatable outcome and behavior evaluations, rather than judging a plausible instruction file or one successful demonstration.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CONTEXT - Effective context engineering for AI agents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://www.anthropic.com/research/effective-context-engineering-for-ai-agents

Finding: Context selection and on-demand retrieval are engineering decisions; persistent notes and compacted context serve different needs from complete conversation history.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-COST - Optimizing for cost and intelligence

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence

Finding: Reported delegation and effort experiments trade cost against accuracy; subagents were not a universal improvement over lower effort. Measurements depend on workload, model, cache and harness.

Reading scope: Cost/context/delegation sections and coding measurement footnote inspected, including sample, hidden-test grading and paired intervals. Results are vendor-specific, not measured for this repository. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-HARNESS - Effective harnesses for long-running agents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents

Finding: Incremental work, externally checked feature completion and durable progress artifacts address failures of one-shot long-running agents.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-SIMPLE - Building effective agents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://www.anthropic.com/research/building-effective-agents

Finding: Simple composable workflows can outperform unnecessary orchestration overhead. The article itself notes that its 2024 tooling landscape has changed.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-DOCX - Document objects, python-docx 1.2.0

Publisher: python-docx maintainers. Access date: 2026-10-28. Research round: 2.

Source: https://python-docx.readthedocs.io/en/latest/api/document.html

Finding: Document-order iteration yields paragraphs and tables; top-level collections do not by themselves traverse nested table content. Extraction must account for document structure.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-LITM - Lost in the Middle: How Language Models Use Long Contexts

Publisher: Liu et al. / TACL and arXiv. Access date: 2026-10-28. Research round: 2.

Source: https://arxiv.org/abs/2307.03172

Finding: The evaluated models were sensitive to evidence position in long contexts; this is historical task/model-specific evidence, not a universal property of every current model.

Reading scope: Paper abstract and publication metadata inspected; no reproduction and no claim to have read every experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-RETRIEVAL - Retrieval Quality at Context Limit

Publisher: Google Research / Max McKinnon. Access date: 2026-10-28. Research round: 2.

Source: https://research.google/pubs/retrieval-quality-at-context-limit/

Finding: The abstract reports position-robust simple fact retrieval for Gemini 2.5 Flash, limiting blanket extrapolation of older lost-in-the-middle findings.

Reading scope: Official publication abstract inspected; the result concerns simple factoid retrieval, not multi-file implementation correctness. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-PERSISTENCE - Persistence

Publisher: LangChain. Access date: 2026-10-28. Research round: 2.

Source: https://docs.langchain.com/oss/python/langgraph/persistence

Finding: Thread checkpoints and cross-thread stores have distinct lifetimes and purposes. Persistence does not itself establish application-level correctness.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-REPLAY - Graph API: re-execution and idempotency

Publisher: LangChain. Access date: 2026-10-28. Research round: 2.

Source: https://docs.langchain.com/oss/python/langgraph/graph-api

Finding: Resumed nodes can execute again; side effects and task ordering need explicit idempotency and replay contracts.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-ATOMIC - os.replace and filesystem interfaces

Publisher: Python Software Foundation. Access date: 2026-10-28. Research round: 2.

Source: https://docs.python.org/3/library/os.html

Finding: A successful same-filesystem replacement has atomic rename semantics; this is not a transaction covering multiple files or a promise of durable persistence after power loss.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CAS - Kubernetes API Concepts: updates

Publisher: Kubernetes. Access date: 2026-10-28. Research round: 2.

Source: https://kubernetes.io/docs/reference/using-api/api-concepts/

Finding: Conditional updates with the observed resourceVersion reject stale writers with a conflict. This is a transferable concurrency pattern, not a requirement to introduce Kubernetes.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-BOOK - AI Engineering supporting resources

Publisher: Chip Huyen. Access date: 2026-10-28. Research round: 2.

Source: https://github.com/chiphuyen/aie-book

Finding: The author repository indexes evaluation, agents and inference optimization resources for the book. It is not the full book.

Reading scope: Author-maintained book description and supporting-material index inspected; no claim of reading the paid book. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-ROUTELLM - RouteLLM: Learning to Route LLMs with Preference Data

Publisher: Ong et al. / ICLR. Access date: 2026-10-28. Research round: 2.

Source: https://arxiv.org/abs/2406.18665

Finding: Preference-trained routers trade model cost against benchmark quality; their evidence does not directly validate retry escalation in a stateful coding workflow.

Reading scope: Research abstract and version metadata inspected; benchmark percentages are not transferred to this codebase. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AUTOMIX - AutoMix: Automatically Mixing Language Models

Publisher: Aggarwal et al. / NeurIPS. Access date: 2026-10-28. Research round: 2.

Source: https://arxiv.org/abs/2310.12963

Finding: AutoMix combines noisy self-verification with a meta-verifier for model selection. Self-confidence alone is not treated as reliable acceptance.

Reading scope: Abstract and author implementation overview inspected; no full-paper experiment reproduction. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-FRUGAL - FrugalGPT

Publisher: Chen, Zaharia and Zou. Access date: 2026-10-28. Research round: 2.

Source: https://arxiv.org/abs/2305.05176

Finding: Learned cascades, prompt adaptation and model approximation can reduce task-specific API cost; their reported maximum savings are not a forecast for this skill.

Reading scope: Research abstract inspected, not a complete paper or paid model benchmark. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-RETRY - Timeouts, retries, and backoff with jitter

Publisher: Amazon Builders Library. Access date: 2026-10-28. Research round: 2.

Source: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/

Finding: Retries can amplify load and repeat side effects; timeout, backoff and jitter require explicit limits and idempotency boundaries.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-OPENAI-CACHE - Prompt caching

Publisher: OpenAI. Access date: 2026-10-28. Research round: 2.

Source: https://developers.openai.com/api/docs/guides/prompt-caching

Finding: The current guide distinguishes model generations and charges cache writes on GPT-5.6 and later; explicit stable-prefix breakpoints and retention have separate economics. A historical no-write-charge assumption is not portable.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CLAUDE-CACHE - Prompt caching

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching

Finding: Cache lifetimes, writes, reads and invalidation depend on API configuration. Managed CLI/subscription accounting must not be inferred from API list pricing.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-LITELLM - Reliability and fallbacks

Publisher: LiteLLM. Access date: 2026-10-28. Research round: 2.

Source: https://docs.litellm.ai/docs/proxy/reliability

Finding: Gateway retries and fallback chains are distinct mechanisms. A stateful coding runner must also account for side effects and the actual selected provider, beyond resending an API request.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-RETRY-LAYERS - Router retries and SDK retries

Publisher: LiteLLM. Access date: 2026-10-28. Research round: 2.

Source: https://docs.litellm.ai/docs/routing

Finding: Router-level retry limits and provider-SDK retries are different layers; nested retry policies can multiply attempts and latency.

Reading scope: Relevant retry/cooldown documentation excerpts inspected; no proxy deployment or authenticated test. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-OPENROUTER - Provider routing

Publisher: OpenRouter. Access date: 2026-10-28. Research round: 2.

Source: https://openrouter.ai/docs/guides/routing/provider-selection

Finding: Provider routing supports ordered fallback and compatibility/data-policy filters. Cost selection must not silently relax required parameters or privacy constraints.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CLAUDE-CLI - CLI reference

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://code.claude.com/docs/en/cli-reference

Finding: Headless output, session persistence and per-invocation budgets have explicit versioned contracts; structured JSON is still subject to independent validation.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CLAUDE-SUBAGENTS - Create custom subagents

Publisher: Anthropic. Access date: 2026-10-28. Research round: 2.

Source: https://code.claude.com/docs/en/sub-agents

Finding: Subagents have selectable context, tools and effort. Worktree isolation and forked conversation context are different choices; a fresh worktree may start from the default branch rather than the parent HEAD.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CODEX-EXEC - Non-interactive mode

Publisher: OpenAI. Access date: 2026-10-28. Research round: 2.

Source: https://learn.chatgpt.com/docs/non-interactive-mode

Finding: Codex exec exposes JSONL events, an output schema and ephemeral sessions. Event output and final structured results require distinct parsing and bounded storage.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-CODEX-SECURITY - Security

Publisher: OpenAI. Access date: 2026-10-28. Research round: 2.

Source: https://learn.chatgpt.com/docs/security

Finding: Approval policy and sandbox boundaries are distinct. A non-interactive invocation must fail rather than silently broaden permissions when its required boundary is unavailable.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-EFFORT - Effort command

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://antigravity.google/docs/cli/commands/effort

Finding: Effort availability is model-variant dependent, including conditional xhigh/max. The headless effort query is read-only; the invocation flag differs from a persistent interactive default.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-MODELS - Choose a model

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://antigravity.google/docs/models

Finding: The public model selector includes Gemini 3.8 Flash and Claude variants. A model listing does not prove an account entitlement, independent quota, maximum native effort or workload superiority.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-CREDITS - CLI AI credits

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://antigravity.google/docs/cli/credits/

Finding: The CLI exposes remaining AI credits and quota indicators; eligibility and quota decisions require account-scoped observations, not a static provider-wide constant.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-USAGE - Usage command

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://antigravity.google/docs/cli/commands/usage

Finding: Usage inspection reports model quota information. The runner can use observed quota scopes but must preserve unknown values and distinguish model quotas from credit pools.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-PERMISSIONS - Permissions

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://antigravity.google/docs/permissions/

Finding: Workspace write access is allowed under ordinary defaults; a sandbox flag alone is not proof of read-only advisory execution. Permission behavior varies by preset and version.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-QWEN-HEADLESS - Headless mode

Publisher: QwenLM. Access date: 2026-10-28. Research round: 2.

Source: https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/

Finding: Headless output and budgets are documented; safe-mode disables customization rather than establishing a read-only security boundary. Native goals and sessions can add their own control loops.

Reading scope: Official headless guide sections on flags, safe-mode, JSON and budgets inspected. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-QWEN-SETTINGS - Qwen Code settings

Publisher: QwenLM. Access date: 2026-10-28. Research round: 2.

Source: https://github.com/QwenLM/qwen-code/blob/main/docs/users/configuration/settings.md

Finding: The documented unattended retry opt-in can retry throttling/capacity failures indefinitely. The orchestrator must bound or disable this separate retry layer.

Reading scope: Official source documentation excerpts on wall-time, retry and environment controls inspected. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-KIMI-CLI - Kimi command reference

Publisher: Moonshot AI. Access date: 2026-10-28. Research round: 2.

Source: https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command

Finding: Current prompt-mode permission semantics differ from older combinations: prompt cannot be combined with auto, plan or yolo, and defaults to auto. Version-aware capability checks must prevent an implicit permission expansion.

Reading scope: Official command reference sections on prompt, permissions, session and output inspected; no local Kimi executable tested. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-TRAE-README - TRAE Agent README

Publisher: ByteDance. Access date: 2026-10-28. Research round: 2.

Source: https://github.com/bytedance/trae-agent

Finding: TRAE Agent is a separate configurable agent with explicit trajectory output and tool execution; its identity and data artifacts must not be confused with an IDE brand.

Reading scope: Official repository README examples and architecture description inspected. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-TRAE-TRAJECTORY - Trajectory recording

Publisher: ByteDance. Access date: 2026-10-28. Research round: 2.

Source: https://github.com/bytedance/trae-agent/blob/main/docs/TRAJECTORY_RECORDING.md

Finding: Trajectory recording includes agent/LLM/tool history and is diagnostic data, not a proof of validated task completion. Retention and secret handling must be explicit.

Reading scope: Trajectory guide sections and examples inspected; not a full repository audit. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-MUSE - Extending and automating Muse Code

Publisher: Meta. Access date: 2026-10-28. Research round: 2.

Source: https://dev.meta.ai/docs/muse-code/extending

Finding: Subagents share a checkout unless isolation is requested; accepted worktree isolation does not silently fall back. Cancellation is cooperative and retained events differ from a final acceptance result.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-MUSE-SESSIONS - Audit and resume agent sessions

Publisher: Meta. Access date: 2026-10-28. Research round: 2.

Source: https://dev.meta.ai/docs/cookbook/audit-agent-sessions

Finding: Session audit logs and child logs have their own persistence paths; exported session data is not portable cross-provider context by default.

Reading scope: Official cookbook excerpts on session logs, audit and resume inspected. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-GLM - Claude Code integration

Publisher: Z.ai. Access date: 2026-10-28. Research round: 2.

Source: https://docs.z.ai/devpack/tool/claude

Finding: Claude role aliases can all map to the same GLM backend. Alias names therefore cannot establish a capability escalation or independent quota identity.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-GLM-PLAN - GLM Coding Plan overview

Publisher: Z.ai. Access date: 2026-10-28. Research round: 2.

Source: https://docs.z.ai/devpack/overview

Finding: Coding-plan integrations and commercial eligibility are vendor-specific; API billing and subscription quotas should remain separate accounting dimensions.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-DEEPSEEK - Anthropic API compatibility

Publisher: DeepSeek. Access date: 2026-10-28. Research round: 2.

Source: https://api-docs.deepseek.com/guides/anthropic_api/

Finding: Claude-prefixed aliases can be accepted and mapped to DeepSeek backends. Compatibility has supported and ignored fields, so requested model labels and actual billed models must be distinguished.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-DEEPSEEK-MODELS - Model aliases and first API call

Publisher: DeepSeek. Access date: 2026-10-28. Research round: 2.

Source: https://api-docs.deepseek.com/quick_start/pricing

Finding: Legacy model aliases may remain accepted while serving a replacement backend. Successful dispatch alone does not prove the catalog identity or price remains unchanged.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-VISUAL-TESTS - Visual comparisons

Publisher: Microsoft Playwright. Access date: 2026-10-28. Research round: 2.

Source: https://playwright.dev/docs/test-snapshots

Finding: Screenshot comparisons need stable rendering baselines. A pixel comparison measures visual change, not semantic behavior or accessibility.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-ACCESSIBILITY - Evaluating Web Accessibility Overview

Publisher: W3C WAI. Access date: 2026-10-28. Research round: 2.

Source: https://www.w3.org/WAI/test-evaluate/

Finding: Accessibility evaluation combines methods throughout development; an automated check alone does not establish complete conformance.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-FRONTEND - Design2Code

Publisher: SALT-NLP authors / ACL. Access date: 2026-10-28. Research round: 2.

Source: https://aclanthology.org/2025.naacl-long.199/

Finding: Screenshot-to-code benchmarks measure a specific front-end task; these results cannot be used as a universal ranking for design, interactive behavior and accessible implementation.

Reading scope: Primary publication abstract and author benchmark description inspected, not every paper experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-SRE - Monitoring

Publisher: Google SRE Workbook. Access date: 2026-10-28. Research round: 2.

Source: https://sre.google/workbook/monitoring/

Finding: Monitoring needs useful signals and tested alert behavior. It should support operational decisions without promoting every observation to an alert or expensive diagnosis.

Reading scope: Public book chapter monitoring sections inspected; not a claim of reading the whole book. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-OVERLOAD - Handling overload

Publisher: Google SRE Book. Access date: 2026-10-28. Research round: 2.

Source: https://sre.google/sre-book/handling-overload/

Finding: Retry budgets and overload controls prevent recovery traffic from amplifying failures. The analogous runner policy needs a bounded combined retry budget.

Reading scope: Public chapter retry/load-control sections inspected; this is distributed-system evidence adapted to the runner. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-LOGGING - Logging Cheat Sheet

Publisher: OWASP. Access date: 2026-10-28. Research round: 2.

Source: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

Finding: Sensitive values and untrusted event text need protection, sanitization and controlled retention. A digest is not permission to delete original evidence.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-INJECTION - LLM Prompt Injection Prevention

Publisher: OWASP. Access date: 2026-10-28. Research round: 2.

Source: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

Finding: Untrusted retrieved data and tool outputs must not be treated as instructions. Structured separation and least privilege are defense layers, not a guarantee of immunity.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-WINDOWS-JOBS - Job Objects

Publisher: Microsoft. Access date: 2026-10-28. Research round: 2.

Source: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

Finding: Job Objects can contain and terminate process groups, with explicit breakaway and handle-lifetime behavior. Killing only a parent PID is not a portable tree-termination contract.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-SUBPROCESS - Subprocess management

Publisher: Python Software Foundation. Access date: 2026-10-28. Research round: 2.

Source: https://docs.python.org/3/library/subprocess.html

Finding: Unconsumed pipes can deadlock, communicate buffers output in memory, and timeout cleanup requires explicit process handling. Long-running output needs concurrent draining and bounded retention.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-COMPOSE - Control startup and shutdown order

Publisher: Docker. Access date: 2026-10-28. Research round: 2.

Source: https://docs.docker.com/compose/how-tos/startup-order/

Finding: Started is different from ready; dependency conditions and health checks can establish readiness before a dependent operation.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-OTEL - GenAI token metrics

Publisher: OpenTelemetry. Access date: 2026-10-28. Research round: 2.

Source: https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-token-metrics.md

Finding: GenAI telemetry distinguishes input, output and cache-write token measures. Schema evolution and billed-versus-consumed definitions must be versioned, not silently combined.

Reading scope: Official semantic-convention token metric definitions inspected; conventions are evolving and no SDK dependency is prescribed. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-BOOTSTRAP - Bootstrap confidence intervals

Publisher: SciPy. Access date: 2026-10-28. Research round: 2.

Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html

Finding: Paired resampling preserves the relationship between compared observations. The independent sampling unit must be defined before computing an interval.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-NPM - npm pack

Publisher: npm. Access date: 2026-10-28. Research round: 2.

Source: https://docs.npmjs.com/cli/v12/commands/npm-pack/

Finding: Pack dry-run and JSON output expose package contents; ignore-scripts and lifecycle execution have distinct behavior and must be stated in validation evidence.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-ACTIONS - Secure use of GitHub Actions

Publisher: GitHub. Access date: 2026-10-28. Research round: 2.

Source: https://docs.github.com/en/actions/reference/security/secure-use

Finding: Immutable action references and least-privilege workflow tokens reduce automation supply-chain exposure. Do not execute untrusted changes with publishing credentials.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-REFLEXION - Reflexion: Language Agents with Verbal Reinforcement Learning

Publisher: Shinn et al.. Access date: 2026-10-28. Research round: 2.

Source: https://arxiv.org/abs/2303.11366

Finding: Reflection can use external feedback and retained verbal information, but its reported gains do not make an unverified self-summary an acceptance oracle.

Reading scope: Original paper abstract inspected; no claim of reproduction or full-paper reading. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-PLANS - Plans and overages

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://www.antigravity.google/docs/plans

Finding: Baseline model quota, plan entitlement and optional paid overages are distinct. Exhausting baseline quota can activate credits only under the configured overage policy; availability does not imply free execution.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-ENTERPRISE - Claude Opus and Sonnet in Antigravity

Publisher: Google Cloud. Access date: 2026-10-28. Research round: 2.

Source: https://cloud.google.com/blog/products/ai-machine-learning/claude-opus-55-and-claude-sonnet-55-available-in-antigravity/

Finding: For the described enterprise setup, partner models use pay-as-you-go billing rather than pooled Gemini monthly tokens; first-party coordination can still consume first-party tokens. This does not establish identical accounting for individual plans.

Reading scope: Official rollout article billing/governance section inspected; enterprise scope explicitly retained. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-AGY-HEADLESS - Headless mode

Publisher: Google. Access date: 2026-10-28. Research round: 2.

Source: https://antigravity.google/docs/cli/headless/

Finding: The headless flag table lists low/medium/high while the dedicated effort page describes conditional xhigh/max; this documentation mismatch must be resolved with versioned CLI/model capability evidence.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-SELFCORRECT - Large Language Models Cannot Self-Correct Reasoning Yet

Publisher: Huang et al. / ICLR. Access date: 2026-10-28. Research round: 2.

Source: https://proceedings.iclr.cc/paper_files/paper/2024/hash/8b4add8b0aa8749d80a34ca5d941c355-Abstract-Conference.html

Finding: On the studied reasoning settings, intrinsic self-correction without external feedback can fail or degrade quality. This supports testing feedback quality, not a universal claim about all current models.

Reading scope: Conference abstract inspected; historical models/tasks, no full reproduction. Public source reading is not an independent code review or reproduction of vendor experiments.

## W-TAIL - tail invocation

Publisher: GNU Coreutils. Access date: 2026-10-28. Research round: 2.

Source: https://www.gnu.org/s/coreutils/manual/html_node/tail-invocation.html

Finding: Following a descriptor differs from following a pathname across rotation. An incremental reader must define identity, truncation and reopen behavior explicitly.

Reading scope: Relevant sections of the primary source inspected through web.run; no authenticated CLI or account experiment. Public source reading is not an independent code review or reproduction of vendor experiments.
