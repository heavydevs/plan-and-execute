# F004 / task 012 - Requirements, task decomposition and schema-v4 state

Date: 2026-10-28. Product baseline: 0.11.0, tree `f4b5a2285b7f2b1089d974c9e60814e46db858f4`.

**Research prepared; implementation pending; independent review pending.** This report is an implementation input, not a completion receipt. No external reviewer is impersonated.

## Decision and scope

**Recommendation (engineering inference):** Preserve the manifest as authority and implement transactional, traceable replanning with regenerated task projections.

## Questions addressed

- Trace request-part to requirement to task coverage and concise live projections.
- Evaluate bounded subtasks, high-task splitting, review gates and legacy schema compatibility.

## Repository evidence

The following are static-code observations against the pinned baseline, not results from authenticated providers:

- planctl creates schema-v4 plans, validates requirement coverage and dependencies, and renders per-task files. artifact_contract supplies the concise projections used in production.
- The existing plan has 86 tasks and an initial independent-review prerequisite inherited by the whole graph. The current user instruction removes research execution and the second-plan deliverable, so those assumptions must be revised explicitly.

### Read targets and integrity

- `skill/plan-and-execute/scripts/planctl.py` (SHA-256 `c3cdf3064fa18b7271ea801c614e18b45a467b4c923b98fdb8fbd16ab00bffd4`): `render_task` L1784-1933; `render_todo` L1935-1953; `save_manifest` L1981-2008; `create_plan` L2011-2195; `validate_plan` L2197-2402
- `skill/plan-and-execute/scripts/artifact_contract.py` (SHA-256 `477646cf30634e334e5c704a6cbe86e9dea4712f7527f51501c43462cadc08f3`): `install_plan_contract` L672-810
- `skill/plan-and-execute/scripts/planctl_concise.py` (SHA-256 `650baa02ebcb555acc9fe5874e5c94b4090720bc63f963c76b73f332dd3082e9`): file-level contract
- `skill/plan-and-execute/references/PLAN_SPEC.md` (SHA-256 `6b1014618196c4e0f966751190eb5bb3104798da7ff10694f9944f27b99fc92d`): `# Plan spec contract — schema v4` L1; `## Top level` L5; `## `request_analysis`` L25; `## `requirements`` L63
- `skill/plan-and-execute/references/PLANNING_PROTOCOL.md` (SHA-256 `2c12e549fa7032ef1691ea8c87b805beab4732c6fb976164ed295faf0b266508`): `# Final planning protocol` L1; `## 1. Preserve meaning, compress representation` L5; `## 2. Route planning work explicitly` L21; `## 3. Requirements` L31

## External basis

- [E057] [JSON Schema object reference](https://json-schema.org/understanding-json-schema/reference/object) - JSON Schema; accessed 2026-10-28.
- [E056] [os.replace and operating-system interfaces](https://docs.python.org/3/library/os.html#os.replace) - Python Software Foundation; accessed 2026-10-28.
- [E047] [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence) - LangChain; accessed 2026-10-28.
- [E058] [Semantic Versioning 2.0.0](https://semver.org/) - SemVer; accessed 2026-10-28.

Consult only these entries in `SOURCE_REGISTER.md` for the checked finding and scope. Provider documentation establishes an interface, not this account's available quota or a universal ranking of model quality. The proposed design below combines that evidence with the repository observations; it is not a vendor guarantee.

## Alternatives and cost/quality tradeoffs

| Disposition | Approach | Tradeoff |
|---|---|---|
| current_baseline | Edit TODO text by hand | Appears cheap but leaves manifest/projections and execution contracts inconsistent. |
| recommended | Validated spec revision plus deterministic rendering | More preparation checks, but one authoritative representation and safe recovery. |
| rejected | Create a new unrelated plan and leave both actionable | Ambiguous resumption, duplicate work and loss of original task traceability. |

## Implementation instructions

1. Define a plan-revision record containing previous spec hash, amendment, task-ID mapping and changed acceptance/dependencies. Keep completed evidence immutable and invalidate only outputs whose contract changed.
2. Generate manifest, TODO and task files from one normalized specification in a staging directory; audit the staged graph before activation. Do not hand-edit a task projection to disagree with its manifest.
3. Preserve requirement IDs and attach supersession notes for the two-plan clauses. Separate research-prepared metadata from implementation status.
4. Reject cycles, missing requirements, orphan reviews and inconsistent subtask IDs. Use bounded outcome-oriented subtasks, not one TODO per arbitrary file.
5. Replace the initial global model gate with deterministic preflight and put independent review after each implementation. Missing review capability blocks acceptance, not report preparation.

## Acceptance tests to implement and run

- [ ] A failed revision leaves the previous manifest and task projections readable.
- [ ] Every requirement has a consumer; every implementation has explicit acceptance and validation.
- [ ] A transformed research task remains pending, with subtasks instructing implementation from its assigned report.
- [ ] Legacy schema1-3 files are not silently rewritten using schema4 projection rules.
- [ ] No active task creates a second plan or depends on a nonexistent research output.

These cases are proposed test obligations. A research report or a fake-provider fixture cannot establish production model performance. Record executed commands, exit codes, source state and logs in the task's implementation receipt.

## Economic evaluation

The revision machinery is deterministic. Keep the implementation package small; avoid a model-generated duplicate narrative for every projection.

## Rollout and compatibility

Use the existing small deterministic helpers and compose through `run_concise.py` where applicable. Preserve disabled-mode behavior, persisted schema compatibility and locally edited installed copies. Add a behavior-changing policy only behind an explicit tested option. Do not add a framework, a paid model call or a global setting merely to satisfy this report. If current code already satisfies a proposed invariant, keep it and add the missing regression evidence instead of duplicating the mechanism.

## Limits and unresolved verification

- Multi-file durability needs fault-injection tests; os.replace alone is not a complete transaction or power-loss guarantee.
- No paid model benchmark, Windows live execution or independent maximum-model code review was performed during this research. Those are distinct future acceptance activities where applicable.

## Task handoff

Task **012** now implements this recommendation; task **013** reviews the resulting code and requires corrections before acceptance. Read this report, its JSON decision record and only the assigned source paths. Do not repeat broad research unless a material version mismatch invalidates a specific finding. No second plan is required.
