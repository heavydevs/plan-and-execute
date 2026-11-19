# P064 — Roteamento por fase e contexto mínimo em todas as tasks

**Pesquisa arquitetural para implementação futura (2026-11-19).** Não é código/teste/revisão executada. Só carregar na task 119/120.

## 1. Problema

Diagnóstico: 014 (contexto), 028 (delegação/cache), 064 (telemetria), 087 (design forte/executor econômico) e 089 (evitar skill desnecessária) não impõem uma verificação universal por task/fase. Novo contrato aplica-se a 120 tasks e futuras, sem repetir estudo em cada arquivo.

## 2. Contratos

Arquitetura: task_context_router.py usa task_id, phase (study/design/implementation/validation/repair/review/handoff), hashes de source/reports, dependencies, affected_symbols, route floor e context packet curto. Índice do repositório, rg/AST/diff antes de abrir arquivos inteiros. Apenas estudo associado e referência de fase, um guia de provedor ativo; não carregar 32 pesquisas, 120 TODOs, transcrições ou logs de sucesso.

## 3. Estratégia

Roteamento: chamadas determinísticas para busca, seleção de testes, hashes, quota e monitoramento; economy low só para exploração localizada/edição mecânica validável; standard medium implementação limitada; strong high para arquitetura, depuração difícil e falha silenciosa; max fresh para revisão exigida. Preservar preferências, privacidade, autorização de custo, capability floor e root model. Escala por evidência, não tempo isolado.

## 4. Execução

Cache: prefixo curto, estável e versionado + sufixo da task, sem timestamps desnecessários; usar cache explícito apenas em SDK que realmente suporte e com ganho mensurado, mantendo isolamento de dados e vida útil. Não adicionar instruções só para exceder mínimo de cache. Cache de provider não equivale a economia faturada sem medição.

## 5. Riscos

Enforcement: novo checker de cada task valida route-per-phase, paths/hash/reason/trust/bytes/estimated-tokens, dependências atuais, contexto adicional justificado e ausência de segredo. Registrar motivos de exceção, custos e qualidade; não impor teto cego que retire contexto vital.

## 6. Validação

Invalidar apenas packets afetados por mudança no código, shared pattern, fonte ou contrato; falhas levam breve classe, mensagem atual, casos e path do log. Aprendizado de tentativa sem validação permanece hipótese. Switching usa handoff determinístico limitado e não transcrição.

## 7. Economia

Comparar baseline e candidato em fixtures de leitura simples, mecânica, arquitetura security, debug, troca de provedor e matriz de testes. Medir input real/estimado, cache read/write, chamadas, gasto real quando exposto, tempo, retrabalho e aceite; quality non-inferiority é gate. Unknown não vira economia inventada.

## 8. Limitações

Alternativas rejeitadas: ler a skill inteira em todo passo, chamar agente para grep, usar sempre modelo barato ou sempre máximo, concatenação de logs, caching como solução única. Referência detalhada TASK_CONTEXT_ROUTING.md só é carregada na fase aplicável; usar 119/120 para auditar todo o plano e futuras tasks.

## Fontes consultadas (páginas/capítulos abertos; nenhum livro integral alegado)

- https://developers.openai.com/api/docs/guides/prompt-caching
- https://abseil.io/resources/swe-book/html/ch11.html
- https://conf.researchr.org/details/ase-2025/ase-2025-papers/10/Do-LLMs-Generate-Useful-Test-Oracles-An-Empirical-Study-with-an-Unbiased-Dataset

Decisão: implementar **somente** o delta do plano existente; revisar no TODO 120 com agente independente e evidência de código real. Documentação não prova disponibilidade de créditos nem economias mensuradas.
