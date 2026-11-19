# P061-P062 — Recuperação de cotas e retomada automática

**Pesquisa arquitetural para implementação futura (2026-11-19).** Não é código/teste/revisão executada. Só carregar na task 115/116.

## 1. Problema

Diagnóstico: 022 e 074 já cobrem quota/cooldown/fallback; 103 tem scheduler opt-in para keepalive, mas não há contrato para voltar ao fornecedor preferencial depois do reset nem retomada automática se todos esgotarem. Complementar controladores existentes, sem criar segundo roteador.

## 2. Contratos

Persistência: ledger por provider, auth-profile ID não secreto, quota_pool, modelo, esforço e janela, com observed_at, error_class, retry_after, next_probe_at, policy_fingerprint e last_success. Separar quota temporária, limites de faturamento, autenticação, política e indisponibilidade de rede. Reset desconhecido permanece unknown; proibir token/segredo em ledger.

## 3. Estratégia

Despacho: a cada task nova sem worker ativo reordenar candidatos por preferência do usuário, capability floor, restrições de dados, preço autorizado e disponibilidade vigente. A expirou cooldown = candidato a recheck, não prova créditos. Quando A volta e B executa, B termina sua task; próxima task elegível vai para A. Pinned e fallback-disabled continuam rígidos.

## 4. Execução

Ausência total: registrar PAUSED_QUOTA, current task/checkpoint, plan generation e única próxima verificação, agendada como one-shot no scheduler nativo reutilizado de 103/104 (independentemente do número de tasks). Lease+CAS impedem despertar duplo; validar fingerprint, status, cancel e fonte antes de retomar. Host desligado ou scheduler indisponível = manual_resume_required explícito; não prometer auto-wake impossível.

## 5. Riscos

Não usar prompts pagos como sondas. Preferir respostas já recebidas e metadados locais não pagos; respeitar Retry-After validado; em reset desconhecido usar backoff limitado com jitter, orçamento e diagnóstico explícito. SDK/CLI podem ocultar saldo; não alegar leitura de créditos não observável. Numa verificação que custaria tokens, aguardar despacho autorizado.

## 6. Validação

Segurança: ação de scheduler com caminho validado, proprietário, ID estável, fence da geração; nunca desativar políticas, salvar credenciais, inferir créditos financeiros recuperáveis, executar dois trabalhadores simultaneamente ou preemptar validação ativa. Cancel/reset/conclusão remove só o job da skill.

## 7. Economia

Fixtures: A>B>C com A quota e retorno a A; todos 429; pools separados; retry-after inválido; billing e auth; clock falso; crash/reboot e timer duplicado; plano cancelado; host sem scheduler; cadeia pinned e privacidade; overhead e zero paid poll. Medidas de saldo real e host físico ficam não verificadas.

## 8. Limitações

Roteamento/token: leitura somente de availability.py, keepalivectl.py, run_isolated.py, planctl.py e símbolos relacionados. Ferramenta local para status/agendamento; agente strong/high na concorrência e segurança; revisão independente max; prefixo curto e handoff hash-bound. Pesquisa não entra nos prompts de outras tasks.

## Fontes consultadas (páginas/capítulos abertos; nenhum livro integral alegado)

- https://platform.claude.com/docs/en/api/rate-limits
- https://developers.openai.com/api/docs/guides/rate-limits
- https://www.rfc-editor.org/rfc/rfc6585
- https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
- https://docs.temporal.io/tasks

Decisão: implementar **somente** o delta do plano existente; revisar no TODO 116 com agente independente e evidência de código real. Documentação não prova disponibilidade de créditos nem economias mensuradas.
