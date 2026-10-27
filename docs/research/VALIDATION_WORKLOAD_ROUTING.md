# Validation and workload routing research

Date: 2026-10-27. Baseline: 6bdbab5. Execution: host-managed; no provider CLI is installed.

## Repository findings

- Watcher starts from invocation and implements idle, health and process-tree supervision. Source: `skill/plan-and-execute/scripts/resource_watch.py`.
- Cooldowns currently key only by provider, conflating Gemini and Claude quotas on Antigravity. Source: `skill/plan-and-execute/scripts/availability.py`.
- Installer validates and owns exactly one skill today. Source: `lib/installer.js`.
- Baseline has 37 passing Node tests, one skip, then two WindowsPath-mocking errors in keepalivectl tests on Linux. Evidence: the development baseline log; summarized in the final verification record. This is not a newly introduced regression.

## Primary-source research

### E001 - Antigravity models

https://www.antigravity.google/docs/models/

Flash 3.8 and Claude Opus 5.5 are listed; availability varies by account.

### E002 - Antigravity quotas

https://antigravity.google/docs/models/

Consumer quota displays separate Gemini and Claude/GPT family buckets; enterprise billing differs.

### E003 - Antigravity headless

https://antigravity.google/docs/cli/headless/

Use exact discovered model IDs and explicit timeouts; headless sandbox alone is not read-only.

### E004 - Antigravity agents

https://www.antigravity.google/docs/subagents/

Custom primary agents expose explicit tools, MCP, skills and command policy controls.

### E005 - Claude subagents

https://code.claude.com/docs/en/sub-agents

Subagents separate context but share parent usage limits; tools and effort require explicit control.

### E006 - Claude CLI

https://code.claude.com/docs/en/cli-reference

Tools removal differs from autoapproval; bare tool-less execution can bound advisory calls.

### E007 - Codex subagents

https://developers.openai.com/codex/multi-agent

Inherited permissions mean read-only prose does not enforce a read-only subprocess.

### E008 - Codex skills

https://developers.openai.com/codex/skills

Progressive disclosure keeps skill metadata small and loads instructions only when needed.

### E009 - Qwen subagents

https://qwenlm.github.io/qwen-code-docs/en/users/features/sub-agents/

Agent tool allowlists and inherited permissions must be respected.

### E010 - Kimi agents

https://moonshotai.github.io/kimi-code/en/customization/agents.html

Exploration and implementation agents differ in tool permissions and context scope.

### E011 - Trae Agent

https://arxiv.org/abs/2507.23370

Repository-level task evaluation supports measured routing rather than universal model rankings.

### E012 - Monitoring distributed systems

https://sre.google/sre-book/monitoring-distributed-systems/

Actionable low-noise monitoring separates symptoms from diagnosis.

### E013 - RouteLLM

https://arxiv.org/abs/2406.18665

Cost-quality routing requires empirical validation on the target workload.

### E014 - Context engineering

https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

Bounded evidence and just-in-time retrieval reduce irrelevant context.

### E015 - Playwright visual checks

https://playwright.dev/docs/next/test-snapshots

Screenshot baselines require consistent environments and review, not blind updates.

## Decisions and uncertainty

Use deterministic supervision from invocation, not model polling. Anomaly advice is optional and cannot approve work, execute fixes, terminate arbitrary processes or delete evidence. Separate workload fit, logical floor, host model ID and quota pool. Antigravity Claude is capped at advanced by conservative policy; no empirical cross-host IQ equivalence is claimed. Flash 3.8 is available but no universal cheapest-price claim is made. Model IDs must come from the installed CLI/account. Enterprise and custom credentials may share different pools.

No measured token savings or live-provider success is claimed. Validate routing with deterministic fixtures and frontend work with screenshots, interactions and accessibility checks.

## Additional adapter and boundary checks

### E016 - Gemini CLI headless

https://geminicli.com/docs/cli/headless/

Official headless documentation remains available. Do not rely on an unsupported retirement-date claim to select an adapter. Retain the existing Gemini coding adapter for compatibility; it is not audited as a tool-less observer here.

### E017 - Antigravity startup hooks

https://antigravity.google/docs/hooks/

Global, workspace and plugin hooks can execute before model/tool initialization. The observer checks documented global startup metadata first, uses a fresh workspace, and refuses customized executable boundaries instead of altering the user's settings.

### E018 - Antigravity plugins

https://antigravity.google/docs/plugins/

Installed CLI/IDE plugins can extend tools and startup behavior. A verified empty tool list alone is not an OS sandbox; executable native CLI and authentication storage remain trusted. Unknown/nonempty customization directories cause a skip. Never describe request-review or a writable sandbox as read-only.

## Architecture and acceptance implications

The independent entrypoint is intentionally tiny. Python resource/progress modules are bundled mechanically into the companion with hashes, not reimplemented, and loaded as code rather than added to model context. DIRECT may create bounded validation receipts but never planning state. A task's optional workload is projected into its bounded definition so a resumed worker need not inspect a whole manifest to discover it.

Observation is deterministic and starts at invocation. A five-minute estimate prompts explicit progress instrumentation; it is not a delay before detecting failures. Increasing counters, output, process activity and mapped health carry different meanings. Genuine environmental failures and explicit time ceilings do not justify spending on a stronger model.

Optional diagnosis has a finite call/candidate/time budget, an evidence cursor and deduplication. An observer receives redacted bounded packets, cannot approve or repair, and cannot request deletion. The deterministic owner cleans only allowlisted artifacts after a passed result; source and external application logs are never cleanup targets.

Profile preference is workload-specific, not a global intelligence ranking. Frontend preferences require rendered, interaction and accessibility evidence. Intermediate Antigravity Claude preference is a user-requested conservative policy. Flash 3.8 availability is documented, but its price/credit advantage is account-dependent and no provider cost saving is measured here. Exact CLI IDs, authentication, quotas and local executable capabilities must be checked at deployment.
