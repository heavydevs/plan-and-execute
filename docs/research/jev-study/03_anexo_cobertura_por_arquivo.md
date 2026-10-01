# Anexo - Cobertura por arquivo e evidência de testes

**Snapshot:** `6be46885ad691d3d43557a42fc2fd36a804b7eba`.  
**Pasta coberta integralmente pelo inventário:** `skill/plan-and-execute/`.

## Como interpretar a cobertura

Os 79 arquivos foram obtidos e seus hashes Git comparados com a árvore remota. Todos os scripts Python receberam inspeção estrutural de funções, chamadas, importações e guardas; a documentação foi cruzada com os fluxos relevantes. A leitura aprofundada concentrou-se nos contratos e caminhos de autoridade, roteamento, falhas, contexto, validação e limpeza.

**Cobertura de inventário não significa leitura manual linha a linha de cada arquivo.** O campo `inspection_method` do JSON distingue os métodos. Não seria correto apresentar uma inspeção estrutural como prova de ausência de bugs.

`inventario_79_arquivos.json` conserva caminho, tamanho, linhas, hash verificado, URL fixada no commit, papel, proposta e método de inspeção. O mapa abaixo resume a utilidade de Jev em cada arquivo. As propostas não representam mudanças já realizadas.

## Entrada, metadados e recursos

| Arquivo | Linhas | Papel e proposta |
|---|---:|---|
| [`LICENSE.txt`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/LICENSE.txt) | 21 | **Licença.** Nenhuma inferência; preservar a licença. |
| [`SKILL.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/SKILL.md) | 82 | **Entrada e carga progressiva.** Referenciar decisões opcionais sob demanda; manter DIRECT sem estado e sem chamada obrigatória. |
| [`agents/openai.yaml`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/agents/openai.yaml) | 13 | **Metadados do agente.** Descrever o recurso como opcional, sem transformação da Jev em executor generativo. |
| [`assets/icon.svg`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/assets/icon.svg) | 7 | **Recurso visual.** Nenhum uso de Jev. |
| [`assets/service-map-template.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/assets/service-map-template.md) | 24 | **Template de recursos.** Manter schema determinístico; eventual sugestao de dependências deve exigir reconciliação. |

## Referências

| Arquivo | Linhas | Papel e proposta |
|---|---:|---|
| [`references/ADAPTIVE_STUDY.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ADAPTIVE_STUDY.md) | 163 | **Estudo adaptativo.** Sugerir pertinência de evidências sem reduzir a profundidade escolhida pelo usuário. |
| [`references/ARTIFACT_WRITING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ARTIFACT_WRITING.md) | 202 | **Precisão dos artefatos.** Avaliar ambiguidade como conselho; limites de tamanho e campos ficam no programa. |
| [`references/ASSISTANTS.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ASSISTANTS.md) | 39 | **Conselho de falhas.** Documentar o contrato tipado separado e seus limites de autoridade. |
| [`references/EXECUTION_CONTEXT.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/EXECUTION_CONTEXT.md) | 112 | **Contexto por tarefa.** Ordenar candidatos; preservar fatos obrigatórios e escopo de compartilhamento. |
| [`references/INSTALLATION.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/INSTALLATION.md) | 190 | **Instalação.** Explicar credencial e dependência opcionais, sem chamada automática. |
| [`references/INSTALLATION.pt-BR.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/INSTALLATION.pt-BR.md) | 180 | **Instalação em português.** Manter paridade com o guia e explicar envio externo de evidência. |
| [`references/INTAKE.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/INTAKE.md) | 188 | **Recepção de demanda.** Sinalizar ambiguidade sem inventar requisitos ou repetir perguntas respondidas. |
| [`references/LIFECYCLE.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/LIFECYCLE.md) | 109 | **Ciclo de vida.** Nenhuma autoridade semântica sobre cancelamento, retomada ou limpeza. |
| [`references/MODEL_ROUTING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/MODEL_ROUTING.md) | 121 | **Política de modelos.** Receber sinais sugeridos; preservar pisos e corrigir generalizacoes documentais. |
| [`references/MODEL_ROUTING_CLAUDE.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/MODEL_ROUTING_CLAUDE.md) | 88 | **Adapter Claude.** Manter capacidades do executor distintas do avaliador Jev. |
| [`references/MODEL_ROUTING_CODEX.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md) | 91 | **Adapter Codex.** Corrigir a descrição de overrides; não adicionar Jev ao catálogo de programação. |
| [`references/ORCHESTRATION.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ORCHESTRATION.md) | 173 | **Planejamento e execução.** Adicionar pontos opcionais; manter autoridades e revisão independente. |
| [`references/PLANNING_INPUT_CONTRACT.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PLANNING_INPUT_CONTRACT.md) | 66 | **Contrato do pacote preparado.** Comparar suporte semântico; verificar hashes e IDs sem modelo. |
| [`references/PLANNING_PROTOCOL.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PLANNING_PROTOCOL.md) | 183 | **Decomposição.** Revisar coesão e cobertura como conselho ao planejador. |
| [`references/PLANNING_ROUTING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PLANNING_ROUTING.md) | 82 | **Capacidade de planejamento.** Sugerir sinais por etapa, sem herdar automaticamente a rota do executor. |
| [`references/PLAN_SPEC.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PLAN_SPEC.md) | 226 | **Schema do plano.** Separar metadados de decisão de status e aceite autoritativos. |
| [`references/PRIMARY_PLANNING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PRIMARY_PLANNING.md) | 188 | **Fontes extensas.** Classificar fragmentos; preservar digests generativos e fontes imutáveis. |
| [`references/PROMOTION.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PROMOTION.md) | 84 | **Promoção tardia.** Sugerir que o restante ganhou fronteiras independentes, sem recriar trabalho concluído. |
| [`references/ROUTING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ROUTING.md) | 68 | **DIRECT versus ORCHESTRATED.** Julgamento opcional apenas na fronteira ambigua. |
| [`references/ROUTING_CONFIG.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ROUTING_CONFIG.md) | 54 | **Configuração e disponibilidade.** Introduzir namespace próprio para o backend de decisões. |
| [`references/SHARED_PATTERNS.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/SHARED_PATTERNS.md) | 171 | **Contratos compartilhados.** Sinalizar equivalência/conflito; nunca revisar automaticamente contratos. |
| [`references/SKILL_MAINTENANCE_REVIEW.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/SKILL_MAINTENANCE_REVIEW.md) | 22 | **Revisão da própria skill.** Adicionar coerência documental e limites do avaliador ao checklist. |
| [`references/STUDY_CHOICES.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/STUDY_CHOICES.md) | 86 | **Preferências de estudo.** Escolhas explícitas do usuário sempre prevalecem sobre inferências. |
| [`references/TEST_RESOURCE_MONITORING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md) | 140 | **Observabilidade dos testes.** Conselho após falha, não inferências repetidas durante cada amostra. |
| [`references/TOKEN_EFFICIENCY.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/TOKEN_EFFICIENCY.md) | 85 | **Economia de contexto.** Medir custo por resultado validado e evitar chamadas onde codigo basta. |
| [`references/WORKFLOW.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/WORKFLOW.md) | 232 | **Contrato de execução.** Corrigir hooks de padrões desatualizados e preservar fail-before-advice. |
| [`references/completion-report.schema.json`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/completion-report.schema.json) | 137 | **Relatório de conclusão.** Schema continua determinístico; conselho externo não aprova completed. |
| [`references/plan-spec.example.json`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/plan-spec.example.json) | 195 | **Exemplo de plano.** Explicar comandos de exemplo versus validação monitorada de produção. |
| [`references/routing-evals.json`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/routing-evals.json) | 35 | **Casos de entrada.** Reusar como baseline e ampliar com casos novos PT/EN e abstenção. |
| [`references/study-spec.example.json`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/study-spec.example.json) | 123 | **Exemplo de estudo.** Representar evidências e escopo; não substituir síntese por classificação. |
| [`references/tier-evals.json`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/tier-evals.json) | 34 | **Casos de piso.** Provar que sinais sugeridos jamais abaixam o piso determinístico. |

## Scripts e self-tests

| Arquivo | Linhas | Papel e proposta |
|---|---:|---|
| [`scripts/artifact_concision_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/artifact_concision_self_test.py) | 232 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/artifact_contract.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/artifact_contract.py) | 1045 | **Validadores e projeções.** Preservar contratos; plugar lint semântico fora da validação obrigatória. |
| [`scripts/assistant_triage.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/assistant_triage.py) | 387 | **Triagem limitada.** Primeiro piloto: adapter tipado, reserva, deduplicação e conselho sem autoridade. |
| [`scripts/assistant_triage_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/assistant_triage_self_test.py) | 264 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/availability.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/availability.py) | 164 | **Disponibilidade.** Sem Jev no caminho normal; falha do avaliador não muda rota de programação. |
| [`scripts/availability_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/availability_self_test.py) | 190 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/configure.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/configure.py) | 282 | **Wizard.** Opt-in separado e transparente, sem inferência no show/dry-run. |
| [`scripts/configure_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/configure_self_test.py) | 164 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/context_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/context_self_test.py) | 243 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/lifecycle_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/lifecycle_self_test.py) | 333 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/lifecyclectl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/lifecyclectl.py) | 721 | **Estado e leases.** Nenhuma decisão por modelo sobre locks, donos, cancelamento ou recuperação. |
| [`scripts/lifecyclectl_concise.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/lifecyclectl_concise.py) | 11 | **Wrapper de ciclo de vida.** Sem rede na importação nem novas responsabilidades semânticas. |
| [`scripts/log_watch.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/log_watch.py) | 166 | **Leitura incremental de logs.** Cursores e limites continuam exatos; fornecer apenas trecho elegivel ao conselheiro. |
| [`scripts/model_routing_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/model_routing_self_test.py) | 194 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/pattern_runner_contract.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/pattern_runner_contract.py) | 165 | **Hooks de padrões.** Preservar assignment/adopt/validate; não duplicar wrappers. |
| [`scripts/pattern_runner_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/pattern_runner_self_test.py) | 163 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/pattern_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/pattern_self_test.py) | 133 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/patternctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/patternctl.py) | 539 | **Registro de padrões.** Conselho de conflito fica fora da revisão e reabertura determinísticas. |
| [`scripts/planctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/planctl.py) | 3701 | **Estado autoritativo.** Nenhuma autoridade a Jev; novos metadados não alteram invariantes de status. |
| [`scripts/planctl_concise.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/planctl_concise.py) | 11 | **Wrapper do controlador.** Manter inicialização idempotente e sem chamadas externas. |
| [`scripts/preplan_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/preplan_self_test.py) | 193 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/preplanctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/preplanctl.py) | 840 | **Fragmentos e pacote.** Semantica em tarefas auxiliares; split/IDs/hashes continuam exatos. |
| [`scripts/process_tree.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/process_tree.py) | 166 | **Árvore de processos.** Nenhuma Jev para PIDs, processos filhos, limites ou encerramento. |
| [`scripts/promotectl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/promotectl.py) | 302 | **Handoff de promoção.** Sugestão anterior ao comando; preservar apenas resultados remanescentes. |
| [`scripts/promotion_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/promotion_self_test.py) | 79 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/provider_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/provider_self_test.py) | 421 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/requestctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/requestctl.py) | 446 | **Pedido e intake.** Fonte original preservada; classificação não pode reescrever evidência. |
| [`scripts/resource_watch.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/resource_watch.py) | 545 | **Saúde e progresso.** Nao incluir rede de Jev no loop temporal do watcher. |
| [`scripts/routing_config.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/routing_config.py) | 206 | **Overlay e schema.** Backend próprio de decisões com defaults desligados e compatibilidade. |
| [`scripts/routing_config_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/routing_config_self_test.py) | 135 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/routing_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/routing_self_test.py) | 84 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/routingctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/routingctl.py) | 352 | **Pisos e escadas.** Receber sinais válidos, calcular piso em codigo, nunca usar confidence como autorização. |
| [`scripts/run_concise.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/run_concise.py) | 19 | **Entrypoint do runner.** Integracao idempotente; preservar hooks existentes e zero chamada ao importar. |
| [`scripts/run_isolated.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/run_isolated.py) | 1949 | **Execução e validação.** Registrar falha antes do conselho; manter validação independente e resumo generativo. |
| [`scripts/runner_contract.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/runner_contract.py) | 136 | **Reforço dos contratos.** Jev não flexibiliza campos, leitura de contexto, subtarefas ou artefatos. |
| [`scripts/self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/self_test.py) | 1250 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/service_map.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/service_map.py) | 634 | **Inventário de recursos.** Sugestões de impacto sao auxiliares; hash, frescor e reconciliação continuam obrigatórios. |
| [`scripts/study_choice_interaction_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/study_choice_interaction_self_test.py) | 77 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/study_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/study_self_test.py) | 560 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/studyctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/studyctl.py) | 1190 | **Estudo persistido.** Registrar avaliação como evidência auxiliar, nunca como aprovação automática. |
| [`scripts/studyctl_concise.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/studyctl_concise.py) | 10 | **Wrapper de estudo.** Nenhuma carga extra de rede no fluxo desligado. |
| [`scripts/task_memory_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/task_memory_self_test.py) | 413 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |
| [`scripts/token_efficiency_self_test.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/token_efficiency_self_test.py) | 62 | **Self-test de contrato.** Manter determinístico; ampliar casos do ponto afetado, sem usar Jev como oráculo de teste. |

## Resultados locais

O executável de teste foi rodado com ambiente privado e sem credenciais de provedores. Os testes usam seus próprios dublês; estes resultados não avaliam qualidade real ou latência da Jev.

| Suíte | Exit code | Resultado |
|---|---:|---|
| `routing_config_self_test.py` | 0 | Passou |
| `availability_self_test.py` | 0 | Passou |
| `configure_self_test.py` | 1 | 11/12 testes passaram; ponte Node não verificada por lançador ausente no pacote isolado |
| `assistant_triage_self_test.py` | 0 | Passou |
| `self_test.py` | 0 | Passou |
| `study_self_test.py` | 0 | Passou |
| `lifecycle_self_test.py` | 0 | Passou |
| `context_self_test.py` | 0 | Passou |
| `task_memory_self_test.py` | 0 | Passou |
| `provider_self_test.py` | 0 | Passou |
| `token_efficiency_self_test.py` | 0 | Passou |
| `model_routing_self_test.py` | 0 | Passou |
| `artifact_concision_self_test.py` | 0 | Passou |
| `study_choice_interaction_self_test.py` | 0 | Passou |
| `routing_self_test.py` | 0 | Passou |
| `promotion_self_test.py` | 0 | Passou |
| `preplan_self_test.py` | 0 | Passou |
| `pattern_self_test.py` | 0 | Passou |
| `pattern_runner_self_test.py` | 0 | Passou |

**Total:** 18 suítes com exit code zero em 19. Não foi executado `npm run check` localmente. A CI remota do mesmo commit informou sucesso; esse é outro registro de evidência, não um resultado local.

Os logs completos de cada suíte estão em `testes/`. O erro remanescente é de resolução do arquivo `/mnt/data/bin/plan-and-execute.js`, ausente no artefato que distribui apenas a skill. Uma validação posterior da integração deve usar o layout completo do repositório e repetir a ponte Node, além dos testes de Windows.

## Proveniência do pacote

Artefato GitHub Actions: `plan-and-execute-skill`, ID `11075307616`, run `36664762585`. SHA-256 do ZIP externo:

```text
b7fa8aa228a1bb99e624e5b8f7099957dbcaad18f6159610431b28d17aa63b49
```

O ZIP contém o pacote instalável da skill. Foram considerados os 79 arquivos rastreados correspondentes à árvore Git; arquivos de cache gerados não fazem parte do inventário.