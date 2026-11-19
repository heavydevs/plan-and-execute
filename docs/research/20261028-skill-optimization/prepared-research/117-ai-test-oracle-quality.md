# P063 — Qualidade dos testes automatizados criados pela IA

**Pesquisa arquitetural para implementação futura (2026-11-19).** Não é código/teste/revisão executada. Só carregar na task 117/118.

## 1. Problema

Diagnóstico: 111/112 já implementará níveis por risco, seleção de impacto e E2E representativo; 109/110 corrige em lote e 113/114 protege refatoração de legados. Lacuna distinta: testes produzidos pela IA podem estar verdes com assert incorreto, alucinação de API, mocks irreais e cobertura sem detecção de defeito.

## 2. Contratos

Escolha: em cada comportamento mapear requirement_id, estímulo, partições/limites, resultado externo esperado, fonte do oráculo independente da implementação, camada mínima fiel, teste ID, fixture, risco e motivo de E2E exclusivo. Os próprios retornos do código atual não são o oráculo de verdade.

## 3. Estratégia

Testes parametrizados e property-based com seeds reproduzíveis para regras e limites; contracts/API/integração para autorização, persistência e fronteiras reais; E2E para jornada real, foco/erro acessível e comportamento navegador que nível inferior não prova. Evitar E2E por permutação de campos, sleeps cegos, ordem global e contagem fixa.

## 4. Execução

Test quality gate determinístico: compile/collect, símbolos reais, assertion significativa e negativa, teste novo alterado e impacted via 111, depois test-failure cycle 109. Para risco alto, seeded bug/mutação incremental limitada ou relação metamórfica verificável deve revelar ao menos um defeito; não executar mutação global em cada task. No reparo reproduzível, teste deve falhar antes e passar depois.

## 5. Riscos

Não usar assert True, verificação fraca de exists/status, snapshot não interpretado, produção mockada como integração, xfail/skip automático, alteração de expectativa só para ficar verde ou E2E redundante. Sem oráculo válido, escalar revisão do requisito/design, não inventar assert.

## 6. Validação

Teste adversarial: 45 regras de formulário com falhas parametrizadas, navegação E2E representativa; auth positiva/negativa real; mutante sobrevivente; retorno incorreto no código anterior; suite flaky; arquivo misto legado; teste com API inexistente; ausência de caso crítico. Preservar autorização 113 e suíte global final.

## 7. Economia

Economia: medir cobertura de comportamento/defeito real semeado, falsos verdes, flakiness, duração, bytes de prompt, tokens reais quando observáveis e revisão/retrabalho. Revisar oráculos de alto risco com modelo forte independente; scripts e edição mecânica com ferramenta/tier econômico. Nenhum benchmark de carga da aplicação é criado.

## 8. Limitações

Limites das fontes: Software Engineering at Google foi consultado em capítulos abertos, xUnit Test Patterns apenas conceitos citados em pesquisa 111 (não livro completo). Resultados acadêmicos sobre geração de oráculos e mutação não garantem ganhos universais para esta skill.

## Fontes consultadas (páginas/capítulos abertos; nenhum livro integral alegado)

- https://abseil.io/resources/swe-book/html/ch11.html
- https://abseil.io/resources/swe-book/html/ch12.html
- https://martinfowler.com/articles/practical-test-pyramid.html
- https://playwright.dev/docs/best-practices
- https://hypothesis.readthedocs.io/en/latest/
- https://stryker-mutator.io/docs/stryker-js/incremental/
- https://conf.researchr.org/details/ase-2025/ase-2025-papers/10/Do-LLMs-Generate-Useful-Test-Oracles-An-Empirical-Study-with-an-Unbiased-Dataset

Decisão: implementar **somente** o delta do plano existente; revisar no TODO 118 com agente independente e evidência de código real. Documentação não prova disponibilidade de créditos nem economias mensuradas.
