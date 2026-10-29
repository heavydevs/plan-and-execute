# Study

Implement the 32 twice-researched topic decisions and opt-in provider switching in one graph, with explicit compatibility, scoped writes, negative tests and independent acceptance reviews.

## Triage

- complexity: **complex** — Cross-provider dispatch, durable state, context safety and full-skill discovery require independent research and review boundaries.
- internal: **full_project** (user) — All32 reports were revised with competing approaches, scoped source evidence and counterexamples. Implementation and independent reviews remain pending.
- external: **broad** (user); required — The user requested a second broad review. Revision2 records63 newly inspected primary-source entries and preserves58 historical records with explicit reading limits.

## Questions

- **Q001** [high/resolved; I001] Does this request still produce a second plan? — No. Prepared research becomes input to one implementation plan with tests and code-review gates. -> Convert research tasks and repurpose all former second-plan deliverables.
- **Q002** [high/resolved; I002] Can research preparation count as product or independent-review completion? — No. Every implementation task remains pending and reviews need actual external execution evidence. -> Separate prepared report hashes from future validation and reviewer receipts.

## Repository evidence

- **I001** `docs/plans/20261028-skill-optimization/REQUEST_AMENDMENT.md` — The current user request replaces the two-plan workflow with one implementation graph. -> Use one implementation plan and preserve superseded source text in history.
- **I002** `docs/research/20261028-skill-optimization/prepared-research/INDEX.json` — All 32 research topics now have prepared reports; all implementation and independent review tasks remain pending. -> Bind each transformed TODO and checklist to its specific report.
- **I003** `skill/plan-and-execute/scripts/run_concise.py` — The production runner composes raw execution with artifact, model, runner and pattern contracts. -> Test the composed production entrypoint as well as pure helpers.
- **I004** `skill/plan-and-execute/scripts/availability.py:116-168` — Declared-chain escalation and escalated-tier availability can select different providers in the baseline. -> Implement coherent dispatch with opt-in compatibility and explicit acceptance.

## External evidence

- **E201** Anthropic, Optimizing for cost and intelligence (Retrieved 2026-10-28; record W-COST) — Reported delegation and effort experiments trade cost against accuracy; subagents were not a universal improvement over lower effort. Measurements depend on workload, model, cache and harness. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence
- **E202** OpenAI, Prompt caching (Retrieved 2026-10-28; record W-OPENAI-CACHE) — The current guide distinguishes model generations and charges cache writes on GPT-5.6 and later; explicit stable-prefix breakpoints and retention have separate economics. A historical no-write-charge assumption is not portable. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://developers.openai.com/api/docs/guides/prompt-caching
- **E203** Google, Effort command (Retrieved 2026-10-28; record W-AGY-EFFORT) — Effort availability is model-variant dependent, including conditional xhigh/max. The headless effort query is read-only; the invocation flag differs from a persistent interactive default. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://antigravity.google/docs/cli/commands/effort
- **E204** Google Cloud, Claude Opus and Sonnet in Antigravity (Retrieved 2026-10-28; record W-AGY-ENTERPRISE) — For the described enterprise setup, partner models use pay-as-you-go billing rather than pooled Gemini monthly tokens; first-party coordination can still consume first-party tokens. This does not establish identical accounting for individual plans. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://cloud.google.com/blog/products/ai-machine-learning/claude-opus-55-and-claude-sonnet-55-available-in-antigravity/
- **E205** QwenLM, Headless mode (Retrieved 2026-10-28; record W-QWEN-HEADLESS) — Headless output and budgets are documented; safe-mode disables customization rather than establishing a read-only security boundary. Native goals and sessions can add their own control loops. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/
- **E206** Moonshot AI, Kimi command reference (Retrieved 2026-10-28; record W-KIMI-CLI) — Current prompt-mode permission semantics differ from older combinations: prompt cannot be combined with auto, plan or yolo, and defaults to auto. Version-aware capability checks must prevent an implicit permission expansion. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command
- **E207** SciPy, Bootstrap confidence intervals (Retrieved 2026-10-28; record W-BOOTSTRAP) — Paired resampling preserves the relationship between compared observations. The independent sampling unit must be defined before computing an interval. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
- **E208** Python Software Foundation, Subprocess management (Retrieved 2026-10-28; record W-SUBPROCESS) — Unconsumed pipes can deadlock, communicate buffers output in memory, and timeout cleanup requires explicit process handling. Long-running output needs concurrent draining and bounded retention. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://docs.python.org/3/library/subprocess.html
- **E209** Python Software Foundation, os.replace and filesystem interfaces (Retrieved 2026-10-28; record W-ATOMIC) — A successful same-filesystem replacement has atomic rename semantics; this is not a transaction covering multiple files or a promise of durable persistence after power loss. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://docs.python.org/3/library/os.html
- **E210** OWASP, LLM Prompt Injection Prevention (Retrieved 2026-10-28; record W-INJECTION) — Untrusted retrieved data and tool outputs must not be treated as instructions. Structured separation and least privilege are defense layers, not a guarantee of immunity. -> Apply the assigned revision2 decision, negative tests and version/account capability checks. · https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

## Constraints

- Preserve original request bytes in REQUEST_ORIGINAL.md and the historical snapshot; the current amendment supersedes the two-plan workflow.
- Use prepared reports as implementation inputs; never mark implementation complete because research exists.

## Derived requirements

- Implement the prepared research recommendations in this one plan; do not create another plan.
- Replace every research task and its internal checklist with implementation instructions linked to its prepared report.

## Risks

- No authenticated CLI or independent external reviewer was exercised during research.
- Current documentation can differ from installed versions; capability fixtures and bounded probes must reconcile a material mismatch.
- Offline route replay is not a measurement of real model quality, quota consumption or dollar savings.
- Prepared source hashes are baseline evidence; implementation deliberately changes them and must record the new validated state.

## Validation

- Keep historical receipt integrity separate from current source/command/map validation.
- Every changed implementation and correction gate needs actual acceptance evidence; prepared research never counts as a pass.

Stop: All32 topics have a concrete selected design, alternatives, primary sources, assigned write scope and negative tests. Material unknown account/version capabilities have explicit fail-closed checks.
Ready: **yes**

Review: `Current-session research synthesis; no independent external review` — internal_coverage_sufficient, external_decision_justified, source_quality_sufficient, findings_translated_to_plan, contradictions_resolved

- All113 code anchors were hash-checked against the preserved baseline; this is not an independent line-by-line audit.
- New material constraints were assigned to implementation owners; provider and Windows execution remain unverified.
