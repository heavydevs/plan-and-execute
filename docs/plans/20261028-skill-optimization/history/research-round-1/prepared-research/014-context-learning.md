# F005 / task 014 - Assigned context, learned facts and token budgets

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Use bounded assigned context and directional, evidence-backed learnings; keep hypotheses separate from normative contracts.

## Questions addressed

- Compare global versus scoped context and validated directional learnings.
- Measure repeated prefixes, assigned-read enforcement and anchoring from prior errors.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- The current context system separates universal context, task-scoped context and directional learnings. The production worker prompt is built by runner_contract.
- Useful worktree changes and completed subtasks survive a worker; transcripts are not the intended cross-task memory.

### Read targets and integrity

- `skill/plan-and-execute/scripts/planctl.py` (SHA-256 `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4`): `render_task` L1784-1933
- `skill/plan-and-execute/scripts/artifact_contract.py` (SHA-256 `477646cf30634e334e5c704a6cbe86e9dea4712f7527f51501c43462cadc08f3`): `_error` L100-101; `concise_line` L104-129; `concise_list` L132-162; `_md` L165-167
- `skill/plan-and-execute/scripts/runner_contract.py` (SHA-256 `74db8be9153d63c8accc1e3a650279fd54da0ea0b6405b0bfb4e470f183a97c6`): `worker_prompt` L44-80
- `skill/plan-and-execute/references/EXECUTION_CONTEXT.md` (SHA-256 `4ed0e09d146e6a228943f9607de92a3156e19ca5c5e19b77bdd78ffa5de82447`): `# Execution context and validated learning` L1; `## Omission is the default` L5; `## Global `CONTEXT.md`` L18; `## Scoped context files` L36
- `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md` (SHA-256 `72da10bd5e05fd08d213ed29ca649e83fbe23d4f082bf1c3159e87402cbef8cd`): `# Token-efficiency contract` L1; `## Objective` L5; `## 1. Avoid the harness when the harness does not pay for itself` L9; `## 2. Keep useful shared context while it is useful` L15

## External basis

- [E003] [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) - Anthropic; accessed 2026-10-28.
- [E011] [Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models](https://arxiv.org/abs/2510.04618) - Zhang et al. / arXiv; accessed 2026-10-28.
- [E010] [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) - Shinn et al. / arXiv; accessed 2026-10-28.
- [E021] [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) - OpenAI; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Carry forward all conversation history | Maximal recall but repeated tokens and unrelated or misleading context. |
| recommended | Assigned evidence-backed memory with invalidation | Small useful state, explicit provenance and less anchoring risk. |
| rejected | Automatically turn every failure narrative into a global rule | Cheap writing creates unbounded stale context and can propagate an incorrect diagnosis. |

## Implementation instructions

1. Attach a provenance hash, producing task, applicable consumers and expiry/invalidation rule to each reusable learning.
2. Load only universal constraints and the receiving task's assigned entries. Repeated conventions used by multiple tasks belong in a versioned pattern, not copied learning prose.
3. Require deterministic evidence before promoting a failed worker's hypothesis into a reusable fact. Keep disproven hypotheses clearly labeled and bounded.
4. Add a compact context accounting receipt: selected file IDs, byte counts and reason for inclusion, without retaining prompts or secrets.
5. Keep static prompt rules stable across tasks; append task-specific evidence afterward. Test cache structure but measure actual cache usage per host rather than assuming an exact hit.

## Acceptance tests to implement and run

- [ ] An unrelated task cannot receive a learning merely because it ran later.
- [ ] Changing a cited file invalidates or flags the learning before reuse.
- [ ] A malicious or unsupported note cannot alter acceptance, permissions or provider policy.
- [ ] The universal context contains only constraints needed by all tasks and remains within its existing budget.
- [ ] Byte-stable prefixes and bounded task suffixes survive different task IDs and prior failure lengths.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Measure re-read source bytes, assignment size and acceptance regressions. Reuse is valuable only when it avoids rediscovery without lowering correctness; do not promise a universal token reduction.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Research on memory/context reports workload-specific gains, not proof for this repository. Independent implementation review remains necessary.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **014** now implements this recommendation; task **015** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
