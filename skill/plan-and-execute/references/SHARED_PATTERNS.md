# Versioned shared-pattern contracts

Use this reference during final planning and execution when multiple TODOs must obey a shared contract whose later evolution can invalidate already-completed work.

Shared patterns are **not** ordinary execution context and are **not** validated learnings:

- execution context is minimal, mostly immutable knowledge needed to perform work;
- validated learning is directional earlier -> later evidence discovered after a source TODO passes;
- a shared pattern is a named, versioned normative contract with signatories and backward invalidation when its revision changes.

Examples: frontend Resource facades, common Admin CRUD/list behavior, SCSS/design-token conventions, API error envelopes, persistence/idempotency rules, or reusable accessibility interaction contracts.

## 1. Promote only real cross-cutting contracts

Create a pattern only when all are true:

- at least two TODOs must implement or consume the same non-obvious normative rule;
- consistency matters to product/architecture quality;
- a later legitimate revision could require already-completed consumers to change;
- duplicating the rule inside every task would create drift or waste context.

Do not create patterns for generic framework knowledge, style preferences with no correctness impact, or facts cheaply visible in one source file.

## 2. Pattern artifacts

`patternctl.py` stores live pattern state beside a final plan:

```text
<plan>/patterns/
  registry.json
  PAT001-rest-resource-facade.md
  PAT002-admin-crud.md
  assignments/
    001.md
    004.md
```

`registry.json` is authoritative for pattern revisions/signatories. Markdown files are deterministic projections for workers.

Each pattern records:

- stable id and title;
- current integer revision and digest;
- concise normative contract;
- source/requirement/fragment references;
- reason it is cross-cutting;
- signatory TODO ids;
- per-signatory adopted revision;
- revision history with reason and causing task when known.

Pattern contracts should describe **what must remain consistent**, not narrate every implementation detail.

## 3. Plan-time creation

After the ordinary final plan has passed review and `planctl ... create`, create patterns from a compact pattern spec:

```bash
python <skill-dir>/scripts/patternctl.py init \
  --plan .ai-work/<plan-id> \
  --spec /tmp/pattern-spec.json
```

A pattern spec example:

```json
{
  "patterns": [
    {
      "id": "PAT001",
      "title": "Frontend REST Resource facade",
      "contract": [
        "UI code calls business Resources instead of importing Axios directly.",
        "Each Resource uses the configured apiClient and typed DTOs.",
        "Resources do not import React components or UI stores."
      ],
      "source_refs": ["R014", "F027"],
      "rationale": "User, Book, Author and Genre flows must expose one stable HTTP facade convention.",
      "signatories": ["004", "006", "007", "009"]
    }
  ]
}
```

The final plan review must verify that pattern signatories are neither missing nor over-broad. A TODO reads only the patterns assigned to it.

For a prepared request package, `PATTERN_SEEDS.json` is only candidate evidence; the final planner decides which seeds become live patterns and which TODOs sign them.

## 4. Worker dispatch

Before dispatching a TODO, the orchestrator asks `patternctl assignment --plan ... --task ...` (or reads the generated assignment file) and gives the worker:

- its one task definition;
- assigned execution context;
- assigned validated learning files;
- **only its assigned pattern files/assignment projection**.

The worker must treat the current pattern revision as part of acceptance. It may propose a pattern change when implementation evidence makes the existing contract unsafe, impossible, or materially inferior, but must not silently diverge.

## 5. Adoption/signature

After a TODO passes its deterministic validation and is completed, record the exact pattern revisions it implemented:

```bash
python <skill-dir>/scripts/patternctl.py adopt \
  --plan .ai-work/<plan-id> --task 004
```

That adoption is the task's signature. A completed signatory is considered current only when its adopted revision equals the pattern's current revision.

The signature records compliance with a revision, not ownership of the pattern.

## 6. Evolving a pattern

When implementation reveals a necessary cross-cutting change:

1. capture the concrete evidence and why the old pattern is insufficient;
2. update the contract through `patternctl update`, not by editing Markdown directly;
3. increment the revision and preserve the prior digest/history;
4. identify all signatories whose adopted revision is now stale;
5. reset/reopen only affected completed TODOs;
6. pending signatories simply consume the latest revision when they eventually run;
7. reject or pause unsafe changes while another affected signatory is actively being edited from a stale assignment.

Example:

```bash
python <skill-dir>/scripts/patternctl.py update \
  --plan .ai-work/<plan-id> \
  --pattern PAT001 \
  --contract-file /tmp/rest-resource-v2.json \
  --reason "Generated Orval client requires the facade to accept typed cancellation metadata." \
  --changed-by-task 006
```

This is dependency invalidation: tasks that signed the old revision are downstream of the changed pattern and must be revalidated. Unrelated tasks are not reopened.

## 7. Avoid oscillation

A pattern should not change for cosmetic local preference. Revise only when evidence shows a material shared contract needs to change.

When a proposed change is architecturally significant and hard to reverse, retain rationale in a decision record or plan evidence as appropriate. Pattern history records the operational revision chain; it is not a substitute for a full ADR when the architectural decision itself deserves one.

Before accepting a revision, consider:

- compatibility with already-written signatories;
- migration cost;
- whether a new pattern is cleaner than mutating an unrelated one;
- deterministic validation needed for old and new consumers;
- whether the pattern should be split because two consumer groups no longer share one invariant.

## 8. Pattern validation and completion

Run:

```bash
python <skill-dir>/scripts/patternctl.py validate --plan .ai-work/<plan-id>
```

before dispatch and again before final handoff.

A final plan cannot be considered complete while any completed signatory has a stale adopted revision or while a pattern assignment references an unknown task.

Pattern files live inside the disposable planning workspace. Implementation code/tests survive cleanup; the pattern registry can be summarized into the final handoff or permanent project documentation when the project needs the contract after orchestration ends.

## 9. Why this resembles incremental build systems

The lifecycle deliberately follows dependency-graph invalidation rather than global rework. Build-system research defines minimal rebuilding as rerunning only tasks that transitively depend on changed inputs. Here, a pattern revision is a changed input and its signatory TODOs are dependents.

This also resembles contract compatibility workflows: shared contracts evolve, consumers verify a known version, and incompatible changes require explicit re-verification instead of silent drift.

For architectural rationale history, ADR practice recommends concise decision records and superseding prior decisions rather than rewriting history in place. Pattern revisions preserve the same auditable direction while remaining operationally tied to TODO invalidation.
