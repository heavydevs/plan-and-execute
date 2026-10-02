# Routing documentation baseline

Machine-readable record: [`ROUTING_DOC_BASELINE.json`](ROUTING_DOC_BASELINE.json) (path, sha256, status, reason per document; findings; requirement diff). Maintained with `tools/doc_baseline.py`:

```bash
python tools/doc_baseline.py inventory   # refresh hashes; new/changed paths become pending
python tools/doc_baseline.py review --status reviewed --reason "<=200 chars" <path>...
python tools/doc_baseline.py check       # fails only on schema/coverage defects; lists changed/new paths
```

`check` exits 0 when documents change after review and prints them for re-review, so a resume rereads only listed paths. It runs from `npm test` through `tools/run-repo-checks.js`.

Scope: root `*.md`, `docs/**/*.md` except `docs/requests/`, `skill/*/SKILL.md`, `skill/*/references/**`, `skill/*/assets/**/*.md|json`, `skill/*/agents/**`. Source request: `docs/requests/portable-model-routing-dynamic-provider-catalog.md` (its hash is recorded; its sections are cited as `#FR-nnn`). Request ids `TODO-nnn` are the request's own numbering, not plan task ids.

## Coverage

44 documents inventoried: 40 `reviewed`, 4 `not_applicable` (CONTRIBUTING, SECURITY, PUBLISHING en/pt-BR). Reviewed means contract sections were read or grep-verified, as each reason states; peripheral and Portuguese mirrors were checked by headings and contract-term search, not rewritten. Volatile external provider facts (GLM, DeepSeek, Muse, prices) were not re-verified here; they belong to the catalog TODOs.

## Stale or conflicting documents

| Id | Document / section | Issue | Affects |
|---|---|---|---|
| F001 | `MODEL_ROUTING.md` §4 | Four tiers; `advanced` is new | FR-021..023, TODO-001, TODO-008 |
| F002 | `SKILL.md` §4 | Four-tier floor table; size-budgeted, replace not append | FR-021, NFR-002, NFR-009, TODO-011 |
| F003 | `ORCHESTRATION.md` §6 | Four tiers; no F/L alias language | FR-002, FR-021, TODO-001, TODO-011 |
| F004 | `PLAN_SPEC.md` tasks[] | No documented tier value set, alias or MODEL_MATRIX link | FR-002, FR-004, FR-021, TODO-001, TODO-007 |
| F005 | `README.md` Logical tiers (+ pt-BR) | Four tiers; no Muse/GLM/DeepSeek rows | FR-006..008, FR-021, TODO-011 |
| F006 | `MODEL_ROUTING.md` Objective | "Exactly one of two provider files" | FR-006..008, FR-026, TODO-003, TODO-011 |
| F007 | `MODEL_ROUTING_CLAUDE.md` header | Ids fixed in `CURRENT_MODELS` v2026-09-30-v6 | FR-003, FR-015, NFR-001, TODO-001, TODO-002 |
| F008 | `MODEL_ROUTING_CODEX.md` Older catalogs | Fixed map re-applied each run | FR-003, FR-016, TODO-002, TODO-010 |
| F009 | `INSTALLATION.md` Model mapping (+ pt-BR) | Ids in per-plan `orchestrator.config.json` | FR-004, FR-005, FR-017, TODO-007, TODO-010 |
| F010 | `ROUTING_CONFIG.md` Paths and precedence | `tier_routes` keyed by four tiers | FR-021, FR-022, FR-026, NFR-001, TODO-003, TODO-010 |
| F011 | `TEST_RESOURCE_MONITORING.md` §2-3 | Monitor JSONL and cursors outlive plans | FR-034, NFR-015, TODO-015 |
| F012 | `LIFECYCLE.md` Successful completion cleanup | Monitor reports preserved | FR-034, TODO-015 |
| F013 | `WORKFLOW.md` §6 | Same preservation claim | FR-034, TODO-015 |
| F014 | `MODEL_ROUTING.md` §6 stagnation | Windows has no CPU/progress comparison | FR-028, NFR-007, TODO-015 |
| F015 | `completion-report.schema.json` | `additionalProperties:false`, no evidence/usage fields | FR-027, FR-030, FR-031, NFR-001, TODO-009, TODO-015 |
| F016 | `MODEL_ROUTING.md` §3 | Delegation bounds to extend, not relax | FR-024, FR-025, FR-029, NFR-012, TODO-014, TODO-015 |
| F017 | `PRIMARY_PLANNING.md` §3 | Immutable hashed fragments already exist | FR-032, NFR-014, TODO-016 |
| F018 | `tier-evals.json` | Expected routes must stay green | FR-010, FR-021, TODO-001, TODO-012 |
| F019 | `agents/openai.yaml` default_prompt | Duplicates SKILL.md policy | FR-021, TODO-011 |
| F020 | `RESEARCH_BASIS.md` Routing and cascades | No sources for new providers/cache/multi-agent | FR-007, FR-008, FR-013, TODO-011, TODO-017 |
| F021 | `CHANGELOG.md` Unreleased | Needs entries for each new contract | FR-037, TODO-011 |

Full wording per finding is in the JSON `findings` array.

## Requirement diff against the request

| Request ref | Change | Note | Findings |
|---|---|---|---|
| `#FR-021` | add | Five tiers replace four; old plans keep meaning | F001 |
| `#FR-002` | add | F1-F5/L1-L5 aliases normalized at plan/config boundary | F004 |
| `#FR-003` | add | Catalog supersedes fixed `CURRENT_MODELS`; fixed map becomes bootstrap | F007 |
| `#FR-004` | change | Ids move to `MODEL_MATRIX` snapshot; config keeps provider chains | F009 |
| `#FR-006` | add | Muse/GLM/DeepSeek profiles and per-provider references | F006 |
| `#FR-026` | change | Keep "one provider guide" rule; absent optional providers vanish | F010 |
| `#FR-034` | change | Docs promise survival; contract is owner/scope/retention with cleanup | F011 |
| `#FR-028` | change | Windows path must use progress/process evidence, not elapsed time | F014 |
| `#FR-027` | add | Evidence/delegation/usage fields as optional versioned report fields | F015 |
| `#FR-032` | confirm | Fragments/hashes exist; add per-question retrieval only | F017 |
| `#FR-029` | confirm | Assistants already lack authority | F016 |
| `#FR-037` | confirm | No contradiction with plan requirements, boundaries or dependencies | F002, F006, F011 |

## Decision

No finding changes a plan requirement, boundary or dependency: every conflict is a documentation change the request already requires (FR-021, FR-004, FR-034, FR-028). No `plan_defect`. Items to carry forward: keep `SKILL.md` within its size budget; keep `completion-report.schema.json` additions optional; update mirrored pt-BR docs and `agents/openai.yaml` together with their English sources.
