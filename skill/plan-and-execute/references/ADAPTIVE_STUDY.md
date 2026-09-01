# Adaptive study protocol

Use this file only before planning. Read `ARTIFACT_WRITING.md` first. The goal is enough evidence to choose correct architecture, TODO boundaries, risks, and validation — not a research transcript.

## 1. Classify before broad repository inspection

Choose `simple`, `medium`, or `complex` from the request and immediately visible risk signals.

### Simple

Use when the change is direct, low-risk, locally scoped, and version/architecture uncertainty is unlikely to change the implementation. Internal/external study may be `none`; record one precise skip reason.

### Medium

Use when bounded repository discovery improves confidence. Automatically choose:

- `related_packages`: inspect the target package plus direct tests/dependencies; or
- `workspace_keywords`: search symbols/keywords across the workspace, then open only high-signal matches.

Use focused external research only for a material trigger such as version-sensitive behavior, unfamiliar API semantics, compatibility, security, or unclear external contract.

### Complex

Use when architecture, migration, security, compatibility, data integrity, ownership, or another high-impact uncertainty can materially change the plan.

Complex requests use two user choices in a fixed order. **Ask only one choice per chat turn. Never combine the internal and external questions in one message.**

#### Choice 1 — internal study

If the request does not already determine the internal depth, present exactly one single-select multiple-choice question:

**Qual deve ser a profundidade do estudo interno do repositório?**

- **Pacotes relacionados** -> `related_packages`
- **Busca por palavras-chave em todo o workspace** -> `workspace_keywords`
- **Projeto completo** -> `full_project`

Use the platform's native single-choice UI when available. Do not use a free-form question when a choice UI is supported. If no native choice UI exists, render only this question plus the three numbered options and ask the user to select exactly one. Do not mention or preview the external-study question in this turn. End the turn after asking.

After the user selects an internal option, record it with `selection_source: user`. Do not start broad repository study yet if the external choice is still missing.

#### Choice 2 — external study

Only after the internal choice is known, and only if the request does not already determine the external depth, present a second single-select multiple-choice question in a new chat turn:

**Qual deve ser a profundidade do estudo externo?**

- **Sem estudo externo** -> `none`
- **Pesquisa focalizada** -> `focused`
- **Pesquisa ampla** -> `broad`

Again, use the platform's native single-choice UI when available; otherwise render only this question plus the three numbered options and require exactly one selection. Do not repeat the internal question or its options. End the turn after asking.

After the user selects the external option, record it with `selection_source: user` and continue the adaptive study in that response.

#### Already-specified choices

Resolve missing choices independently:

- if both choices are already explicit in the request, ask nothing;
- if only the internal choice is explicit, ask only the external question;
- if only the external choice is explicit, still ask the internal question first; after its answer, the external choice is already known, so continue without asking again;
- if the user explicitly requested broad/deep repository **and** internet study, treat that as `Projeto completo` + `Pesquisa ampla` and ask nothing.

Never ask both questions together for convenience, even when both are missing.

## 2. Search first, read second

Repository study:

1. locate candidate files/symbols/tests;
2. rank by likely effect on the request;
3. open focused files/ranges;
4. inspect direct dependencies/contracts/tests only when they can change planning;
5. widen scope only when discovered coupling justifies it.

Do not read the entire workspace merely because it is available.

External study:

- prefer primary/official docs, standards, release notes, papers, or authoritative technical sources;
- capture title/publisher/version/date/URL plus the conclusion that changes the plan;
- do not paste articles or long quotes into study state.

## 3. Record evidence, not process

One internal source:

```json
{
  "id": "I001",
  "location": "src/auth/token.py:88-121",
  "finding": "Refresh tokens expire after 30 days and reuse the common token parser.",
  "planning_impact": "The refresh TODO must preserve the 30-day contract and modify the common parser path."
}
```

One external source:

```json
{
  "id": "E001",
  "title": "...",
  "publisher": "...",
  "url": "https://...",
  "version_or_date": "2026-08-20",
  "why_authoritative": "Official vendor documentation for the API used by this repository.",
  "finding": "The cursor becomes invalid after 24 hours.",
  "planning_impact": "Tests must cover cursor expiry and the retry path must not reuse expired cursors."
}
```

Do not record:

- search queries;
- dead ends that do not affect a decision;
- generic framework knowledge;
- verbose explanation of how the finding was discovered.

## 4. Material questions

A material question exists only when its answer can change architecture, requirement interpretation, task decomposition, compatibility, risk, or validation.

```json
{
  "id": "Q001",
  "question": "Does API v2 still accept the legacy cursor format?",
  "importance": "high",
  "status": "resolved",
  "resolution": "Vendor v2 rejects legacy cursors with HTTP 400.",
  "planning_impact": "Add a migration boundary before enabling v2 pagination.",
  "evidence_ids": ["E001"]
}
```

Do not turn curiosity into a material question. Resolve high-impact uncertainty before autostart.

## 5. Synthesis

Schema-v2 synthesis keeps only planning inputs:

- `planning_constraints`;
- `derived_requirements`;
- `risks`;
- `validation_implications`;
- `unresolved_questions`;
- `ready_for_planning`;
- `stopping_reason`.

Each list item is one atomic statement. Prefer path/symbol/source ids over repeating evidence text.

Stop when additional evidence is unlikely to change:

- architecture/compatibility decision;
- requirement inventory;
- TODO/context boundaries;
- material risk;
- deterministic validation strategy.

`stopping_reason` states that saturation condition; it does not summarize the research session.

## 6. Review

A fresh study reviewer checks:

- selected depth matches complexity/user choice;
- all material questions are resolved or explicitly block planning;
- evidence is authoritative enough for the decision;
- synthesis follows evidence;
- no important version/security/compatibility issue is missing;
- unnecessary findings/process narration are omitted.

Review notes record concrete defects/evidence only.

## 7. Commands

Use the concise study controller:

```bash
python <skill-dir>/scripts/studyctl_concise.py validate --study /tmp/study.json
python <skill-dir>/scripts/studyctl_concise.py attach --plan <plan-path> --study /tmp/study.json
python <skill-dir>/scripts/studyctl_concise.py validate-plan --plan <plan-path>
```

For a simple request with no broad study, the study still records the explicit selection/skip rationale required by schema v2; it should be very short.

## 8. Text budgets

`studyctl_concise.py` rejects oversized or high-confidence vague derived fields. Important ceilings:

- request summary 320 chars;
- rationale 280;
- signal 180;
- location 220;
- finding 320;
- planning impact 280;
- material question 240;
- synthesis item 260;
- stopping reason 280;
- review note 240.

These are maxima, not targets. Split multiple independent findings instead of writing one long paragraph. Never silently truncate evidence that changes a decision.
