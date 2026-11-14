# P056 — Security and performance review of task architecture and code

**Prepared 2026-11-14; planning specification only.** No real implementation, dispatched reviewer, application benchmark or demonstrated token savings. Public book/publisher previews and contents were consulted; no complete-book reading is claimed.

## Current source and integration points

- `run_isolated.py` (`design_prompt`, `run_design_phase`, `needs_design_phase`) currently accepts a nonempty design note plus a completed worker report, with no separate security or performance architecture review. `worker_prompt` has an existing isolated dispatch contract.
- `planctl.py` validates `design_route`, stores `design_phase` and resets it; use the existing native controller for optional review state and hash invalidation, preserving schema 1–4 and prior task state.
- `artifact_contract.py` renders compact tasks. Existing code-review TODOs (088, 100, 106, etc.) already demand an actual fresh independent reviewer. Add two review lenses inside that existing call, rather than dispatching two more agents on every task.
- `PLANNING_PROTOCOL.md`, `WORKFLOW.md`, `PLAN_SPEC.md`, `DELEGATION.md`, `MODEL_ROUTING.md` contain complexity, worker isolation, qualified routing and cost constraints. Planned DIRECT architecture delegation 087/088 must share the policy without converting DIRECT work into a full plan.

## Alternatives considered

| Design | Upside | Downside | Decision |
|---|---|---|---|
| Extra security and performance model each on every task | Distinct specialist viewpoints | Higher latency/tokens, repeated context, false positives on mechanical edits | Reject default |
| Only linters/tests/scanners | Cheap and deterministic | Misses architecture tradeoffs, trust boundaries and scaling hazards | Insufficient alone |
| Full ATAM/STRIDE ritual on all edits | Broad formalism | Excessive for task-scoped changes | Reject |
| Independent, risk-gated design review + security/performance in existing final review | Earlier mitigation, bounded model calls, preserves correct process | Requires durable gated state and hash validity | **Chosen** |

## Implementation architecture and precise acceptance contract

1. **Admit design review only when design matters.** Planner classifies `no_design` versus `material_design` from actual security/performance/system-boundary risk, not file count. Every formal `design_route` is material. A substantive auth/data-flow, distributed coordination, concurrency, storage/cache, resource or trust-boundary decision must have a compact design note even when DIRECT. Tiny mechanical work is not forced to open another model context.
2. **Architect note.** Extend existing note (bounded to current size limits) with architectural alternatives and tradeoffs, concise security scenario (asset, entrypoint, trust boundary, attacker/misuse case, mitigation/residual risk) and performance scenario (expected data/workload, hot path, asymptotic/IO/memory/lock/caching/fanout effects, model-call cost, backpressure/retry). Distinguish known measurements from assumptions. Reuse source paths and symbols, no full transcripts.
3. **Pre-implementation independent gate.** After design worker writes note, dispatch a *different* qualified fresh **read-only** reviewer using existing provider/permission/workload routing. Reviewer assesses applicable OWASP-style threats and ATAM-style security/performance tradeoffs, plausible alternative and testability. Required result: verdict `approved | changes_required | blocked`, separate `security` and `performance` findings or justified `not_applicable`, severity/file/line or symbol/risk/mitigation, actual provider/model/effort/session/dispatch provenance, design-note hash and relevant assigned source/task/contract fingerprint.
4. **Fail closed and resume safe.** Never dispatch implementation before a valid approved review. Missing/unavailable unauthorized reviewer, unresolved critical/high findings, malformed provenance, stale changed note/contract/source, cancellation/restart or failed hash verification blocks and requires bounded re-review; no silent bypass, fabricated model, unrelated source writes or unbounded retries. A reviewer cannot modify code or authoritative task/route status.
5. **Final code review, no extra routine agents.** Existing independent review TODO examines actual diff plus impacted callers, design mitigations, correctness and ordinary validation. Add separate *security* (authorization, secrets, input, injection, subprocess/path/TOCTOU, data protection, race) and *performance* (hot paths, N+1, allocation/IO/network/model calls, caching, blocking, contention, resource limits and retry) judgments. Each lens lists actionable severity/evidence/file:line plus recommendation/disposition, or a short grounded clean/N/A rationale. High/critical issues block acceptance and need correction/re-review on final hashes. Unmeasured impact remains unknown, never an invented speedup.
6. **Use cheapest qualified route and bounded context.** Review only formal material architecture beforehand; existing code review is one model call with two lenses. No second orchestrator, no observer-as-reviewer, no policy/paid-provider bypass. Optional extra specialist only for a concrete unresolved high-risk gap and within authorization. Track actual additional review cost and quality per accepted task, not speculative savings.
7. **Performance test exception is mandatory.** Do **not** generate or require automated application performance/load/stress/benchmark tests unless explicitly requested by the user for that task. Static reasoning and existing functional evidence suffice for review; future measurement may be proposed, not silently executed. **Do** create functional tests of this review *mechanism* and its negative cases.
8. **Functional regression matrix.** Include no-design small edit (no extra call), material design pre-gate, security/performance N/A justification, reviewer independence, fake/unavailable reviewer, high/critical block, stale hashes after note/source mutation, crash/resume, bounded re-review, final diff re-review, DIRECT, legacy schemas 1–4, provider restrictions, read-only limitations and no implicit performance benchmarks. Document real test commands, receipts, hashes, limitations.

## Task split, order, and outputs

- **107 implementation:** read this study and relevant current code; implement conditional design review state+dispatch in existing `run_isolated.py`/`planctl.py`; document planning admission and quality scenarios; add two lenses to existing code-review prompts/contract and native receipts; integrate DIRECT 087/088; write `test/optimization/architecture_security_performance_review_self_test.py`; wire mapped validation; record actual `107-receipt.json` and outcome.
- **108 independent review/correction:** actual qualified fresh max reviewer checks 107 source/tests/receipts/final hashes, independent pre-design review, code-review lenses, stale state, false positive restraint, permissions, provider cost, optional performance-test rule and backward compatibility; correct high/critical defects and retest; record actual reviewer identity/provenance in 108 receipt.
- **Dependencies:** 013,029,049,088,092,098,100,104,106 -> 107 -> 108 -> 082 integration -> 083/084/085/086 final review. 086 stays last and all tasks pending. No current reviewer or benchmark evidence exists.

## Sources (public material and official documentation)

| Material | URL | Reading scope |
|---|---|---|
| SEI/CMU ATAM | https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/ | Tradeoffs between architectural quality attributes |
| Software Architecture in Practice, Bass/Clements/Kazman, 4th ed. | https://www.pearson.com/en-us/pearsonplus/p/9780137468218.html | Publisher overview/contents, not full book |
| Designing Data-Intensive Applications, Kleppmann/Riccomini, 2nd ed. | https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/ch02.html | Publisher public excerpt on scale and latency, not full book |
| OWASP Threat Modeling Cheat Sheet | https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html | Trust boundaries, STRIDE and abuse scenarios |
| OWASP ASVS | https://asvs.owasp.org/ | Web-service security checks where applicable |
| NIST SSDF SP 800-218 | https://csrc.nist.gov/pubs/sp/800/218/final | Security embedded across development lifecycle |
| Google Engineering Practices: Code Review | https://google.github.io/eng-practices/review/reviewer/looking-for.html | Design, correctness, complexity, maintainability |
| Google SRE Service Level Objectives | https://sre.google/sre-book/service-level-objectives/ | Meaningful workload/latency measures, when relevant |
| Claude Code subagents | https://code.claude.com/docs/en/sub-agents | Independent context and specialized review costs |
| Claude Code security | https://code.claude.com/docs/en/security | Permissions, read-only boundaries |
| OpenAI Codex code-review rules | https://developers.openai.com/blog/custom-code-review-rules-for-codex | Focused rules and findings |
| OpenAI Codex prompting | https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide | Actionable severity and location evidence |

**Evidence boundary:** Security and performance tradeoff patterns come from NIST/OWASP/SEI and engineering practices; exact workflow fields, reviewer routing and hashes above are design inferences specific to this project. Public publisher pages do not equal reading the complete books. No live account/CLI model suitability or token-cost reduction was measured.
