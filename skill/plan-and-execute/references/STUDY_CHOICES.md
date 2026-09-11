# Complex-study choices

Read only when `ADAPTIVE_STUDY.md` classified the request as `complex` and at least one depth choice is still missing. This file owns the two user questions; `ADAPTIVE_STUDY.md` owns classification, evidence, synthesis, and review.

Complex requests use two user choices in a fixed order. **Ask only one choice per chat turn. Never combine the internal and external questions in one message.**

## Recommendation marker

Before presenting each missing choice, infer exactly one recommended option from the request and the evidence already visible without broad exploration. Append the literal suffix **`(recomendado)`** to that option's displayed label and to no other option.

The marker is advisory only:

- never preselect the recommended option;
- always require an explicit user selection;
- keep the underlying canonical value unchanged;
- strip/ignore the display suffix when recording the selected canonical value;
- do not add recommendation rationale unless the user asks for it.

Recommend internal depth using these rules:

- **Pacotes relacionados** when ownership is clear and the likely implementation/test surface is local;
- **Busca por palavras-chave em todo o workspace** when symbols, ownership, tests, or cross-package references must be located but a full-project read is unlikely to change the plan;
- **Projeto completo** when architecture, migration, security, data integrity, broad compatibility, or uncertain coupling makes project-wide understanding materially useful.

Recommend external depth using these rules:

- **Sem estudo externo** when repository evidence is sufficient and external facts are unlikely to change implementation or validation;
- **Pesquisa focalizada** when one or a few version/API/security/compatibility questions can materially change the plan;
- **Pesquisa ampla** when external uncertainty is broad, high-risk, rapidly changing, or the request explicitly requires broad research/comparison.

## Interactive choice UI

Before writing choice text, inspect the tools exposed by the current host. If a native interactive single-choice question tool exists, **use it** so the user can answer by clicking with the mouse. Do not render a duplicate Markdown/numbered choice list when the native tool call succeeds.

Host rules:

- **VS Code**: prefer the built-in `vscode/askQuestions` tool (also referenced as `#vscode/askQuestions` in VS Code prompt/tool contexts). Invoke it with exactly one question for the current turn and the three choices below as clickable **single-select** options.
- **Other hosts**: use an equivalent native single-choice/ask-user tool when one is actually exposed; do not invent a tool name or claim buttons exist when the host does not support them.
- Preserve the literal **`(recomendado)`** suffix in the clickable option label. If the native tool separately supports recommended-answer metadata/highlighting, use it too when safe, but the visible suffix is still required.
- The UI recommendation must not preselect or submit an option automatically. The user must click/select one choice explicitly.
- Do not enable multi-select for these two questions.
- Do not include free-text input as the primary response path when three clickable choices are supported.
- If the interactive tool is unavailable, disabled, or rejected by the host, fall back to the same question plus exactly three numbered text options. This fallback is the only case where the choice list should be written directly in chat.

## Choice 1 — internal study

If the request does not already determine the internal depth, present exactly one single-select multiple-choice question:

**Qual deve ser a profundidade do estudo interno do repositório?**

- **Pacotes relacionados** -> `related_packages`
- **Busca por palavras-chave em todo o workspace** -> `workspace_keywords`
- **Projeto completo** -> `full_project`

Append **`(recomendado)`** to exactly one of the three displayed labels according to the recommendation rules above.

Use the interactive-choice rules above. In VS Code, call `vscode/askQuestions` so the three options are clickable; otherwise use the host's equivalent native single-choice tool. Only if no such tool is usable, render this question with three numbered options in chat. Do not mention or preview the external-study question in this turn. End the turn after asking.

After the user selects an internal option, record it with `selection_source: user`. Do not start broad repository study yet if the external choice is still missing.

## Choice 2 — external study

Only after the internal choice is known, and only if the request does not already determine the external depth, present a second single-select multiple-choice question in a new chat turn:

**Qual deve ser a profundidade do estudo externo?**

- **Sem estudo externo** -> `none`
- **Pesquisa focalizada** -> `focused`
- **Pesquisa ampla** -> `broad`

Append **`(recomendado)`** to exactly one of the three displayed labels according to the recommendation rules above.

Again, use the interactive-choice rules above. In VS Code, call `vscode/askQuestions` so the three options are clickable; otherwise use the host's equivalent native single-choice tool. Only if no such tool is usable, render this question with three numbered options in chat. Do not repeat the internal question or its options. End the turn after asking.

After the user selects the external option, record it with `selection_source: user` and continue the adaptive study in that response.

## Already-specified choices

Resolve missing choices independently:

- if both choices are already explicit in the request, ask nothing;
- if only the internal choice is explicit, ask only the external question;
- if only the external choice is explicit, still ask the internal question first; after its answer, the external choice is already known, so continue without asking again;
- if the user explicitly requested broad/deep repository **and** internet study, treat that as `Projeto completo` + `Pesquisa ampla` and ask nothing.

Never ask both questions together for convenience, even when both are missing.
