---
task_id: "018"
status: "pending"
requirements: "R002,R003,R004,R005,R007,R032,R037,R038,R039,R042,R044"
dependencies: "001,013,015"
allowed_related_task_reads: "none"
---

# 018 — Implement leases, resume, cancellation, reset and guarded cleanup

Objective: Use owned, generation-aware leases and scoped receipt validity for resume; keep cleanup local, guarded and independent of model judgment.

## Context

- `.ai-work/20261028-skill-study-provider-switch/CONTEXT.md`

## Validated learnings

- None

## Checkpoints

- [ ] **S001** Read assigned research and pin applicable contracts — Read docs/research/20261028-skill-optimization/prepared-research/018-lifecycle.md. Verify the current source and only material version/account conflicts.
- [ ] **S002** Implement revised contract 1 — Fence task completion by lease generation and verify process-start identity before process actions.
- [ ] **S003** Implement revised contract 2 — Represent ambiguous post-crash effects as uncertain and require reconciliation before replay.
- [ ] **S004** Implement revised contract 3 — Extend 012's receipt-validity function with scoped contract/input fingerprints (no second fingerprint); reserve whole-repository fingerprints for integration checks.
- [ ] **S005** Validate all assigned positive and negative cases — Run the declared regression commands and every assigned acceptance counterexample. Preserve command logs, input hashes, actual failures and unmeasured limits.
- [ ] **S006** Record implementation evidence for independent review — Write changed-file or justified-preservation evidence and test receipts. Prepared research and fixture-only design are not proof that runtime implementation or independent review passed.

## Scope

In: Implement leases, resume, cancellation, reset and guarded cleanup
Out: No new broad research phase or second-plan generation.; Do not change installed copies, user-global settings or publish without permission.
Files: `skill/plan-and-execute/scripts/lifecyclectl.py`, `skill/plan-and-execute/scripts/planctl.py`, `test/optimization/lifecycle_self_test.py`, `skill/plan-and-execute/references/LIFECYCLE.md`, `docs/research/20261028-skill-optimization/implementation/018-receipt.json`, `docs/research/20261028-skill-optimization/implementation/018-outcome.md`

## Guidance

- Read docs/research/20261028-skill-optimization/prepared-research/018-lifecycle.md.
- Use only task 018 inputs and declared checks in docs/plans/20261028-skill-optimization/TASK_INPUTS.json.
- Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.
- Write actual changed-file, test and acceptance evidence to docs/research/20261028-skill-optimization/implementation/018-receipt.json.
- Use the revision-2 alternatives and counterexamples; preserve security/capability floors before optimizing cost.
- Treat vendor results as bounded evidence, not measured savings here. Refresh only a material version/account mismatch.
- Use only the declared write scope. Shared-file writers wait for the preceding writer and its correction review.
- Complete all owned report instructions. The checkpoints group correlated changes; they do not waive any instruction or acceptance case.

## Acceptance

- A reused PID does not authorize killing an unrelated process.
- Interruptions after each state-write boundary retain completed subtasks and recover only in-progress state.
- Symlinks, parent paths and directories without the plan sentinel cannot be cleaned.
- Cancelled jobs are stopped before their control directory is removed.
- Successful cleanup preserves implementation, tests, shared resource inventory and research reports.
- A reused PID cannot satisfy an old lease or be killed by a stale controller.
- A runner that lost its lease cannot publish task completion.
- An unrelated file change does not invalidate a task receipt while its actual dependency change does.
- Prepared research is not proof of implementation or independent-review completion.

## Validate

- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_018`
- `python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_018`

## Pesquisa e arquitetura obrigatórias (pré-execução)

- **Referência arquitetural aprovada de partida para esta task:** [018-pesquisa-arquitetura.md](../../../../docs/research/20261028-skill-optimization/pesquisas-por-task/018-pesquisa-arquitetura.md) (caminho desde a raiz: `docs/research/20261028-skill-optimization/pesquisas-por-task/018-pesquisa-arquitetura.md`).
- Antes de implementar S001–S006, a IA implementadora deve **ler e seguir integralmente** o relatório como arquitetura de referência obrigatória, junto da pesquisa preparada 018; rever somente incompatibilidades materiais e demonstráveis de versão, API, contrato ou código atual, documentando qualquer desvio e sua justificativa. Não trocar a arquitetura por nova pesquisa genérica nem confundir estudo com receipt de execução.
- Proteger identidade real do processo, fencing de conclusão, reconciliação de efeitos incertos, validação escopada pelo validador único de 012 e limpeza que falha com segurança. Preservar todos os ACs, os checks e o write_scope da task; não marcar desenvolvimento/revisão concluído por causa da pesquisa.
- **Atenção à projeção:** `planctl.save_manifest` reescreve definições da schema 4 a partir do manifest; consumir este vínculo antes do primeiro claim/save e conferir que ele continua acessível pelo guia/relatório após qualquer regeneração. Não alterar manualmente status ou manifest para preservar o vínculo.
