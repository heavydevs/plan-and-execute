# Relatório 2 - Como melhorar plan-and-execute com Jev

**Repositório:** `heavydevs/plan-and-execute`.  
**Snapshot:** `6be46885ad691d3d43557a42fc2fd36a804b7eba`, consultado em 30/09/2026.  
**Escopo desta entrega:** pesquisa e recomendações. Nenhuma alteração remota, commit, push, instalação de Jev ou chamada autenticada foi realizada.

## 1. Parecer

**Há um encaixe real para Jev, mas como avaliador semântico opcional, não como novo executor de programação ou autoridade do plano.** O primeiro experimento deve ser a triagem de falhas já existente. O segundo, seleção de evidência/contexto. Só depois de medir esses resultados eu introduziria sugestões semânticas para roteamento inicial, estudo e revisão de planos.

A arquitetura proposta preserva o que a skill já faz bem:

```text
pedido/evidência
  -> coleta e regras determinísticas
  -> caso ambíguo elegível?
       não: fluxo atual
       sim: Jev -> resposta tipada sem autoridade
  -> política local + pisos + restrições do usuário
  -> executor atual
  -> validação independente
  -> estado persistido por controladores
```

A proposta não pressupõe que um modelo barato melhora qualidade. Ela cria um experimento que pode mostrar ganho, neutralidade ou prejuízo em cada ponto de decisão.

## 2. Evidência, cobertura e limites da análise

Obtive pelo conector GitHub o artefato da CI do commit indicado. A extração validada contém **79 arquivos da skill, 1.048.044 bytes e 23.191 linhas**: 43 scripts Python, 31 referências e cinco arquivos de entrada, metadados, recursos e licença. Os hashes Git de todos os 79 arquivos foram comparados com a árvore remota correspondente. O inventário anexo registra essas identidades.

A inspeção combinou leitura da documentação, leitura dos fluxos críticos, extração estrutural de todos os módulos Python, rastreamento de funções e execução dos self-tests. **Isso não equivale a afirmar leitura manual linha a linha dos 79 arquivos ou auditoria exaustiva de segurança.** O anexo distingue leitura de contrato, inspeção estrutural e leitura aprofundada de implementação. Os arquivos externos à pasta da skill foram consultados seletivamente; não foi feito um checkout completo do repositório.

### Testes realmente executados

Foram executadas localmente as **19 suítes Python enumeradas pelo runner do projeto**. Dezoito terminaram com código zero. Em `configure_self_test.py`, um dos 12 testes falhou porque o pacote isolado não contém o lançador Node na estrutura esperada pelo teste: `Cannot find module '/mnt/data/bin/plan-and-execute.js'`. Os outros 11 testes dessa suíte passaram. Isso limita a validação local da ponte Node, não demonstra por si só um defeito do produto.

Separadamente, a CI do GitHub para esse commit, execução **36664762585**, estava concluída com sucesso. Não confundo esse registro remoto com uma execução local de `npm run check`. Os logs locais estão no pacote de entrega. Não houve benchmark de Jev contra um provedor autenticado.

## 3. O que deve ser preservado

O ponto de entrada separa `DIRECT` de `ORCHESTRATED`, evita criar estado de planejamento para demandas coesas e pequenas, e permite promoção posterior. A complexidade de uma folha não é herdada automaticamente do tamanho da demanda. Os pisos são calculados por `routingctl.minimum_route`; implementação, estudo, design e disponibilidade têm responsabilidades distintas. Ver `SKILL.md`, `MODEL_ROUTING.md`, `ROUTING.md` e `PROMOTION.md`.

`manifest.json` é a autoridade das tarefas. `planctl.py` controla transições, subtarefas, evidências, completude e limpeza. `run_isolated.py` despacha trabalhadores e reexecuta validações. `patternctl.py` administra contratos compartilhados, revisões e signatários. O resultado declarado por um trabalhador não basta para aceitar sua implementação. Ver `WORKFLOW.md`, `ORCHESTRATION.md` e `PLAN_SPEC.md`.

O pré-planejamento preserva fragmentos imutáveis, hashes e referências. Contextos globais, contextos de subconjuntos, fatos locais e aprendizados direcionais possuem regras diferentes. O mapa de serviços, os monitores e os cursores de log reduzem redescoberta e separam falha ambiental de defeito funcional. Ver `PRIMARY_PLANNING.md`, `EXECUTION_CONTEXT.md`, `SHARED_PATTERNS.md`, `TOKEN_EFFICIENCY.md` e `TEST_RESOURCE_MONITORING.md`.

**Nenhuma dessas garantias deve passar a depender de uma resposta correta da Jev.**

## 4. Achados que merecem correção antes da integração

### A. Documentação contraditória sobre sobrescrita de modelos

`references/MODEL_ROUTING_CODEX.md`, linha 85, afirma que os IDs concretos são reaplicados a cada leitura da configuração, sobrescrevendo `codex.models`. Entretanto, `scripts/routingctl.py`, linhas 340-348, aplica o catálogo aos defaults e declara preservar configurações explícitas. Os testes de disponibilidade/configuração inspecionados corroboram a preservação de overrides.

**Recomendação:** alinhar o guia ao comportamento implementado e incluir uma verificação documental desse contrato. Não introduzir um backend de decisão enquanto a precedência dos modelos executores está descrita de forma ambígua.

### B. Guia de execução desatualizado sobre hooks de padrões

A seção de runner externo de `WORKFLOW.md` afirma que integrações devem envolver o runner com hooks de padrões até sua incorporação futura. No snapshot, `run_concise.py` já instala `pattern_runner_contract.py`; `ORCHESTRATION.md` também descreve a integração existente.

**Recomendação:** distinguir o caminho padrão, que já integra os hooks, de integrações realmente externas. Evitar orientações que levem um agente a aplicar a mesma camada duas vezes.

### C. Afirmação ampla sobre cache precisa ser harmonizada

`MODEL_ROUTING.md` apresenta uma afirmação geral sobre cache por modelo/esforço, enquanto o ponto de entrada e `TOKEN_EFFICIENCY.md` tratam esse comportamento como dependente do fornecedor/modelo. Não avaliei autenticamente cada combinação de CLI/modelo citada.

**Recomendação:** adotar linguagem uniforme, com versão e fonte por provedor, sem uma regra universal não comprovada. Isso evita justificar uma otimização de roteamento com premissa imprecisa.

### D. Sanitização e truncamento precisam de testes de fronteira

Em `assistant_triage.evidence`, os textos recebidos são cortados antes de certas chamadas de `redact`, enquanto a documentação enfatiza sanitizar antes de truncar. A análise identificou a diferenção de ordem; **não demonstrou vazamento explorável**.

**Recomendação:** acrescentar testes com segredos, delimitadores e blocos multilinha atravessando limites, e adotar uma estratégia de sanitização limitada em memória que falhe com segurança. Nunca substituir um problema de truncamento por leitura ilimitada de logs.

### E. Exemplos precisam explicitar seu contexto

`plan-spec.example.json` possui comandos diretos como testes de existência/grep, enquanto o contrato de planos orquestrados exige wrappers do mapa de validação. Isso pode ser exemplo reduzido ou fixture deliberada, não necessariamente bug funcional.

**Recomendação:** explicar a exceção ou disponibilizar um exemplo completo de produção. Não converter fixtures mecanicamente sem verificar seus consumidores.

## 5. Oportunidades em todas as etapas relevantes

Nesta seção, os comportamentos existentes são identificados pelos arquivos correspondentes. As integrações com Jev são **propostas**, não recursos já implementados ou ganhos medidos.

| Etapa e arquivos centrais | Proposta com Jev | Limite que permanece determinístico |
|---|---|---|
| Entrada: `SKILL.md`, `ROUTING.md`, `routing-evals.json` | Classificar sinais ambíguos de independência, risco e valor de retomada. | Comandos explícitos e `DIRECT` sem estado continuam prioritários; não chamar em todo pedido. |
| Intake: `INTAKE.md`, `requestctl.py` | Sinalizar informação material ausente em uma demanda. | O pedido original permanece intacto; não inventar requisito nem repetir escolha já feita. |
| Profundidade: `STUDY_CHOICES.md`, `ADAPTIVE_STUDY.md`, `studyctl.py` | Indicar quais incertezas podem mudar o plano e quais fontes merecem inspeção. | Escolha explícita do usuário, cobertura e proveniência não podem ser reduzidas por score. |
| Pré-planejamento: `preplanctl.py`, `PRIMARY_PLANNING.md` | Categorizar fragmentos e marcar candidatos a contrato, requisito ou contradição. | Split, IDs, ordem, hashes e preservação integral da fonte continuam em código. |
| Handoff: `PLANNING_INPUT_CONTRACT.md` | Verificar suporte entre afirmações do digest e fragmentos candidatos. | A existência de fragmentos, cobertura por IDs e hashes é checada por programa. |
| Requisitos: `PLANNING_PROTOCOL.md`, `PLAN_SPEC.md`, `artifact_contract.py` | Apontar requisitos possivelmente fundidos, ambíguos ou sem validação adequada. | P -> R -> TODO e limites de campos continuam sendo contratos; Jev não aprova o plano. |
| Decomposição: `PLANNING_ROUTING.md`, `ORCHESTRATION.md` | Avaliar coesão, dependência de contexto e necessidade de design separado. | O planejador decide fronteiras e arquitetura; DAG e tipos são validados localmente. |
| Contexto: `EXECUTION_CONTEXT.md`, `planctl.py` | Priorizar trechos candidatos e sugerir alcance global, de subconjunto ou local. | Nenhum requisito obrigatório é excluído; atribuição de arquivos permanece explícita. |
| Aprendizados: `planctl.py`, `task_memory_self_test.py` | Avaliar pertinência de um aprendizado para um alvo já declarado. | Somente origem validada e destino autorizado; não distribuir a todos os TODOs. |
| Padrões: `SHARED_PATTERNS.md`, `patternctl.py` | Detectar equivalência ou possível conflito entre contratos. | Revisão, signatários, reabertura e proteção de tarefas ativas continuam no controlador. |
| Roteamento: `routingctl.py`, `MODEL_ROUTING.md`, `tier-evals.json` | Propor sinais semânticos já conhecidos pelo calculador de piso. | Nunca abaixar o piso, violar provedor fixado ou decidir por mera confiança. |
| Falhas: `assistant_triage.py`, `ASSISTANTS.md` | Classificar evidência ambígua e selecionar códigos de hipótese. | A classe registrada, a escalada e a aceitação não mudam por conselho. |
| Disponibilidade: `availability.py`, `routing_config.py` | No máximo, aconselhar sobre mensagem desconhecida para revisão posterior. | HTTP/cota/autenticação, cooldown e troca permitida são código; indisponibilidade não é dificuldade. |
| Serviços: `service_map.py` | Sugerir recursos afetados por mudanças em arquivos de teste/configuração. | Fingerprints, IDs, frescor e revisão do inventário continuam obrigatórios. |
| Monitoramento: `resource_watch.py`, `process_tree.py`, `log_watch.py` | Triagem posterior de sintomas ainda ambíguos. | PID, CPU, timeouts, bytes lidos e interrupção de processos não dependem de Jev. |
| Validação: `run_isolated.py`, `runner_contract.py` | Apontar aceitação possivelmente não coberta por testes. | Testes precisam executar; resultados e subtarefas obrigatórias não podem ser dispensados. |
| Conclusão: `completion-report.schema.json`, `planctl.py` | Sinalizar afirmação de conclusão sem suporte no registro. | Schema, lista de artefatos, revisões e status são verificados independentemente. |
| Resumo final: `run_isolated.py`, `TOKEN_EFFICIENCY.md` | Avaliar afirmações do resumo contra `SUMMARY_INPUT.json`. | Texto final continua com gerador; fatos canônicos não são reescritos pelo avaliador. |
| Ciclo de vida: `lifecyclectl.py`, `LIFECYCLE.md`, `promotectl.py` | Sugestão de promoção somente quando o trabalho remanescente ficou ambíguo. | Leases, retomada, cancelamento, caminhos e limpeza nunca são decisões de modelo. |
| Manutenção: guias, exemplos, self-tests e CI | Revisão semântica opcional de contradições entre documentos. | Testes determinísticos de contrato continuam sendo a barreira obrigatória. |
| Instalação/configuração: `configure.py`, metadados e guias | Explicar e configurar explicitamente o backend opcional. | Instalação e `--show` não geram inferência nem revelam segredos. |

### 5.1 Onde o retorno parece mais plausível

**Triagem de falhas:** o ponto já tem gatilho, limites, evidência curta, ledger e consumidor sem autoridade. A integração não precisa redesenhar toda a skill.

**Seleção de contexto:** há uma oportunidade de reduzir leitura irrelevante, mas a métrica principal deve ser manter evidência necessária, não eliminar o maior volume possível. Recomendo começar apenas ordenando candidatos, antes de qualquer filtro excludente.

**Revisão de coerência documental:** é um trabalho de manutenção que pode rodar separado da execução comum. As divergências já identificadas fornecem exemplos positivos para uma avaliação, mas não devem contaminar o conjunto final de teste.

**Roteamento exige uma ressalva adicional:** um calculador de piso correto ainda pode receber sinais semanticamente errados. Jev classificar uma migração perigosa como edição mecânica enfraqueceria a decisão antes do cálculo. Portanto, os sinais obrigatórios já conhecidos por regras, contratos ou revisão devem ser preservados; a sugestão não os remove. Na dúvida, encaminhar a decisão para revisão. Isso é diferente de obrigar toda demanda a usar planejamento completo: uma folha pequena pode permanecer DIRECT e ser delegada a um executor mais capaz.

### 5.2 Onde eu não usaria Jev

Não usaria para contar tokens exatos, comparar hashes, decidir se uma suíte passou, validar um DAG, controlar arquivos, selecionar PIDs, matar processos, calcular prazos, decidir se uma credencial existe, alterar permissões ou executar limpeza. Também não substituiria pesquisa, escrita de requisitos, design, implementação e resumo por chamadas de decisão. A limitação de saída da Jev torna algumas dessas substituições tecnicamente inadequadas; as demais seriam uma regressão arquitetural. [S36]

## 6. Primeiro piloto: triagem sem autoridade

### 6.1 O contrato atual não aceita uma troca simples de fornecedor

`assistant_triage.py` aceita exatamente `suggested_class`, `confidence`, `hypothesis` e `evidence_refs`. A hipótese é texto livre. `native_profile` suporta um perfil específico, sem ferramentas, e pula perfis não comprovados. Jev não gera essa hipótese livre. Acrescentar `provider: jev` à lista atual seria insuficiente e confundiria contratos.

O contrato proposto deve usar escolhas tipadas e distinguir `backend` de `provider` executor. Uma alternativa é manter dois tipos de conselheiro, com um envelope comum e payloads diferentes: `freeform_diagnostic_v1` e `typed_diagnostic_v1`. Outra é introduzir uma camada `decisions` independente. Prefiro a segunda para não obrigar roteamento e ranking a caberem em um auxiliar de falhas.

### 6.2 Perguntas recomendadas

| Pergunta proposta | Tipo | Utilidade |
|---|---|---|
| Qual classe melhor descreve esta evidência? | Choice nas classes do projeto, incluindo `unknown` | Sugestão comparável à classe atual. |
| A evidência distingue problema ambiental de comportamento incorreto? | Noul | Sinalizar insuficiência; não inferir saúde a partir de silêncio. |
| Qual hipótese previamente cadastrada merece inspeção? | Choice, incluindo `none` | Substituir texto livre por código rastreável. |
| Quais trechos apoiam a classificação? | Noul por ID de evidência existente | Seleção de referências, não geração de evidência nova. |

Códigos possíveis de hipótese: `dependency_unready`, `configuration_mismatch`, `assertion_contract_mismatch`, `concurrency_suspected`, `insufficient_evidence`. São **catálogo proposto**. Um template local pode mostrar o nome e as referências; isso não deve ser apresentado como explicação produzida pela Jev.

### 6.3 Ordem de autoridade

No fluxo inspecionado de `run_isolated.execute_one_task`, a falha é registrada por `planctl.fail_task` antes da consulta ao auxiliar. Preservar essa ordem:

```text
validação falhou
  -> guardar resultado e classe autoritativos
  -> conferir elegibilidade e orçamento de conselho
  -> reservar tentativa persistente
  -> sanitizar evidência e consultar Jev
  -> validar resposta tipada
  -> registrar conselho não verificado
  -> próximo trabalhador decide se a hipótese procede
```

Divergência entre Jev e a classe atual deve virar informação de auditoria, não uma reclassificação automática. Isso evita que um log adversarial transforme erro funcional em problema ambiental e impeça a escalada apropriada.

### 6.4 Gatilhos e degradação

Manter a filosofia atual: nenhuma chamada em sucesso, auxiliar desativado ou diagnóstico determinístico conhecido. Uma evidência ambígua repetida pode ser elegível. Reserva interrompida consome tentativa; não refazer chamada durante a retomada apenas porque o processo anterior morreu.

Chave ausente, perfil inválido, timeout, erro de serviço, limite, resposta incompleta ou dados fora do contrato devem pular o conselho e preservar a falha original. Não acionar automaticamente outro modelo generativo, outra conta ou permissões mais amplas como recuperação de Jev.

## 7. Desenho de implementação proposto

### 7.1 Componentes novos e responsabilidades

| Arquivo proposto | Responsabilidade |
|---|---|
| `scripts/decision_client.py` | Transporte, autenticação explícita, timeout total, resposta limitada, normalização estrita e metadados de uso. Sem acesso ao manifest. |
| `scripts/decision_policy.py` | Elegibilidade por ponto, validação de sinais, abstenção, cache e versionamento. Sem ferramentas de escrita do produto. |
| `scripts/decisionctl.py` | Inspeção de configuração e replay offline explícitos; nada automático ao importar. |
| `references/JEV_DECISIONS.md` | Contrato curto, limites e instruções de uso, carregado sob demanda. |
| `references/jev-questions.json` | Perguntas versionadas e rubricas; sem segredos ou limiares apresentados como universalmente corretos. |
| `scripts/decision_self_test.py` | Contratos offline com transporte falso, incluindo adversários e orçamentos. |
| `docs/research/JEV_EVALUATION.md` | Protocolo, baseline e resultados medidos; fora do contexto de trabalhadores comuns. |

Não é necessário fragmentar excessivamente a base: se o primeiro piloto couber de forma coesa em menos módulos, essa separação pode ser lógica. O limite importante é não misturar conselho e autoridade.

### 7.2 Configuração ilustrativa

O bloco abaixo **não existe no snapshot**. Os valores de limites são escolhas conservadoras para um piloto, não recomendações universais nem garantias do fornecedor.

```json
{
  "decisions": {
    "enabled": false,
    "backend": "typesafe",
    "model": "jev-1.13.0",
    "mode": "shadow",
    "allowed_sites": ["failure_triage"],
    "max_calls_per_task": 1,
    "max_input_chars": 6000,
    "max_response_bytes": 32768,
    "timeout_seconds": 5,
    "max_retries": 0,
    "allow_external_evidence": false,
    "question_set_version": "pae-triage-v1"
  }
}
```

`enabled: false` garante que o exemplo não autoriza envio. A ativação deve exigir consentimento e explicar quais dados saem. Caracteres limitam o texto fornecido, não medem exatamente tokens faturados. Os limites devem considerar tokens observados e custo do processo completo.

Configuração global e overlay do plano devem preservar a precedência existente. A versão do schema precisa tratar backward compatibility explicitamente; exemplos novos não podem fazer configurações antigas falharem. `configure --show` e `--dry-run` devem continuar sem inferência e sem exposição de chave ou corpos de evidência.

### 7.3 Registro de decisão

Persistir somente o necessário: site, versão do contrato e das perguntas, modelo pedido/resolvido, hash da evidência sanitizada, tarefa e contador de falha, alternativas/probabilidades aceitas, motivo de abstenção, uso retornado, duração e identificador de requisição quando disponível. Não copiar logs completos ou credenciais.

O conselho precisa expirar quando muda a evidência, a revisão do contrato, a política ou o contador de falha. Cache por texto semelhante é insuficiente para assumir equivalência de contexto. A chave deve incluir o ponto de decisão, evitando reutilizar a mesma classificação em tarefas com permissões ou critérios diferentes.

Para custo, distinguir uso observado de uso desconhecido. Um timeout depois do envio pode ter consumido inferência mesmo sem resposta com contagem de tokens. Registrar `unknown`, em vez de zero, e não prometer execução exatamente uma vez sem um contrato de idempotência do serviço. A reserva local limita reenvios; ela não prova que o fornecedor deixou de processar um pedido interrompido.

### 7.4 Validação estrita da saída

Exigir todos os IDs esperados, tipos corretos, números finitos, intervalos válidos, opções conhecidas e distribuição coerente dentro de tolerância numérica definida. Rejeitar chaves duplicadas e payload excessivo. Uma resposta parcial não deve adquirir defaults que parecem aprovações.

O SDK pode ser usado, mas não dispensa validação de completude da aplicação. Seus retries e logs precisam ser configurados explicitamente; a documentação alerta para corpos não sanitizados em DEBUG. [S08]

### 7.5 Modelos, rubricas e confiança versionados

Fixar a versão durante cada avaliação; registrar a efetivamente usada. Uma troca de alias não pode substituir silenciosamente o objeto de calibração. Qualquer alteração material nas perguntas ou alternativas também exige reavaliação.

Não conservar o significado atual de `confidence` como se fosse idêntico em todos os conselheiros. No auxiliar generativo atual é autodeclarado; em Choice/Score da Jev é derivado da distribuição. Guardar `confidence_kind` ou envelopes distintos impede comparações enganosas. Noul não possui esse campo independente. [S06]

## 8. Evitar regressões de custo e segurança

**Zero custo quando desligado** deve ser uma propriedade testável: nenhum cliente inicializado com efeito de rede, descoberta autenticada ou chamada escondida. Atualizar metadados da skill não deve ativar dependência de credencial.

**Um conselho não concede acesso.** A camada recebe apenas evidência selecionada e sanitizada. A API não deve ler o repositório por conta própria. URLs de backend precisam ser configuradas por um operador confiável, não pelo texto de um log ou arquivo analisado.

**Falha do conselheiro não é falha do programador.** Um 401, 422, 429, 529 ou timeout de Jev não incrementa a escada semântica de Codex/Claude. O orçamento de disponibilidade do avaliador é separado do orçamento do trabalhador. [S02]

**Contratos obrigatórios não entram numa média.** A avaliação de qualidade não pode compensar um teste ausente ou uma violação de provedor permitido com boa nota de clareza. Um número alto pode orientar revisão, mas não cria evidência.

**Dados de calibração precisam de política própria.** Resultados de experimento que devem sobreviver à conclusão pertencem a um diretório de pesquisa/telemetria aprovado, não ao diretório descartável do plano. Persistir somente dados permitidos e com retenção definida; não usar a justificativa de pesquisa para manter logs sensíveis indefinidamente. [S33][S34]

## 9. Protocolo de avaliação antes de ativar

### 9.1 Baselines e conjunto de casos

Comparar pelo menos: fluxo atual sem conselho, auxiliar atual quando aplicável, Jev em sombra e Jev como conselho. Para ranking de contexto, comparar também a ordenação determinística existente. Concordar com o classificador anterior não define correção.

Construir casos reais sanitizados e casos controlados: defeito semântico, erro mecânico, falta de dependência, validação fraca, falha de autenticação, quota, limite de turnos, timeout, contradição e defeito de plano. Separar português, inglês e entradas mistas, e tarefas com diagnóstico claro das realmente ambíguas.

Separar treino de rubricas, calibração de limiares e teste final. Remover duplicatas por assinatura para não medir memória de variações do mesmo log. Usar mais de um revisor nos casos ambíguos, registrar discordância e não forçar um rótulo sem suporte.

### 9.2 Métricas que respondem à pergunta certa

| Eixo | Medida proposta |
|---|---|
| Resultado final | TODOs aceitos por validação independente, regressões e reaberturas. |
| Economia | Custo total por TODO aceito, incluindo consultas, fallback, repetições e validação. |
| Diagnóstico | Matriz de confusão por classe e custo de cada confusão. |
| Risco | Defeito funcional classificado como ambiental; evidência obrigatória excluída; escalada indevida. |
| Abstenção | Cobertura versus risco dos casos aceitos, por ponto de decisão e idioma. |
| Calibração | Curvas de confiabilidade e erros por faixa; não tratar um único limiar como universal. |
| Desempenho | Latência p50/p95 do fluxo completo e do avaliador. |
| Retomada | Chamadas duplicadas, reservas interrompidas, validade do conselho após mudança de estado. |
| Robustez | Desempenho com contexto faltante, ruído, alternativas incompletas e instruções adversariais. |

Um relato externo mostrou que o fallback por confiança pode melhorar uma decisão e piorar outra. Esse é um motivo concreto para medir a cascata fim a fim, não apenas o componente barato. [S29]

### 9.3 Testes offline obrigatórios

O transporte falso deve cobrir resposta malformada, campos faltantes, alternativa não permitida, JSON duplicado, NaN/infinito, tamanho excessivo, timeout, indisponibilidade e chave ausente. Interrupção entre reserva e resposta precisa preservar a contabilização; concorrência não pode gerar duas consultas para a mesma reserva.

Acrescentar casos de segredos atravessando o corte, DEBUG ativo, symlink em ledger, tarefa reiniciada, evidência com hash alterado, rubrica nova, modelo resolvido inesperado, resposta parcial do SDK e instrução maliciosa dentro de um log. A pesquisa JevAdvBench torna especialmente importante testar manipulação da escolha, mesmo sem texto livre. [S30]

Testes sem rede continuam obrigatórios na CI comum. Experimentos autenticados ficam em trilha separada, opt-in, com dados e orçamento aprovados. Falhar na configuração de Jev não pode impedir os testes comuns de usuários que não a utilizam.

## 10. Sequência de implementação recomendada

### Etapa 1 - Corrigir contratos e medir o baseline

Resolver as divergências documentais comprovadas, qualificar os exemplos e criar casos de sanitização de fronteira. Registrar custo, tentativas e qualidade sem Jev. Saída: comportamento atual descrito corretamente e medidas reproduzíveis.

### Etapa 2 - Cliente e política sem autoridade

Implementar transporte isolado, contratos tipados, configuração desativada, ledger, testes de falha e garantias de zero chamada no modo desligado. Saída: adapter seguro, ainda sem modificar decisões de produção.

### Etapa 3 - Triagem em modo sombra

Conectar apenas `failure_triage`, sem injetar conselho no trabalhador. Comparar com rótulos revisados e medir elegibilidade, qualidade e custo. Saída: decisão informada de prosseguir, reformular ou abandonar esse uso.

### Etapa 4 - Conselho limitado e ranking

Habilitar conselho somente onde o teste justificar. Experimentar ranking de candidatos de contexto sem exclusão inicial. Saída: ganho medido por TODO validado e preservação da evidência necessária.

### Etapa 5 - Expansão seletiva

Estudar roteamento por sinais, revisão de planos e coerência documental como experiências separadas. Recalibrar cada ponto e idioma; não copiar o limiar do primeiro piloto. Saída: somente os pontos com vantagem comprovada ficam ativos.

### Etapa 6 - Revisão final da skill

Reexecutar a suíte completa no layout de repositório, incluindo Node e Windows quando disponíveis, revisar todos os contratos afetados e conferir que saída `DIRECT`, restrições de provedor, retomada, validação independente e limpeza continuam intactas. Uma integração que economiza chamadas mas enfraquece essas garantias deve ser rejeitada.

## 11. Decisão recomendada

**Vale implementar um piloto restrito; não vale tornar Jev obrigatória nem inseri-la em todas as transições.** O caminho de menor risco aproveita o auxiliar existente, mas troca seu contrato de texto livre por um contrato tipado apropriado. Em paralelo, usar a manutenção documental para reduzir contradições que já podem prejudicar agentes hoje.

A economia pretendida é menos raciocínio generativo desperdiçado e menos tentativas equivocadas. Ela precisa ser demonstrada. O projeto já possui uma base de controle determinístico relevante; a integração deve protegê-la, não competir com ela.

## Referencias do snapshot

- [`SKILL.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/SKILL.md).
- [`references/ASSISTANTS.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ASSISTANTS.md).
- [`references/ROUTING_CONFIG.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ROUTING_CONFIG.md).
- [`references/MODEL_ROUTING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/MODEL_ROUTING.md).
- [`references/MODEL_ROUTING_CODEX.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/MODEL_ROUTING_CODEX.md).
- [`references/ORCHESTRATION.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/ORCHESTRATION.md).
- [`references/WORKFLOW.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/WORKFLOW.md).
- [`references/PRIMARY_PLANNING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PRIMARY_PLANNING.md).
- [`references/PLAN_SPEC.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/PLAN_SPEC.md).
- [`references/TEST_RESOURCE_MONITORING.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/TEST_RESOURCE_MONITORING.md).
- [`references/TOKEN_EFFICIENCY.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/TOKEN_EFFICIENCY.md).
- [`references/EXECUTION_CONTEXT.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/EXECUTION_CONTEXT.md).
- [`references/SHARED_PATTERNS.md`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/references/SHARED_PATTERNS.md).
- [`scripts/assistant_triage.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/assistant_triage.py).
- [`scripts/routingctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/routingctl.py).
- [`scripts/run_isolated.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/run_isolated.py).
- [`scripts/planctl.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/planctl.py).
- [`scripts/pattern_runner_contract.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/pattern_runner_contract.py).
- [`scripts/run_concise.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/run_concise.py).
- [`scripts/availability.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/availability.py).
- [`scripts/service_map.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/service_map.py).
- [`scripts/resource_watch.py`](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/skill/plan-and-execute/scripts/resource_watch.py).
- [Runner oficial das 19 suites](https://github.com/heavydevs/plan-and-execute/blob/6be46885ad691d3d43557a42fc2fd36a804b7eba/tools/run-skill-self-test.js).
- [CI do commit, run 36664762585](https://github.com/heavydevs/plan-and-execute/actions/runs/36664762585).

## Fontes consultadas

Consulta em 30 de setembro de 2026. Documentação, relatos dos autores dos experimentos e preprints; o tipo de evidência importa.

- **[S02]** [TypeSafe: API reference](https://docs.typesafe.ai/api).
- **[S06]** [TypeSafe: Confidence](https://docs.typesafe.ai/confidence).
- **[S08]** [TypeSafe: Python SDK usage](https://docs.typesafe.ai/sdk/python/usage).
- **[S29]** [Entagl Research: Jev evaluation, 2026-09-23](https://www.entagl.com/blog/typesafe-jev-benchmark-ai-decision-models).
- **[S30]** [JevAdvBench, preprint submitted 2026-09-25](https://arxiv.org/abs/2609.31142).
- **[S33]** [TypeSafe: Privacy Policy](https://typesafe.ai/legal/privacy-policy).
- **[S34]** [TypeSafe: Data Processing Agreement](https://typesafe.ai/legal/data-processing).
- **[S36]** [TypeSafe: Coding agents](https://docs.typesafe.ai/introduction/coding-agents).