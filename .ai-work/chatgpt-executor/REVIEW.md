# Reviewer contract and evidence levels

## Separate evidence types

1. **Local static analysis** (syntax, diff, source reads) can find defects, but is not an independent model review or proof of test execution.
2. **Executed automated tests** prove only the asserted behavior on the reported exact commit, platform, commands and environment. A pass for `self-test` proves just this harness.
3. **Independent review** requires a distinct authorized reviewer (the repo's `review_dispatch.py` through genuine max-tier Codex/Claude, or a future formally approved equivalent), full provider/model/effort/session provenance, hash-bound reviewed inputs and a clear no-blockers verdict. A second pass in this same ChatGPT conversation does **not** satisfy that contract.

## 015 instructions

First read `.ai-work/20261028-skill-study-provider-switch/tasks/015-*.md` and `docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md`. The completed 014 receipt and outcome, not an unexecuted pre-study, are the reviewed implementation. Review trust boundaries, prompt injection, provenance hash integrity, `#symbol`-style file anchors, stale learnings on retries, scoped context and bounded prefix/suffix. Verify the acceptance additions on 2026-11-20 and all declared checks on the final SHA.

- Run `taskctl.py review-packet --task 015` to create a small deterministic input packet.
- If an authorized external CLI exists, use `taskctl.py dispatch-review --task 015`, which invokes `review_dispatch.py --repo-root . --task 015` in the foreground. Follow its exit-code-75 rule by re-running **the same dispatcher** in foreground; do not start another reviewer. Direct `taskctl dispatch-review` timeout should be configured beyond the dispatcher wait.
- If no CLI or remote review backend exists, mark **blocked by missing independent reviewer**; do not submit fabricated `RECEIPT_REVIEWER` fields, and do not mark S002/S006 or the task complete.
- Human GitHub PR review or CodeQL findings can be useful **supplementary** evidence; they do not automatically satisfy the explicit max-tier independent reviewer contract without approved plan amendment.

When reviewing source, report finding severity, exact path:line, reproducible failing case and scope, or state that evidence is inconclusive. No speculative critical findings. Always re-review changed files after fixes.