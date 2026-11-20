---
task_id: "019"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "018"
allowed_related_task_reads: "none"
---

# 019 — Review and correct leases, resume, cancellation, reset and guarded cleanup

Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/018-lifecycle.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Dispatch the independent reviewer — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 019` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Implement change 2 — Correct every blocking finding or leave the gate incomplete with a recorded reason.
- [ ] **S004** Implement change 3 — Re-run declared checks after corrections and pin the final reviewed source state.
- [ ] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct leases, resume, cancellation, reset and guarded cleanup
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/planctl.py`, `test/optimization/lifecycle_self_test.py`, `skill/plan-and-execute/references/LIFECYCLE.md`, `docs/research/20261028-skill-optimization/implementation/019-receipt.json`, `docs/research/20261028-skill-optimization/implementation/019-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/018-lifecycle.md.
- Use only task 019 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/019-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Review the revision-2 alternatives, scope boundary and negative tests against the actual changed code; report unsupported cost/quality claims.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_019`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_019`

## Pesquisa e arquitetura obrigatórias (pré-execução)

- **Arquitetura aprovada de partida para a revisão 019:** [019-pesquisa-arquitetura.md](../../../../docs/research/20261028-skill-optimization/pesquisas-por-task/019-pesquisa-arquitetura.md) (caminho desde a raiz: `docs/research/20261028-skill-optimization/pesquisas-por-task/019-pesquisa-arquitetura.md`).
- Antes de S001–S006, a IA revisora/implementadora deve **ler e seguir integralmente** o relatório como arquitetura de referência obrigatória, junto da decisão preparada 018 e da arquitetura individual 018; conferir apenas incompatibilidades **materiais e demonstráveis** de código, APIs, versão ou contrato, documentando qualquer desvio. A pesquisa é pré-execução e **não** substitui o review independente real nem seus receipts.
- **Dependência inegociável:** a task 018 deve estar implementada, com 018-receipt.json, 018-outcome.md e hashes verificáveis. Sem tais artefatos, manter 019 pendente e não fabricar findings, session_id, aprovação ou testes. Fazer review via `review_dispatch.py --repo-root . --task 019` em foreground; corrigir apenas findings bloqueadores dentro do write scope, executar os checks declarados e redespachar review após alterações de arquivos revisados.
- **Integridade de projeções:** `planctl.save_manifest` regenera a definição da task no schema 4. Ler o vínculo neste arquivo e no guia antes do primeiro claim/save, e conferir a preservação/acessibilidade da arquitetura após regeneração. Não alterar manifest nem status de desenvolvimento em nome da pesquisa.
