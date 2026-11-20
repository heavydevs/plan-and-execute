---
task_id: "017"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "016"
allowed_related_task_reads: "none"
---

# 017 — Review and correct versioned shared contracts and selective invalidation

Objective: Review the actual implementation against the assigned prepared decision, correct blocking findings and re-run the targeted acceptance tests.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned decision and pin baseline — Read docs/research/20261028-skill-optimization/prepared-research/016-shared-patterns.md. Confirm source applicability; do not repeat broad research.
- [ ] **S002** Dispatch the independent reviewer — Run `python docs/plans/20261028-skill-optimization/support/review_dispatch.py --repo-root . --task 017` in the foreground (rerun on exit 75); use only its DISPATCH line and compact findings.
- [ ] **S003** Implement change 2 — Correct every blocking finding or leave the gate incomplete with a recorded reason.
- [ ] **S004** Implement change 3 — Re-run declared checks after corrections and pin the final reviewed source state.
- [ ] **S005** Run declared regression checks — Run the declared targeted tests through the resource watcher. Implement every assigned acceptance case and preserve failures and limitations.
- [ ] **S006** Record acceptance evidence — Write the implementation receipt and outcome report with changed-file hashes, acceptance coverage and actual test logs. Leave unresolved work pending.

## Scope

In: Review and correct versioned shared contracts and selective invalidation
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/patternctl.py`, `skill/plan-and-execute/scripts/pattern_runner_contract.py`, `test/optimization/shared_patterns_self_test.py`, `skill/plan-and-execute/references/SHARED_PATTERNS.md`, `docs/research/20261028-skill-optimization/implementation/017-receipt.json`, `docs/research/20261028-skill-optimization/implementation/017-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/016-shared-patterns.md.
- Use only task 017 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/017-receipt.json.
- Review only via review_dispatch.py (synchronous; max route; writes dispatch evidence); fix blocking findings, rerun declared checks, re-dispatch if a reviewed file changed, copy its RECEIPT_REVIEWER fields into the receipt.
- Review the revision-2 alternatives, scope boundary and negative tests against the actual changed code; report unsupported cost/quality claims.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Never launch background or asynchronous agents or processes: this headless session ends when you stop calling tools, so anything unfinished is lost.

## Acceptance

- Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.
- No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.
- A reused or fabricated review receipt is rejected.
- A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated max-review failure; a reused review session or dispatch is rejected.
- Every 2026-11-20 acceptance addition of task 016 has actual test evidence on the final reviewed hashes.
- The prepared report is input evidence, not proof that this implementation or its independent review has passed.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_017`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_017`

## Pesquisa e arquitetura obrigatórias (pré-execução)

- **Relatório de estudo antecipado e arquitetura de revisão:** `docs/research/20261028-skill-optimization/pesquisas-por-task/017-pesquisa-arquitetura.md`.
- A IA que executar ou revisar esta task **deve ler e adotar esse relatório como arquitetura de referência obrigatória** para a revisão independente: hipóteses de defeitos, invariantes, matriz de testes negativos, protocolo de hashes/recibos, segurança, concorrência, compatibilidade e economia de tokens. Use também a arquitetura-base da 016. Revalide apenas mudanças materiais de código/versão entre o estudo e a implementação efetivamente entregue por 016; não trate hipóteses do estudo como achados comprovados.
- **Gate de independência:** somente iniciar 017 depois de 016 concluída com `016-receipt.json`, `016-outcome.md`, fonte/testes e evidência real; execute o `review_dispatch.py --task 017` conforme S002, corrija findings críticos/altos no escopo e refaça revisão para hashes alterados. O relatório não substitui essa revisão nem autorização de implementação.
- O vínculo é **somente preparatório**: não modifica status, dependências, checkpoints, ownership, aceite ou testes; não declara que 016/017 foram implementadas, aprovadas ou executadas.
