---
task_id: "015"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "014"
allowed_related_task_reads: "none"
---

# 015 — Review and correct assigned context, learned facts and token budgets

Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [x] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Dispatch the independent reviewer — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 015` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Implement change 2 — Correct every blocking finding or leave the gate incomplete with a recorded reason.
- [ ] **S004** Implement change 3 — Re-run declared checks after corrections and pin the final reviewed source state.
- [ ] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct assigned context, learned facts and token budgets
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/planctl.py`, `skill/plan-and-execute/scripts/artifact_contract.py`, `skill/plan-and-execute/scripts/runner_contract.py`, `test/optimization/context_learning_self_test.py`, `skill/plan-and-execute/references/EXECUTION_CONTEXT.md`, `skill/plan-and-execute/references/TOKEN_EFFICIENCY.md`, `docs/research/20261028-skill-optimization/implementation/015-receipt.json`, `docs/research/20261028-skill-optimization/implementation/015-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/014-context-learning.md.
- Use only task 015 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/015-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Review the revision-2 alternatives, scope boundary and negative tests against the actual changed code; report unsupported cost/quality claims.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 014 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_015`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_015`

## Pesquisa e arquitetura obrigatórias (pré-execução)

- **Estudo antecipado:** `docs/research/20261028-skill-optimization/pesquisas-por-task/015-pesquisa-arquitetura.md`.
- A IA revisora **deve usar a arquitetura, matriz de riscos, fontes e estratégia de validação desse relatório como referência obrigatória de partida**; consultar o relatório 014 para contextos anteriores. Verificar apenas divergências materiais de código/versão; não repetir pesquisa ampla sem mudança que altere uma decisão.
- Este vínculo certifica **somente a pesquisa antecipada**, não a revisão independente 015, nem testes, nem conclusão da implementação. Preservar o dispatch real, os receipts e os checks declarados.
