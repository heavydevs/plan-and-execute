# P065 — Arquitetura definitiva de UI/UX, design system e laboratório de protótipos

Data 2026-11-20. **Estudo e decisão para implementação futura; NÃO é implementação, revisão independente ou teste executado.** Leitura sob demanda somente nas tasks 121–126. O trabalho deve acontecer no plano ativo existente, sem outro orquestrador ou subplano.

## 1. Diagnóstico e decisões

O plano já tem roteamento de trabalho visual (024/025), revisão de segurança e performance (107/108), estratégia e seleção de testes (109–114) e roteamento/contexto enxuto (119/120), mas não uma fonte de verdade para identidade visual, componentes e UX, nem um caminho controlado para protótipos e aferição visual. Esses recursos são complementares; não duplicá-los.

**Decisão:** criar mecanismo especializado UI/UX opcional e progressivo na skill principal; uma subskill leve pode ser empacotada como ponto de descoberta somente onde o host beneficiar, compartilhando o MESMO runtime. Três contratos independentes, cada um seguido de review genuíno: (121/122) memória visual/design system; (123/124) protótipo opcional e importação/sync-plan; (125/126) UX e validação visual/acessível. A task 082 integra os três reviews, 086 permanece final.

**Design source-of-truth:** no projeto existente, decisões humanas explícitas + componentes/estilos REAIS aprovados prevalecem sobre protótipos, inspirações e inferência da IA; qualquer redesign exige aprovação. No greenfield, criar identidade visual provisória antes de código e pedir aprovação para adotá-la como padrão.

### Comparação fundamentada de opções

- **In-app/Storybook ou workbench nativo:** padrão recomendado quando há componentes existentes que funcionam isoladamente. Histórias reutilizam componentes verdadeiros, variantes, estados e testes de interação. Menos divergência com produção; não pressupor que Storybook já esteja instalado [S03–S05].
- **Subprojeto Node/Vite + HTML/JavaScript/SCSS:** oferecer mediante escolha explícita, especialmente quando o app é legado, pesado ou a pessoa quer explorar rapidamente páginas/fluxos. Vite oferece vanilla e pré-processadores Sass, instalado à parte [S06,S07]. Risco principal: duplicação, transposição errada de HTML para framework, custos de dependência e manutenção. Não gerar laboratório automaticamente onde workbench nativo resolve.
- **Figma MCP + Code Connect:** opcional quando conta/assento/conector já autorizados; associa componentes de design ao código real e reduz ambiguidade [S08,S09]. Não assumir disponibilidade, custo, nem conversão automática em produção [S10].
- **Screenshot isolado e troca obrigatória da biblioteca de componentes:** rejeitar. Screenshots não representam UX, semântica, foco ou contratos; respeitar tecnologia existente, licenças e acessibilidade.

Referências conceituais: Atomic Design (reuso e composição) [S01], princípios USWDS [S02], Nielsen [S13,S14]. O padrão DTCG 2025.10 define tokens portáveis com $type/$value, mas é relatório final da Community Group, NÃO recomendação W3C [S11]. Style Dictionary é opção de compilação, ainda não oferece suporte integral à especificação 2025.10 [S12]. Livros: sumários e trechos públicos de Designing Interfaces, Laws of UX e Designing with the Mind in Mind [S18–S20] — não alegar leitura integral.

## 2. Fluxo e API concretos

Entrada: intenção UX e consentimento -> design_context.py (descoberta e memória) -> ux_prototype.py (in-app ou lab opt-in) -> ux_review.py (evidência) -> planctl e roteadores EXISTENTES. Atividade backend sem UI deve carregar ZERO arquivo/skill/reviewer/browser novo. Novo projeto: perguntar uma vez se deseja identidade visual/protótipo; projeto existente: perguntar somente ao iniciar explicitamente auditoria ou criação de protótipo ou quando não há padrão definido. Nunca perguntar a cada feature.

Propor comandos do dispatcher oficial (bin/plan-and-execute.js), com script Python fixo de destino em vez de eval: pae ux init --new|--existing --mode auto|in-app|vite-vanilla|none; pae ux extract --scope PATH; pae ux prototype init --mode in-app|vite-vanilla; pae ux prototype import --scope PATH; pae ux audit --scope PATH; pae ux sync-plan --prototype PATH; pae ux validate --scope PATH; pae ux status. Nenhum comando deve instalar dependências, acionar Figma/pagamento, coletar dados privados ou gravar no frontend de produção sem consentimento. --yes só para scaffold local ESPECIFICADO, nunca aprovação de migração.

Dois caminhos:
A) frontend existente compatível: detectar routes/imports/componentes e usar histórias ou sandbox de componentes REAIS;
B) opt-in isolado: criar prototypes/ui-lab via template Vite com package.json, lockfile, localhost-only, index.html, pages/*.html, src/main.js, src/components/*.js, src/styles/main.scss, tokens SCSS GERADOS, src/mocks/*.json, README.md. Dependências fixadas/compatíveis, licenças conferidas, sem auth real, segredos, API de produção nem CDN não autorizado. Sem Node/browser: explicar modo documentação-planejamento, não sinalizar testes verdes.

## 3. Identidade visual e memória rápida para IA

Criar no repositório ALVO apenas após habilitar, com esquema explícito:

- docs/ui-ux/AGENT_INDEX.md (~2 KB): índice de UX para agentes; modo, status aprovado/provisório, referência de componentes e rotas; instrução para buscar somente trechos afetados. Em AGENTS.md já existente, eventualmente acrescentar somente link mínimo autorizado, nunca reescrever.
- docs/ui-ux/manifest.json (schema_version 1): enabled, mode, production_authority, framework, route_map, component_file_hashes (SHA-256), token_version, source_provenance/confidence, stale entries, approved_by/at explicitamente nulos até decisão real.
- docs/ui-ux/identity.md: audiência, principais jornadas, personalidade, cores, tipografia, espaçamentos, grid, radii, formas, imagens/licenças, microinterações, tom dos textos, temas, breakpoints, anti-patterns e pendências.
- docs/ui-ux/tokens.json (DTCG compatível, aliases e validação de ciclos); CSS custom properties/SCSS gerados da FONTE única; não manter dois conjuntos independentes.
- docs/ui-ux/components.json: path REAL/export, variantes, estados, props, feedback, loading/empty/error, acessibilidade/keyboard/ARIA, rotas consumidoras, last_source_hash e owner.
- docs/ui-ux/UX_PATTERNS.md: navegação, hierarquia, forms, rótulos, foco, tabelas, responsividade, mensagens, erros, acessibilidade e escolhas aprovadas.
- docs/ui-ux/decisions/*.md e evidence/: somente decisões validadas e artefatos redigidos sem segredo/dados sensíveis.

**Extração brownfield:** ler arquivo de dependências/framework, rotas, stylesheet/tokens e index de imports; executar rg/AST e ler 1–3 componentes relevantes; opcionalmente renderizar telas/estados autorizados com screenshots redigidos. Propor inventário com fonte/linha/hash, confiança e desconhecidos; preservar tudo que já funciona. Mudança de hash invalida só entradas afetadas, sem reestudo global. Não inferir "aprovado" de screenshot da IA.

**Greenfield:** brief pequeno (usuário principal, 2–3 tarefas-chave, identidade desejada, restrições e referências se fornecidas), 1 direção visual coesa com tokens semânticos + tela exemplar. Alternativas só quando explicitamente pedidas ou decisão ambígua. Usuário valida antes de padronizar.

## 4. Prototipação, importação e migração

- **Real -> protótipo:** input de routes/features limitado. Parser lê somente código e estilos autorizados; coleta componentes/estados/tokens/screenshot autorizados; sanitiza dados e gera mock. Salvar {real_path, real_export, baseline_sha256, prototype_path, state_ids, token_refs, provenance, fidelity_limitations}. Origem somente LEITURA, nunca autenticação real nem espelhamento de API.
- **Alterar protótipo:** iterar UX por jornada com coerência de tokens, sem assumir que código de lab é framework production-ready. Ter estados loading, error, empty, success, foco, responsividade, touch.
- **Protótipo -> produção:** pae ux sync-plan é apenas uma PROPOSTA com diff dos arquivos REAIS, mapeamento de componentes, decisões UX, impacto nos tokens, API contracts, testes necessários, screenshots antes/depois, riscos e rollback. Requer autorização explícita antes de disparar tasks de implementação com planctl nativo. Rejeitar SHA obsoleto, conflito, path traversal, symlink fora do workspace e cópia automática de HTML/SCSS em Next/React/Vue. Diferenças precisam ser reinterpretadas como componentes reais, não coladas cegamente.
- **Não criar segundo gerente:** toda task usa controles nativos, resource map, roteamento, quotas e protocolos de reviews já existentes.

## 5. Qualidade e aceitação

Gates objetivos e julgamento diferenciado:
1. Coerência visual: proporção, alinhamento, espaçamento, tipografia/hierarquia, cores/contraste, densidade, responsividade e padrão existente. Heurísticas NN/g para feedback do avaliador, com severidade e evidências; não equivalem a pesquisa com usuários [S13,S14].
2. Fluxos funcionais: tarefa real do usuário, rotas, estados, submit, erros, loading, mensagens, teclado, foco, screen-reader, conteúdo, redução de movimento.
3. Acessibilidade: objetivo WCAG 2.2 AA, inclusive rótulos, contraste, foco visível e tamanho/alvo acionável com exceções da norma [S15]. axe/Storybook/Playwright capturam apenas parte das falhas; review manual de teclado e semântica é obrigatório em interface crítica [S05,S16].
4. Visual regression: screenshot Playwright estabilizado (OS/browser/fonte, animação, data/locale) para componentes/telas MUDADOS, breakpoints e temas relevantes, contra golden aprovado [S17]. Diff não é automaticamente bug; update de baseline só após revisão. Nunca atualizar automaticamente para deixar CI verde.
5. Experiência e performance: verificar interações, estabilidade visual/layout shift e custos de assets; sem benchmarks obrigatórios de carga/performance sem pedido (R056 vigente) [S21].
6. Revisão estética: agente com capacidade visual e contexto limitado avalia screenshot + identidade e criticidade; mudança de marca/decisão subjetiva exige validação humana. Não confundir avaliação de IA com teste por usuário real. Respeitar permissão de envio de screenshot privado.

Testes unitários/contratos/histórias para ampla cobertura barata; Playwright visual/keyboard e axe direcionados; E2E apenas jornadas críticas. Task 111 escolhe escopo, 109 coleta todas falhas selecionadas e corrige focado; suite total global permanece somente no 082/084 depois da integração, com mesmo fingerprint final. Evidência: current code hash, navegador/viewport/tema, screenshot baseline/proveniência, interação falhada, axe, heurística, revisão humana quando houve, aprovação/pendências e custo real ou desconhecido. Sem "green" fictício.

## 6. Roteamento e economia de tokens

Detector determinístico para UX. Busca/indexação/token transforms/testes por scripts sem IA; extração ambígua -> modelo econômico qualificado; identidade/arquitetura complexa -> strong/high comprovadamente apto para visual com review; implementação simples -> modelo suficiente + testes, nunca economizar derrubando capability floor; review final -> independente max/fresh onde já exigido. Reusar routingctl, 024 e 119; considerar permissão, privacidade, quota e custo explícito. Prompt compacto contém {goal, route, current_hashes, approved_patterns, relevant_token_subset, affected_real_components, states, acceptance, image_refs, unknowns}; não ler todos designs, logs ou histórico. Prefixo cacheável apenas se suportado e ganhos medidos. Sem modelos periódicos para monitorar screenshots. Métricas: tokens, chamadas, tempo, retrabalho, qualidade; unknown não é zero.

## 7. Critérios negativos (testes adversariais)

A. Projeto existente com design bem documentado => preservar componentes e não abrir lab.
B. Projeto novo => identidade provisória e aprovação explícita.
C. App legado e opção Node => Vite/JS/SCSS isolado e assets locais.
D. Import route existente => mock sanitizado, nenhuma mutação em produção.
E. Fonte mudou depois do protótipo => bloquear sync-plan e propor reextrair só área afetada.
F. Novo botão/página com padrão aprovado => ler índice e componente afetado, não reestudar projeto.
G. Screenshot perfeito mas keyboard trap ou label ausente => falhar aceite.
H. Screenshot instável ou alteração deliberada => evidenciar e exigir aprovação do novo golden.
I. Task backend-only => zero overhead UX.
J. Figma indisponível/assinatura restrita/sem Node => modo opcional honesto, nunca sucesso falso.
K. Screenshot privado e nenhuma autorização de enviar a modelo => avaliação visual externa não acontece.
L. Contraste/foco/targets WCAG falham => bloquear gate até remediação.
M. Link/assets sem licença, paths com symlink ou segredos => rejeitar.
N. Não executar toda matriz browser E2E após cada pequena alteração.
O. Falta review independente real da task => não completar.
P. Ausência de autorização para alterar frontend real => sync-plan produz proposta, não código.

## 8. Contratos exatos de execução e ownership

121: design_context.py, uxctl.py, referências UI_UX_WORKFLOW.md e UI_UX_DESIGN_SYSTEM.md, ponte mínima no SKILL.md, teste ux_context_self_test.py; depende 025,120. 122 revisa em contexto independente final.
123: ux_prototype.py, template assets/ux-lab-template e UI_UX_PROTOTYPING.md, teste ux_prototype_lab_self_test.py; depende 122,112. 124 revisa.
125: ux_review.py, UI_UX_VALIDATION.md, integração fixa em bin/plan-and-execute.js, teste ux_visual_acceptance_self_test.py + cli; depende 124,108,110. 126 revisa.
Reviews 122/124/126 são bloqueadores de 082 e 086 continua último. Não alterar main, skills instaladas, config global ou testes legados sem autorização.

## 9. Referências consultadas, escopo e limitações (2026-11-20)

[S01] Brad Frost, Atomic Design, capítulo público: https://atomicdesign.bradfrost.com/chapter-2/
[S02] U.S. Web Design System princípios e componentes: https://designsystem.digital.gov/design-principles/
[S03] Storybook isolado: https://storybook.js.org/docs/get-started/why-storybook
[S04] Storybook interaction: https://storybook.js.org/docs/writing-tests/interaction-testing
[S05] Storybook acessibilidade/visual: https://storybook.js.org/docs/writing-tests/accessibility-testing ; https://storybook.js.org/docs/writing-tests/visual-testing
[S06] Vite vanilla: https://vite.dev/guide/
[S07] Vite Sass/SCSS: https://vite.dev/guide/features.html#css-pre-processors
[S08] Figma MCP: https://developers.figma.com/docs/figma-mcp-server/
[S09] Figma Code Connect e permissões: https://developers.figma.com/docs/figma-mcp-server/code-connect-integration/
[S10] Figma MCP não é tradutor 1 clique: https://help.figma.com/hc/en-us/articles/39252411778583-Figma-MCP-server-FAQs
[S11] Design Tokens 2025.10 Community Group: https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/
[S12] Style Dictionary suporte parcial: https://styledictionary.com/info/dtcg/
[S13] Nielsen Norman Group 10 heurísticas: https://www.nngroup.com/articles/ten-usability-heuristics/
[S14] Limites heurística versus pesquisa de usuários: https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/
[S15] WCAG 2.2: https://www.w3.org/TR/WCAG22/
[S16] Playwright a11y limitações: https://playwright.dev/docs/accessibility-testing
[S17] Playwright screenshot baseline: https://playwright.dev/docs/test-snapshots
[S18] Tidwell, Brewer, Valencia, Designing Interfaces 3e, sumário/apresentação públicos, NÃO livro integral: https://www.oreilly.com/library/view/designing-interfaces-3rd/9781492051954/
[S19] Jon Yablonski, Laws of UX 2e, sumário/trechos públicos, NÃO livro integral: https://lawsofux.com/book/
[S20] Jeff Johnson, Designing with the Mind in Mind 2e, sinopse editorial, NÃO livro integral: https://shop.elsevier.com/books/designing-with-the-mind-in-mind/johnson/978-0-12-407914-4
[S21] web.dev Web Vitals: https://web.dev/articles/vitals
[S22] OpenAI guidance skills com progressive disclosure: https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md

Fontes verificam técnicas e contratos, não execução por este agente, rankings de modelo, economias reais ou teste com usuários. Revisões, implementação e validação visual só poderão ser marcadas depois de realizadas no projeto de destino.

