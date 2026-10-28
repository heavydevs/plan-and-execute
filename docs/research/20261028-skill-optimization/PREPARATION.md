# Initial planning reconnaissance

Date: 2026-10-28. Source tree: `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

This is planning evidence, not the requested completed broad research, completed implementation or an independent maximum-model review.

## Verified local findings

- Restored 188 tracked source files from the 0.11.0 archive; their tree matches remote commit 193fefd. No runtime files were edited.
- `run_concise.py` installs artifact, routing, runner and pattern contracts. Production validation must exercise the patched entrypoint, not only raw helpers.
- `run_isolated.choose_route` (lines 301-346) selects from the declared chain; `availability.select` (lines 116-168) rebuilds the escalated-tier chain.
- `runner_contract.worker_prompt` calls `failure_context(task)` without `plan_dir`, leaving evidence-path forwarding as a distinct change boundary.
- `workload_routing.candidates` (lines 121-175) raises for an unconfigured tier on the legacy path. Fixture replay reproduces codex/advanced failure.
- The fixture replay covers default and source-equivalent chains with no authenticated calls and no reading of user-global configuration.

## Actual preliminary validation

- `npm ci --ignore-scripts --offline`: exit 0. This is not a claim to have run arbitrary install hooks.
- Mapped `ALL` / `npm run check`: inconclusive after the container command limit (200 seconds); logs end during Node tests, without the full-suite exit result.
- `routing_self_test.py`: passed, 28 cases. `model_routing_self_test.py`: passed. `workload_routing_self_test.py`: passed, 16 cases.
- Fresh service-map check passed before preparation. Semantic coverage of every old validation entry still belongs to the audit task.
- `claude`, `codex` and `agy`: not on PATH. No external reviewer, Windows validation or real-provider run was executed.

## Planning decisions (inference)

- Preserve a separate maximum-capability reviewer task per topic to make review resumable and observable, rather than a prose instruction hidden in a cheaper task.
- Research can compare alternatives independently, while provider-switch implementation follows reviewed contract/state/handoff/integration boundaries.
- Keep durable research under docs so Plan 1 cleanup cannot erase Plan 2 inputs.
- Book overview and search-discovered pages are leads, not evidence that full texts have been read.

## Numbered initial sources

### E001 - Effective harnesses for long-running agents
Publisher: Anthropic. Version/access: 2025-11-26; accessed 2026-10-28.
URL: https://www.anthropic.com/research/effective-harnesses-for-long-running-agents
Scope: selected_official_page_or_paper_abstract.
Finding: Incremental tasks and durable progress artifacts address loss of context; the article does not prove this skill is complete.
Planning impact (inference): Separate audit, feature evidence and final-plan synthesis; preserve unfinished work.

### E002 - Claude Code CLI reference
Publisher: Anthropic. Version/access: Live documentation accessed 2026-10-28.
URL: https://code.claude.com/docs/en/cli-reference
Scope: selected_official_page_or_paper_abstract.
Finding: Print mode and session controls have distinct contracts; nonpersistent execution cannot be assumed resumable.
Planning impact (inference): Compare a worker-provided summary and deterministic fallback before choosing native-session persistence.

### E003 - Codex non-interactive mode
Publisher: OpenAI. Version/access: Redirects to learn.chatgpt.com; accessed 2026-10-28.
URL: https://developers.openai.com/codex/noninteractive/
Scope: selected_official_page_or_paper_abstract.
Finding: The documentation distinguishes ephemeral execution, structured output and explicit sandbox settings.
Planning impact (inference): Test adapter flags and schema against the installed CLI version; do not assume existing argv is current.

### E004 - Antigravity CLI commands
Publisher: Google. Version/access: Live documentation accessed 2026-10-28.
URL: https://antigravity.google/docs/cli/reference/
Scope: selected_official_page_or_paper_abstract.
Finding: Effort is model-dependent; --continue and --conversation are documented session controls.
Planning impact (inference): Resolve effective effort from both CLI and model list; preserve divergence as an explicit test input.

### E005 - Antigravity model quotas
Publisher: Google. Version/access: Live documentation accessed 2026-10-28.
URL: https://antigravity.google/docs/cli/commands/usage
Scope: selected_official_page_or_paper_abstract.
Finding: The CLI exposes usage/quota inspection; this alone does not prove a selected account has a particular available quota.
Planning impact (inference): Plan per-profile and model-family checks without spending authenticated quota during preparation.

### E006 - Handoffs - OpenAI Agents SDK
Publisher: OpenAI. Version/access: Live documentation accessed 2026-10-28.
URL: https://openai.github.io/openai-agents-python/handoffs/
Scope: selected_official_page_or_paper_abstract.
Finding: Structured handoff inputs and input filters are explicit SDK mechanisms.
Planning impact (inference): Use their separation of metadata and history as an alternative, not proof of cross-CLI session portability.

### E007 - AutoMix: Automatically Mixing Language Models
Publisher: NeurIPS / paper authors. Version/access: NeurIPS 2024; abstract accessed 2026-10-28.
URL: https://papers.nips.cc/paper_files/paper/2024/hash/ecda225cb187b40ea8edc1f46b03ffda-Abstract-Conference.html
Scope: selected_official_page_or_paper_abstract.
Finding: The abstract reports model routing with noisy self-verification and cost/quality experiments.
Planning impact (inference): Compare against measured skill baselines; do not import the paper savings percentage into project claims.

### E008 - AI Engineering book overview
Publisher: Chip Huyen. Version/access: OReilly 2025; author overview accessed 2026-10-28.
URL: https://huyenchip.com/books/
Scope: metadata_only.
Finding: The author describes coverage of foundation-model applications, evaluation and deployment. Full book text was not consulted.
Planning impact (inference): Research tasks must obtain accessible author excerpts or an authorized book copy and state reading scope.

### E009 - Qwen Code headless mode
Publisher: QwenLM. Version/access: Search-discovered on 2026-10-28; full reading pending.
URL: https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/
Scope: metadata_only.
Finding: Official source located for the Qwen-specific research task.
Planning impact (inference): Verify pinned headless flags, permission behavior and structured output in that task.

### E010 - Kimi command reference
Publisher: Moonshot AI. Version/access: Search-discovered on 2026-10-28; full reading pending.
URL: https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command
Scope: metadata_only.
Finding: Official source located for the Kimi-specific research task.
Planning impact (inference): Verify session, print and interruption semantics before proposing adapter changes.

### E011 - Trae Agent repository
Publisher: ByteDance. Version/access: Search-discovered on 2026-10-28; code review pending.
URL: https://github.com/bytedance/trae-agent
Scope: metadata_only.
Finding: Official source located for the Trae Agent-specific research task.
Planning impact (inference): Disambiguate this repository from TRAE IDE and other CLI products.

### E012 - Muse Code documentation
Publisher: Meta. Version/access: Search-discovered on 2026-10-28; full reading pending.
URL: https://dev.meta.ai/docs/muse-code
Scope: metadata_only.
Finding: Meta documentation located; unrelated muse-cli products must not be substituted.
Planning impact (inference): Pin exact adapter identity and version before session or summary changes.

