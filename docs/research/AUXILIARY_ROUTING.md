# Auxiliary model collaboration: research and design decisions

Reviewed 2026-09-28 against repository base `da785e567f5f3c6640f1ba3e0caf39900e4b0310`.

## Decision

The demand is justified: the existing runner records quota events without rotating the selected provider. An advisory role is useful only when deterministic failure evidence is insufficient. Availability fallback is a reliability mechanism; advisory diagnosis is a cost-bearing optimization. They must remain independent.

## Evidence and bounded conclusions

### E001 - Anthropic multi-agent research system

Source: https://www.anthropic.com/engineering/multi-agent-research-system (2025-06-13).

Parallel research benefits from bounded specialists, but the reported multi-agent system used roughly 15 times chat tokens. This is workload-specific, not a universal saving.

Implementation implication: Gate advice; keep one implementation owner; never promise measured savings.

### E002 - Building effective agents

Source: https://www.anthropic.com/engineering/building-effective-agents (2024-12-19).

Simple routing and orchestrator-worker workflows are preferable to unnecessary autonomous coordination. Evaluation needs explicit success criteria.

Implementation implication: Retain deterministic validators and fail-class authority.

### E003 - Effective context engineering

Source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (2025-09-29).

Context is a finite resource; task-scoped retrieval and compact handoffs reduce irrelevant context.

Implementation implication: Pass bounded failure evidence, not full logs, plans or conversations.

### E004 - Agents SDK multi-agent orchestration

Source: https://openai.github.io/openai-agents-python/multi_agent/ (retrieved 2026-09-28).

Code-driven orchestration offers explicit control; manager-tool and handoff patterns have different ownership semantics.

Implementation implication: Use advisory tools, not ownership transfer, for diagnosis.

### E005 - Towards a Science of Scaling Agent Systems

Source: https://arxiv.org/abs/2512.08296 (2025-12-09).

Controlled configurations show coordination benefits depend on task structure; sequential tasks can suffer overhead and error amplification.

Implementation implication: Do not introduce mandatory debate, voting or extra model calls.

### E006 - Scaling LLM-Driven Multi-Agent Systems

Source: https://arxiv.org/abs/2607.27942 (2026-07-30).

Architecture experiments favor selective feedback and summary-based communication; effectiveness depends on task and model capability.

Implementation implication: Use bounded opt-in assistance and explicit stopping conditions.

### E007 - Multi-Agent Coordination Adaptation

Source: https://arxiv.org/abs/2605.25746 (2026-05-25).

Budget-conditioned coordination can suppress redundant interactions in its experimental setting.

Implementation implication: Enforce call, evidence, time and repetition budgets; benchmark total cost per validated outcome.

### E008 - Claude CLI reference

Source: https://code.claude.com/docs/en/cli-reference (retrieved 2026-09-28).

tools empty disables built-ins but not MCP; restricted mode and settings controls matter. auth status exits zero when logged in.

Implementation implication: Disable all model tools and customizations; distinguish installed from authenticated.

### E009 - Codex CLI reference

Source: https://developers.openai.com/codex/cli/reference/ (retrieved 2026-09-28).

codex login status checks credential presence without a generation request. Read-only is distinct from workspace-write.

Implementation implication: Use a bounded status probe; do not infer authentication from executable presence.

### E010 - Antigravity sandbox

Source: https://www.antigravity.google/docs/sandbox (retrieved 2026-09-28).

The sandbox permits writes in its workspace. Sandbox enabled alone is not a read-only guarantee.

Implementation implication: Fail closed without a verified no-write execution boundary.

### E011 - Antigravity CLI permissions

Source: https://www.antigravity.google/docs/permissions?tab=cli (retrieved 2026-09-28).

Permission controls and sandboxing are distinct from a tool-less advisory role. CLI versions and affordances differ.

Implementation implication: Never reuse skip-permissions coding profiles; probe capabilities and isolate evidence.

## Security and economic refinements

- Treat logs as untrusted and potentially confidential. Explicit opt-in authorizes sending only redacted, bounded evidence to the configured provider; redaction is best effort, not a universal secret detector.
- A fresh directory is not a sandbox. A sandbox that permits workspace writes is not read-only. Assistant launch must have a verifiable, fail-closed capability boundary independent of coding-worker flags, hooks, MCP and extensions.
- Authentication is separate from executable discovery. Use non-generative status checks and explicit verified configuration for CLIs without a documented status command. Do not inspect credential contents.
- Reserve an advisory attempt before dispatch. Malformed output, timeout and interruption still consume the bounded call budget. Reuse evidence-identical advice and prevent recursive assistants.
- Never derive authoritative failure classes or shell commands from advice. Record the deterministic decision separately, even when it disagrees with the suggestion.
- Preserve the logical tier and effort during availability failover. Record capability caps separately. Exhausting a chain pauses; it does not count as a semantic failure or silently upgrade cost.
- Configuration precedence is defaults < user-global < explicit per-plan overrides. Legacy full snapshots remain explicit; new plans should inherit through a small overlay rather than silently freezing defaults.
- No universal token or accuracy improvement is claimed. Evaluate cost per validated completion, repeated-failure recovery, latency, calls and safety; char/byte budgets are proxies, not billed token counters. Real-provider comparative evaluation remains separate from deterministic/mock tests.

## Evaluation matrix

Availability: primary quota then fallback success; unavailable design worker; same logical rung across unequal provider ladders; all providers exhausted; explicit pinned provider; no semantic counter changes; resume/cooldown; cancellation; genuine failure escalation.

Configuration: global inheritance; nested per-plan overrides; legacy snapshots; malformed JSON/types/duplicate chains; effort-embedded models; no installed or authenticated CLI; ordered numbered questions; cancellation and atomic writes.

Advice: default off; deterministic lint skipped; gated repetition/stall/unhealthy evidence; bounded and redacted input; no tools or write authority; malformed/oversized/untrusted output; unsupported provider fails closed; timeout and interruption budget persistence; duplicate evidence; authoritative class unchanged; next-worker capsule stays bounded.

## Baseline and execution provenance

`npm run check` fails on the unmodified base because SKILL.md exceeds its existing 7,000-character budget (7,727 characters). Fix concision rather than increasing budgets. No Codex/Claude CLI or independent model worker is installed here; plan-and-execute runs in its documented host-managed mode. Native provider and Windows behavior cannot be inferred from mocks.

## Native-profile verification and deliberate scope refinement

### E012 - Claude bare/headless execution

Source: https://code.claude.com/docs/en/headless (reviewed 2026-09-28).

Bare mode removes automatic project configuration, hooks/plugins/skills and credential-file discovery; built-in tools must still be disabled separately. It requires an explicitly supplied API key and is not subscription OAuth. Structured output is returned in the `structured_output` envelope.

Implementation: separate trusted-native Claude adapter; private working directory and environment; `--bare`, no built-ins, strict empty MCP, disabled slash commands, one turn, no persisted session. The wizard/documentation warn about API billing. No real key was used in implementation tests.

### E013 - Antigravity headless execution

Source: https://antigravity.google/docs/cli/headless/ (reviewed 2026-09-28).

Headless execution still grants workspace writes; a sandbox/fresh folder does not make it tool-less. The inspected interface did not establish an equivalent per-run bare/no-tool boundary.

Implementation: retain selectable provider preference and coding support, but skip native advisory calls for this and other unverified profiles. Do not silently reuse coding flags or pretend read-only isolation exists. This is a documented limitation, not verified multi-provider advisory execution.

## Comparative quality/cost protocol (not yet executed)

Use a fixed, versioned corpus of representative repository tasks and failure fixtures: straightforward syntax errors, ambiguous repeated failures, genuine service outages, confirmed stalls, quota interruption and failures where a wrong diagnosis would silently corrupt the result. Keep task inputs, acceptance tests, model IDs, effort, provider versions, retry limits and context constant across matched conditions. Separate provider-availability recovery from diagnostic value.

Compare: (A) deterministic baseline with assistance disabled; (B) identical workflow with gated one-call assistance; optionally (C) a predeclared different supported assistant. Randomize matched run order and repeat enough independent tasks/runs to report uncertainty rather than cherry-pick successful cases. Native providers must first pass security/capability and credential/billing checks.

The primary quality gate is externally validated completion, including regressions and independently checked high-impact invariants. Record false diagnoses, unnecessary changes, safety violations and resumability. Measure total input/output/billed tokens, billed cost per validated completion, wall time, failed calls and repeated validator runs. Include the assistant's bill and any retry/coordination overhead. Character counts in the implementation are resource limits, not substitutes for these measurements.

Keep assistance off unless the measured tradeoff meets a predeclared quality non-inferiority margin and a useful cost/recovery objective. Report sample sizes, confidence intervals and unsuccessful runs. No numerical quality or economy improvement is asserted by this patch; offline tests validate mechanisms, not real-model performance.
