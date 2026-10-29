# F003 / task 010 - Adaptive internal and external study

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Turn adaptive study into a bounded decision log: preserve user-selected depth, ask material questions, reuse dated evidence and stop when decisions are stable.

## Questions addressed

- Separate user-selected depth from discovery breadth and stopping criteria.
- Evaluate authoritative evidence retrieval, access dates and deduplication without silently omitting requirements.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- studyctl normalizes explicit internal/external study choices and attaches evidence to planning. Its records distinguish questions, sources and synthesis.
- The former plan repeated research as a future task even though the user now requests research in advance. Prepared reports should be inputs, not a reason to restart the same literature search.

### Read targets and integrity

- `skill/plan-and-execute/scripts/studyctl.py` (SHA-256 `fefef4d70d93e92a2aaff124af727d26596de4a7935232c9b009df6269c94d82`): `normalize_study` L706-715; `attach_study` L1001-1043
- `skill/plan-and-execute/scripts/studyctl_concise.py` (SHA-256 `7dc5480368dba06e5c5a14f91b4c41d896ec3b86c8864641929177a3f5d35735`): file-level contract
- `skill/plan-and-execute/references/ADAPTIVE_STUDY.md` (SHA-256 `349f06551e9fd94a33f437d814c4c116339b9a111cebfe506bb6a5f0b59f50a3`): `# Adaptive study protocol` L1; `## 1. Classify before broad repository inspection` L5; `### Simple` L9; `### Medium` L13
- `skill/plan-and-execute/references/STUDY_CHOICES.md` (SHA-256 `8c8adbcdc085eb181009926e3f6306fd99b5ff888de0cef6990e60e3843c4266`): `# Complex-study choices` L1; `## Recommendation marker` L7; `## Interactive choice UI` L31; `## Choice 1 — internal study` L45

## External basis

- [E008] [Agents, adapted from AI Engineering](https://huyenchip.com/2025/01/07/agents.html) - Chip Huyen; accessed 2026-10-28.
- [E009] [AI engineering pitfalls](https://huyenchip.com/2025/01/16/ai-engineering-pitfalls.html) - Chip Huyen; accessed 2026-10-28.
- [E003] [Effective context engineering for AI agents](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) - Anthropic; accessed 2026-10-28.
- [E002] [Building effective agents](https://www.anthropic.com/research/building-effective-agents) - Anthropic; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Study packet with broad prose findings | Supports traceability, but can encourage repeated reading without explicit freshness disposition. |
| recommended | Question-first evidence and selective refresh | Keeps auditability with smaller repeated context and exposes unresolved material facts. |
| rejected | Autonomous unlimited web exploration or source-count-only approval | Expensive and may still miss the decisive compatibility question. |

## Implementation instructions

1. Add a compact reusable evidence record with material question, source/version/date, repository applicability, confidence and implementation consequence.
2. Distinguish verified source facts, observed repository behavior and proposed design. Store failed access attempts and unknowns explicitly rather than substituting a plausible fact.
3. Deduplicate shared external sources by stable ID while giving each task its own applicability analysis. Refresh only version-sensitive decisions or contradicted evidence.
4. Use a stopping condition: every high-impact question is answered or has a concrete implementation-time capability probe; no unresolved issue can silently change acceptance.
5. Preserve user-requested study breadth and the original source. Do not silently narrow a broad study to one blog or use an arbitrary source count as semantic proof.

## Acceptance tests to implement and run

- [ ] A source with no date/version is flagged for refresh when it affects CLI behavior.
- [ ] Two tasks sharing the same source retain different applicability notes without copying an entire article.
- [ ] A contradictory provider document yields a probe requirement, not an invented resolution.
- [ ] Known prepared reports are consumed without requiring another broad research phase.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

Reuse verified source metadata and only reopen the source for a material uncertainty. Track sources retrieved, duplicated input bytes and decisions changed; do not equate more citations with higher quality.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- No complete commercial book was available. This research uses the public AI Engineering excerpt and a public SRE chapter, explicitly labeled as such.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **010** now implements this recommendation; task **011** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
