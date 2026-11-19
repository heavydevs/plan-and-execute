# Amendment P061–P064 — 2026-11-19

Only amend the single active plan on `checkpoint/plano1-estudo-provider-switch-20261028`. User authorizes commit and push of the plan, **not** implementing product, running paid agents or editing legacy user tests.

Quando um agente fica sem créditos, outro assume, mas quando o preferencial recupera créditos a skill deve voltar a usá-lo automaticamente segundo preferências. Se todos esgotarem créditos no meio do plano, deve agendar retomada após créditos voltarem. Pesquisar amplamente livros, estudos, artigos, docs e benchmarks sobre criação/alteração de testes automáticos rápidos e de qualidade, preparar a task com arquitetura. Todas as tasks devem usar roteamento econômico e contexto mínimo, sem ler arquivos irrelevantes. Commit e push no branch checkpoint/plano1-estudo-provider-switch-20261028.

- P061/R061: restore configured highest-priority eligible provider at next safe dispatch, no active worker preemption.
- P062/R062: all providers quota exhausted => durable checkpoint, one-shot automatic recheck and truthful manual fallback if scheduling unsupported.
- P063/R063: improve AI-created tests' oracles/defect-detection quality, complementing existing 109-114 test selection and legacy edit authorization.
- P064/R064: enforce model routing and token-efficient selective context in every current/future TODO, including new tasks.

Implementation and independent reviews: 115/116, 117/118, 119/120. Single plan expands 114 to 120 pending tasks, with 116/118/120 gating integration 082; final 086 remains last. Research:
- docs/research/20261028-skill-optimization/prepared-research/115-quota-auto-recovery.md
- docs/research/20261028-skill-optimization/prepared-research/117-ai-test-oracle-quality.md
- docs/research/20261028-skill-optimization/prepared-research/119-task-wide-lazy-routing.md
