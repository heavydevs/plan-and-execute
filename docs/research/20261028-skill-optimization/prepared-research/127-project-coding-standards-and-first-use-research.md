# P066 — Padrões de código, reuso e onboarding de agentes, com UX sob demanda

Data: 2026-11-20. Escopo: arquitetura para implementação futura dentro de heavydevs/plan-and-execute, branch checkpoint/plano1-estudo-provider-switch-20261028. Pesquisa primária, estudos, documentação de agentes e padrões de engenharia. **Este documento NÃO é implementação, benchmark executado, teste ou revisão independente.**

## 1. Problema, decisão e resultados esperados

Problema observado: um projeto usa entidades Jakarta Persistence/JPA, Hibernate e repositories na maioria dos endpoints, mas um novo endpoint feito pela IA usa JDBC manual; em outros contextos a IA duplica utilitários, troca bibliotecas e cria pacotes, nomes, DTOs ou tratamento de erros incompatíveis com o restante. Falta um contrato contextual que relacione padrões aprovados, código real e tarefas futuras.

Decisão: integrar uma capacidade opcional **Project Conventions** na skill atual, NÃO instalar outro agente, índice de nuvem ou framework de planejamento. Ela (1) oferece configuração apenas na primeira utilização significativa no projeto ou via comando, (2) faz uma investigação do código real e melhores práticas contemporâneas somente nessa ativação/refresh permitido, (3) cria documentos compactos específicos para IA, com mapa de arquivos, regras, fontes e trechos de exemplo, (4) localiza e reutiliza padrões antes de cada implementação, e (5) verifica desvios de arquitetura, naming, dependências e helpers no diff. A capacidade UX 121–126 deve compartilhar o gate de primeiro uso, sem fazer levantamento profundo em cada nova funcionalidade.

Critérios: preservar projetos maduros e escolhas legítimas; não transformar uma hipótese em regra; não exigir JDBC/ORM/arquitetura particular em todo projeto; permitir exceções justificadas; priorizar testes já existentes e análise estática determinística; somente medir economia de tokens quando houver dados reais.

## 2. Comparação fundamentada das abordagens

**Apenas AGENTS.md/CLAUDE.md:** simples e multiplataforma, porém pode crescer indefinidamente, divergir entre provedores, carregar texto irrelevante e não detectar automaticamente violações. Codex tem regras AGENTS.md por ancestralidade/escopo e limite de conteúdo; Claude usa CLAUDE.md e regras por arquivos; Gemini CLI hierarquiza GEMINI.md; Copilot e Cursor têm regras por globs. Assemelham-se, mas não têm resolução de escopo/limites idênticos [S01–S06]. Não duplicar a especificação em cinco formatos; manter fonte canônica e permitir pontes mínimas exportáveis somente com consentimento.

**Skill reutilizável + disclosure progressivo:** Agent Skills descreve metadados na descoberta, instruções completas na ativação e referências/scripts sob demanda. Aplicável aqui; usar referências lazy e um índice curto, não ler relatórios ou histórico em cada execução [S07].

**Somente ferramentas de lint/format:** excelente para padrões mecânicos, insuficiente para identificar que o projeto usa ORM em operações CRUD, reutiliza um helper ou exige DTOs específicos. ArchUnit (regras de dependência Java), ESLint, Semgrep e OpenRewrite podem complementar, mas nunca devem ser instalados ou ativados sem validar suporte/licença/impacto e consentimento. Transformações amplas são propostas separadas [S14–S17].

**Mapeamento de arquitetura/decisões + evidência de código + gates:** escolhido. Registrar decisões pequenas e motivadas, preservar ADRs históricos [S13]; consultar exemplos reais no módulo e rodar guardas específicos para risco do diff. Preferência por consistência é compatível com as orientações de code review do Google [S12].

**Resultados científicos contraditórios:** Gloaguen et al. (2026, arXiv:2602.11988) encontraram custo de inferência >20% maior e ausência de benefício robusto com instruções; Khatri (ACL REALM 2026) não encontrou mudança de acurácia mensurável em 17 tarefas/288 execuções; outro estudo observacional de 124 PRs reporta melhora em duração e output tokens; Shepard/Albrecht reportam ganho em cenário de tuning e modelo específico; Shanto et al. analisaram 3.387 documentos de instrução e divergência entre formatos. Portanto não prometer economia: benchmark local com/sem índice e gates, memória curta e métricas reais ou “unknown” [S08–S11].

## 3. Bootstrap uma vez por projeto — contrato comum com UX

Criar controlador local leve project_onboarding.py, sem execução de modelo, capaz de identificar projeto/módulo e detectar arquivo de estado fora dos diretórios de plano descartáveis. Chave segura baseada no git common-dir + root real + escopo, não apenas nome da pasta (suportar worktrees, monorepos, sem-Git). Não armazenar identidade pessoal ou caminho absoluto no documento distribuído. Estado atômico/lock/CAS, schema version, tópicos independentes coding e ux, status unseen/offered/deferred/declined/approved/ready/stale/unsupported, origem da autorização, timestamp, manifesto e escopos.

No **primeiro uso significativo da skill num repositório de software**, oferecer uma pergunta curta, com decisão separada por tópico: “Deseja analisar o código existente e criar documentação de padrões para IA? Sim / Depois / Não. Também preparar UX/design? Sim / Depois / Não.” Mostrar UX só se for aplicável, por detecção barata de frontend. Um Sim autoriza estudo do escopo escolhido, não instalação de bibliotecas nem envio irrestrito de código. Não perguntar em status, cancel, reset, comandos triviais, CI, execução headless ou sem TTY; nesses ambientes defaults seguros e nenhum bloqueio. Recusa persiste; Depois não inicia pesquisa e só permite próximo aviso numa utilização futura relevante. Init e refresh explícitos têm prioridade sobre recusa anterior, mas ainda respeitam permissões/privacidade. Aprovado/pronto não volta a perguntar.

Não executar pesquisa externa, reindexação integral, navegador ou modelo pago implicitamente a cada task. Ao abrir nova task UX: somente consultar índice aprovado e exemplos afetados; se não existe aprovação, UX permanece off (sem rebrand). Node prototype continua decisão separada e explícita, nunca consequência automática de aceitar UX.

## 4. API CLI planejada e documentação de uso

Comandos públicos via binário existente pae / plan-and-execute, com --repo, --scope, --json, --dry-run, --help, exit codes e validação de argv. Todas as rotas devem entrar no help e README inglês e pt-BR quando a task implementar:

    pae standards status [--repo .] [--json]
    pae standards init [--repo .] [--scope services/api] [--dry-run]
    pae standards refresh [--repo .] [--scope services/api] [--dry-run]
    pae standards explain --path services/api/src/... --intent persistence [--json]
    pae standards check --changed services/api/src/... [--json]
    pae standards export-instructions --target codex|claude|gemini|copilot|cursor [--dry-run]
    pae ux init [--repo .] [--dry-run]
    pae ux refresh [--scope web] [--dry-run]
    pae ux status [--repo .] [--json]
    pae onboarding status [--repo .] [--json]

Status, explain e check: só código/índice local pertinente; sem pesquisa. Init: censo inicial + estudo de práticas atuais autorizado. Refresh: apenas escopo relevante e eventual consulta de fontes atuais, sempre explícita; nunca substituir decisão aprovada sem revisão. Export-instructions gera diff e opt-in por fornecedor, não sobrescreve AGENTS.md, CLAUDE.md, GEMINI.md, regras Copilot ou Cursor preexistentes. Comando não deve alterar funcionalidades legadas ou exigir novo runtime da skill.

## 5. Estudo inicial: repositório e práticas atuais

**Censo barato determinístico:** identificar módulos, manifests e versões (pom.xml/Gradle, package.json/locks, pyproject, go.mod etc.), configurações lint/formatter, .editorconfig, testes, CI, docs e instruções existentes; filtrar .gitignore, vendor, dist, build, coverage, generated, secrets, .env e binários. Não assumir que lib declarada é efetivamente utilizada. Restringir tamanho, tipos, diretórios e caminhos, sempre verificar realpath/symlinks.

**Mapa semântico e amostras representativas:** por módulo, escolher 2–5 fluxos equivalentes à intenção comum: Resource/Controller → Service → Repository/DAO → Entity/DTO → mapper → testes/config. Identificar bibliotecas usadas em imports, transações, auth, logging, validação, DTOs, exceptions, paths/pacotes por feature ou camada, naming, utilitários/helpers, serializers e contratos de resposta. Ferramentas de repositório (git/rg) primeiro; símbolos, AST/Tree-sitter, LSP ou índices opcionais somente se já disponíveis. Registrar caminho relativo, símbolo, método, assinatura, hash SHA-256 e regra demonstrada.

**Classificar por evidência:** (A) explícito e aprovado; (B) padrão repetido em código atual; (C) exemplo isolado/inferido; (D) legado a evitar; (E) boa prática externa candidata. Conflitos entre módulos são resolvidos por escopo; entre estilo aprovado e amostra divergente são submetidos à decisão. Linter atual e ADR aprovado têm prioridade sobre inferências; normas de segurança superioras prevalecem. Não tornar mudanças recomendadas pela internet obrigações silenciosas. Consultar docs atuais da versão realmente instalada apenas no init/refresh autorizado; registrar URLs, data, versão e limites. Sem web: classificar como “externo não verificado”, não inventar verificação.

**Greenfield:** sem fonte relevante gera guia provisório de organização e tecnologias escolhidas pelo usuário, nunca “approved” artificial. Produzir proposta de decision log e opções; só depois de validação e aceite estabelecer padrão.

## 6. Documentação permanente PARA agentes, não um romance

Arquivos canônicos gerados após autorização em docs/ai-standards/ do projeto destino:

- AGENT_INDEX.md: ~1–2 KiB, mapa de módulos, regras de prioridade e links on-demand; carregamento inicial mínimo.
- manifest.json: schema_version, decisões e status, paths/símbolos/fingerprints, fontes, escopos, timestamps, conflitos e revisões.
- TECH_STACK.md: por módulo, linguagem, libs, versões, status declarada/usada e restrições de alternativas.
- ARCHITECTURE.md: árvore de módulos e pacotes, camadas e limites, onde fica classe utilitária/shared, serviços e APIs.
- CODING_RULES.md: naming, packages, DTO, mappers, transactions, auth, exceptions, logging, validar testes e critérios de exceção, com ID, severidade, scope, approval, evidence.
- REUSE_CATALOG.json: helpers, classes base, interfaces, SDKs, services, repositories, scripts, símbolos/caminhos e hashes.
- modules/<modulo>.md: detalhes e 1–3 exemplos reais por intenção: CRUD, paginação, erros, mapping, queries, etc.
- decisions/ADR-*.md: decisões curtas, contexto, opções, motivo, consequências e supersession, nunca apagar histórico.
- evidence/ (opcional): relatório de estudo completo, fora do carregamento padrão.

Uma fonte de verdade. Instruções de fornecedor exportadas são pontes breves para índice e comandos, não cópias independentes. Hierarquia: usuário/política atual > decisões explícitas aprovadas > padrão específico do módulo > exemplo atual > prática geral verificada > sugestão da IA. Arquivo gerado sem aprovação permanece inferred/provisional, jamais bloqueio incondicional.

## 7. Integração “pattern-first” antes da implementação e review

O roteador de contexto 119/120 recebe módulo, intenção e arquivos afetados; o resolvedor de padrões devolve pacote pequeno: rule_ids + status/aprovação/fingerprint, até 3 exemplos próximos com símbolo/path, bibliotecas instaladas **e usadas**, helpers existentes, testes pertinentes, riscos de segurança/performance e dúvidas. Não ler documento amplo em toda task, nem importar texto de outras áreas.

Perguntas obrigatórias no design de uma feature: existe funcionalidade equivalente? há abstração/helper a reutilizar? quais bibliotecas efetivamente adotadas neste módulo? onde colocar classes/pacotes/naming? como o sistema trata erros/segurança/transações? por que uma alternativa nova é necessária? quais testes a validam? O gerador de código respeita padrão aprovado, e o reviewer examina o DIFF real e os contratos atuais. Se migração técnica é desejável, produzir proposta/ADR separada; não refatorar código legado acidentalmente.

**Exemplo JPA/JDBC:** identificar versão e módulo (Jakarta JPA Hibernate, Spring Data ou Quarkus Panache), várias entities @Entity, services e repositories. Novo CRUD equivalente deve reutilizar ORM/repository e estratégias existentes. Importações novas de java.sql.Connection, DriverManager, PreparedStatement, JDBC manual ou JdbcTemplate onde o contrato diz “CRUD em ORM” disparam finding architectural-drift, com comparação a endpoints e dependências reais. Não confundir driver JDBC interno do ORM com opção de escrita de SQL manual; não banir SQL nativo ou JDBC em batch/queries complexas com decisão aprovada, motivo, medição e testes. As documentações oficiais mostram que frameworks ORM podem coexistir com JDBC e consultas SQL nativas [S18–S21].

Guardas: regra approved + verificação objetiva -> bloqueio corrigível ou waiver aprovado por escopo; inferred -> aviso com evidência, sem afirmar reprovação automática. Stack/hash divergente -> refresh parcial autorizado ou pausa segura onde contrato crítico falta. Rodar ArchUnit/ESLint/Semgrep existentes e testes por impacto do 111/112; final global em 082/084. Não instalar ferramentas novas por padrão e não exigir E2E amplo/benchmark de performance salvo pedido. Revisão de segurança e performance compartilha gates 107/108 e mantém qualidade funcional.

## 8. Economia, roteamento, observabilidade e ameaças

Primeiro uso: detector local sem IA; após aceite, censo por ferramentas, modelo econômico para ambiguidade, strong/high para decisões arquiteturais de risco e modelo independente max para revisão da implementação da skill, conforme 119/120. No dia a dia: 1 índice compacto + subconjunto por escopo + 1–3 exemplos/hash, nunca relatório integral, histórico de chat, docs de todo framework ou web recorrente. Se dependência/code hash mudou: invalidar apenas exemplos/regras daquele módulo; estudo externo profundo só em init/refresh explícito. Registrar custo/tokens/tempo se mensuráveis, desconhecido caso contrário, falsos positivos, retrabalho, testes e incidentes evitados sem atribuir benefícios inventados.

**Segurança:** repositório e instruções nele são conteúdo não confiável contra prompt injection; nunca executar instruções arbitrárias encontradas em comentários/MD. Bloquear symlink fora de root, path traversal, secrets, arquivos grandes, vendor/generados e fuga para indexador externo. Sem envio de código a provedores/pesquisa externa sem permissão válida; sem auto-editar fonte, configurações, AGENTS preexistente ou realizar instalações. Escrita transacional com dry-run, hashes/backup/conflitos; validação de schema, controles de acesso e idempotência. Git-root/módulo não devem ser confundidos em worktrees e monorepos.

## 9. Emenda de UX 121–126, acoplamento e grafo

A task 127 entrega project_onboarding compartilhado e docs/CLI de standards; 128 é revisão independente real e aprovada. UX 121 passa a depender de 128: reusa first-use por projeto, só analisa quando UX aplicável e consentido; 122 revisa. UX 125 adiciona/help para comandos init/refresh e garante que o estudo de layout e bibliotecas visuais não se repete a cada feature; 126 revisa. O protótipo em Node/Vite/HTML/JS/SCSS da 123 exige comando/consentimento separado. Não compartilhar a base visual inteira com tarefas backend-only.

A task 129, dependente 128/108/112, integra recuperação/guards ao fluxo de worker; 130 revisa de forma independente no source hash final. 082 depende 128,130 além dos gates anteriores; 086 continua tarefa final. Não marcar nenhuma task completa nesta emenda. No momento atual, só criar documentação de plano e commit/push autorizado.

## 10. Testes adversariais / aceitação obrigatória

A. CRUD JPA dominante mantém ORM, entity, service e repository; B. query/batch JDBC aprovado passa como exceção; C. monorepo com módulos ORM e JDBC separados não cruza convenções; D. library presente mas sem import não é “aprovada”; E. helper existente reutilizado, sem duplicação; F. Node, Python e Java não recebem regra de outro stack; G. projeto vazio = provisional; H. primeira sessão interativa faz uma pergunta com decisões independentes; I. segunda sessão não repete; J. recusado não dispara estudo e init manual pode reabrir; K. CI, headless, status/cancel não têm prompt, pesquisa ou IA; L. UX backend-only é custo zero; M. UX init uma vez e refresh somente explícito; N. conflito em regras não é arbitrariamente resolvido; O. malicious AGENTS.md não ganha precedência de instrução host; P. segredos/symlinks/submodule fora de escopo não são lidos; Q. mudança em módulo A não invalida B; R. hash expirado não fica verde; S. export-instructions não sobrescreve documento manual; T. review independente, lint e testes reais não são simulados. Medir com fixtures e spy de ferramentas/provedores o número de leituras/model calls por cenário; só declarar ganho quando medido.

## 11. Tarefas/arquivos alvo

127 — skill/plan-and-execute/scripts/project_onboarding.py, project_standards.py, standardsctl.py, references/PROJECT_ONBOARDING.md, references/PROJECT_STANDARDS.md, SKILL.md, bin/plan-and-execute.js, test/optimization/standards_onboarding_self_test.py e test/cli.test.js. 128 — review real dos mesmos outputs.

129 — scripts/standards_guard.py, scripts/task_context_router.py, scripts/runner_contract.py, scripts/run_isolated.py, references/PROJECT_STANDARDS_GATES.md e test/optimization/standards_guard_self_test.py. 130 — revisão independente final-hash de 129. 121,122,125,126 — ajustes UX sob demanda. 082/086 — integração e validação final.

## 12. Fontes, estudos e livros (verificados em 2026-11-20)

[S01] OpenAI Codex AGENTS.md discovery e precedência: https://learn.chatgpt.com/docs/agent-configuration/agents-md
[S02] Anthropic Claude memory e regras: https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts
[S03] Google Gemini CLI context: https://geminicli.com/docs/cli/gemini-md/
[S04] GitHub Copilot repository/path instructions: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
[S05] Cursor project rules: https://cursor.com/docs/rules
[S06] Codex guia SKILL e AGENTS: https://learn.chatgpt.com/docs/customization/overview
[S07] Agent Skills, progressive disclosure: https://github.com/agentskills/agentskills
[S08] Gloaguen et al., Evaluating AGENTS.md (2026): https://arxiv.org/abs/2602.11988
[S09] Khatri, Do Context Files Help Coding Agents? (ACL REALM 2026): https://aclanthology.org/2026.realm-1.5/
[S10] Shepard/Albrecht, Probe-and-Refine Tuning (2026): https://arxiv.org/abs/2606.20512
[S11] Shanto et al., instruction-file consistency (nov/2026): https://arxiv.org/abs/2611.02383
[S12] Google Code Review, design/consistency/old code: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[S13] Martin Fowler, Architecture Decision Record (mar/2026): https://martinfowler.com/bliki/ArchitectureDecisionRecord.html
[S14] ArchUnit architecture tests: https://www.archunit.org/userguide/html/000_Index.html
[S15] ESLint configs e regras: https://eslint.org/docs/latest/use/configure/
[S16] OWASP Semgrep: https://devguide.owasp.org/en/05-implementation/05-static-analysis/01-semgrep/
[S17] OpenRewrite recipes e “Do no harm”: https://docs.openrewrite.org/concepts-and-explanations/recipes ; https://docs.openrewrite.org/authoring-recipes/recipe-conventions-and-best-practices
[S18] Quarkus Panache repository e entity: https://quarkus.io/guides/hibernate-orm-panache/
[S19] Quarkus Hibernate ORM: https://quarkus.io/guides/hibernate-orm/
[S20] Spring Data JPA query methods e queries nativas: https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html
[S21] Spring Data JPA transactions: https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html
[S22] Tree-sitter parser incremental: https://github.com/tree-sitter/tree-sitter
[S23] Universidade de Bamberg, estudo de 124 PRs: https://extern.fis.uni-bamberg.de/en/entities/researchdata/fad7bdfe-c39e-41d9-9540-80b703a02ea2/
[S24] Livro: Michael Feathers, Working Effectively with Legacy Code, Prentice Hall, 2004; referência conceitual, não texto integral.
[S25] Livro: Martin Fowler, Refactoring (2nd edition), Addison-Wesley, 2018; referência conceitual, não texto integral.
[S26] Livro: Winters, Manshreck & Wright, Software Engineering at Google, O'Reilly, 2020; referência conceitual, não texto integral.

Não extrapolar os estudos a todos os agentes; relatórios de fontes provam o estudo, NÃO a performance do código ainda não escrito.
