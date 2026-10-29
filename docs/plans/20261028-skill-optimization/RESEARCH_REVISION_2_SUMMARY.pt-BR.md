# Pesquisa aprofundada e validação do plano - revisão 2

Data:28/10/2026. Base de produto:0.11.0.

## Resultado

Os 32 relatórios foram refeitos. Foram comparadas 129 alternativas por tema, com 63 fontes primárias consultadas ou reconsultadas nesta rodada. A bibliografia acumulada contém 89 endereços distintos, representados por 121 registros de fontes antigas e atuais. Esses números documentam a cobertura; não provam um ótimo universal.

O plano permanece único, com86 tarefas de implementação/revisão,43 revisões independentes futuras e527 marcos retomáveis. Todos os TODOs permanecem pendentes. Nenhuma implementação foi executada nesta rodada.

## Principais refinamentos

- Comparar custo total por resultado validado, mantendo os limites de qualidade e segurança; delegar para vários modelos não é uma melhoria automática.
- Tratar esforço, modelo efetivo, ferramenta de execução, permissões e cobrança como dimensões separadas.
- Verificar cache e quota por geração, conta e modalidade, sem transportar regras de API para assinaturas.
- Manter monitoramento saudável determinístico e usar assessoria limitada somente para ambiguidades qualificadas.
- Separar identidade de capacidade da identidade de disponibilidade: trocar apenas quota, credencial referenciada ou caminho de log não é aumentar a inteligência.
- Definir precisamente entrada no fornecedor seguinte, repetição mecânica, reserva de tentativas, reset e passagem de contexto de uso único.
- Validar extração e fragmentos antes de resumir; distinguir sinais de vida de progresso semântico.
- Preservar recibos históricos e executar integração atual sem transformar resultados antigos em aprovações da árvore final.

## Validações reais

| Verificação | Resultado |
|---|---|
| Validação e auditoria nativas do plano | Aprovadas |
| Integração do estudo | Aprovada |
| Mapa e 172 vínculos de validação | Aprovados |
| Relatórios, hashes e vínculos dos 32 temas | Aprovados |
| Verificador de recibos |33 testes aprovados |
| Verificador de prontidão |17 testes aprovados |
| Tentativa de aceitar 001 sem implementação | Rejeitada corretamente |
| Conflitos entre escritores sem dependência | Zero |
|135 arquivos de produto comparados com a base | Nenhuma alteração |

Esses 50 testes validam os controles do plano, não as funcionalidades que serão implementadas. A suíte completa de produto não foi reexecutada nesta revisão de pesquisa.

## Prontidão

O plano está preparado e validado como especificação executável para a skill, com escopos, dependências, entradas futuras e testes declarados. Para executar em outra máquina, siga PORTABILITY.md e recrie o controle nativo para a raiz correta do repositório.

A execução real ainda depende de provedores permitidos instalados/autenticados e de revisores independentes. Neste ambiente, claude, codex e agy não foram encontrados. Não foram executados modelos autenticados, benchmarks reais de custo/qualidade ou testes de processo no Windows. Nenhuma revisão externa foi simulada.

## Onde ler

- Relatórios: docs/research/20261028-skill-optimization/prepared-research/INDEX.md
- Decisões desta revisão: prepared-research/REVISION2_DECISIONS.md
- Evidências: prepared-research/verification/revision2/RESULTS.json
- Plano nativo: .ai-work/20261028-skill-study-provider-switch/
- Checklist: docs/plans/20261028-skill-optimization/IMPLEMENTATION_CHECKLIST.md
- Regras detalhadas de troca: relatório 068-provider-switch-handoff.md

Não houve commit, push, instalação ou publicação. Os arquivos .git não fazem parte da entrega; a cópia local restaurada tinha metadados Git antigos. O código-fonte de produto continua na base 0.11.0.
