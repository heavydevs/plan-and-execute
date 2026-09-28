# Study

Implement inherited tier routing, resumable availability failover and safe bounded advisory diagnosis.

## Triage

- complexity: **complex** — Routing, persisted recovery, provider contracts and advisory permissions cross independent runtime boundaries.
- internal: **related_packages** (user) — Code inspection confirms quota events do not alter the provider candidate set.
- external: **broad** (user); required — The user explicitly requested wide research; current CLI security and coordination costs change architecture.

## Questions

- **Q001** [high/resolved; I001] Does quota fallback work without technical escalation? — The current wait path repeats the same provider; a separate bounded availability state is required. -> Keep availability outside functional failure counters and retain the logical rung.
- **Q002** [high/resolved; I001,E008,E010] Can an advisory role safely reuse the worker profile? — No. Coding profiles permit writes and sandbox defaults are not read-only. -> Use an independent fail-closed assistant profile, opt-in evidence and bounded budgets.

## Repository evidence

- **I001** `skill/plan-and-execute/scripts/run_isolated.py:candidate_providers,choose_route,execute_one_task` — Provider selection uses functional failures while availability failures only retry or abort. -> Add a separate durable availability path with equivalent-rung fallback.
- **I002** `skill/plan-and-execute/scripts/planctl.py:default_config,create_plan,fail_task` — Plan creation writes a full defaults snapshot and quota failures preserve semantic counters. -> Preserve legacy snapshots; make new plans explicit overlays.
- **I003** `tools/validate-skill.js and .ai-work/baseline/npm-check.log` — The unmodified entrypoint exceeds its existing fixed character budget. -> Improve instruction concision during final review without raising ceilings.

## External evidence

- **E001** Anthropic, Anthropic multi-agent research system (2025-06-13) — Parallel research benefits from bounded specialists, but the reported multi-agent system used roughly 15 times chat tokens. This is workload-specific, not a universal saving. -> Gate advice; keep one implementation owner; never promise measured savings. · https://www.anthropic.com/engineering/multi-agent-research-system
- **E002** Anthropic, Building effective agents (2024-12-19) — Simple routing and orchestrator-worker workflows are preferable to unnecessary autonomous coordination. Evaluation needs explicit success criteria. -> Retain deterministic validators and fail-class authority. · https://www.anthropic.com/engineering/building-effective-agents
- **E003** Anthropic, Effective context engineering (2025-09-29) — Context is a finite resource; task-scoped retrieval and compact handoffs reduce irrelevant context. -> Pass bounded failure evidence, not full logs, plans or conversations. · https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- **E004** OpenAI, Agents SDK multi-agent orchestration (retrieved 2026-09-28) — Code-driven orchestration offers explicit control; manager-tool and handoff patterns have different ownership semantics. -> Use advisory tools, not ownership transfer, for diagnosis. · https://openai.github.io/openai-agents-python/multi_agent/
- **E005** Paper authors, Towards a Science of Scaling Agent Systems (2025-12-09) — Controlled configurations show coordination benefits depend on task structure; sequential tasks can suffer overhead and error amplification. -> Do not introduce mandatory debate, voting or extra model calls. · https://arxiv.org/abs/2512.08296
- **E006** Paper authors, Scaling LLM-Driven Multi-Agent Systems (2026-07-30) — Architecture experiments favor selective feedback and summary-based communication; effectiveness depends on task and model capability. -> Use bounded opt-in assistance and explicit stopping conditions. · https://arxiv.org/abs/2607.27942
- **E007** Paper authors, Multi-Agent Coordination Adaptation (2026-05-25) — Budget-conditioned coordination can suppress redundant interactions in its experimental setting. -> Enforce call, evidence, time and repetition budgets; benchmark total cost per validated outcome. · https://arxiv.org/abs/2605.25746
- **E008** Anthropic, Claude CLI reference (retrieved 2026-09-28) — tools empty disables built-ins but not MCP; restricted mode and settings controls matter. auth status exits zero when logged in. -> Disable all model tools and customizations; distinguish installed from authenticated. · https://code.claude.com/docs/en/cli-reference
- **E009** OpenAI, Codex CLI reference (retrieved 2026-09-28) — codex login status checks credential presence without a generation request. Read-only is distinct from workspace-write. -> Use a bounded status probe; do not infer authentication from executable presence. · https://developers.openai.com/codex/cli/reference/
- **E010** Google, Antigravity sandbox (retrieved 2026-09-28) — The sandbox permits writes in its workspace. Sandbox enabled alone is not a read-only guarantee. -> Fail closed without a verified no-write execution boundary. · https://www.antigravity.google/docs/sandbox
- **E011** Google, Antigravity CLI permissions (retrieved 2026-09-28) — Permission controls and sandboxing are distinct from a tool-less advisory role. CLI versions and affordances differ. -> Never reuse skip-permissions coding profiles; probe capabilities and isolate evidence. · https://www.antigravity.google/docs/permissions?tab=cli

## Constraints

- Retain deterministic validators and single task ownership.
- Reserve assistant budgets before dispatch; fail closed on unsupported isolation.

## Derived requirements

- Persist bounded cooldown and resumable pause when all allowed providers are unavailable.
- Enforce a fail-closed no-write assistant boundary and keep failure classification authoritative.

## Risks

- Native provider/OS support varies and cannot be inferred from mocked success.

## Validation

- Test routing precedence, quota resume, bounded assistant failures and wizard cancellation.

Stop: Primary evidence resolves the architecture, safety boundary, bounded cost controls and independent task boundaries.
Ready: **yes**

Review: `host-managed review; independent worker unavailable` — internal_coverage_sufficient, external_decision_justified, source_quality_sufficient, findings_translated_to_plan, contradictions_resolved

- The selected primary sources justify gated assistance, not unconditional multi-agent savings.
- Actual provider and Windows behavior will be reported separately from deterministic tests.
