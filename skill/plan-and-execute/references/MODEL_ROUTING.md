# Model and provider routing

Load this reference only when assigning or escalating portable model capability. `PORTABLE_MODEL_ROUTING.md` defines how F/L is bound dynamically to current concrete models.

Provider-specific references exist for Codex, Claude Code, Gemini CLI, Qwen Code, and Muse Code. Do not preload them during execution: read only the provider actually being resolved. During planning, consult the providers needed to build the compact compatibility table, then persist only the resulting table/sources.

## Objective

Maximize verified quality per credit/token and completed task. A durable TODO must describe capability, not vendor identity.

## 1. Portable model family: F

Every new ORCHESTRATED TODO declares one model family:

| Family | Meaning |
|---|---|
| `F1` | Economy/fast: exploration, classification, mechanical/narrow work, cheap summaries |
| `F2` | General coding: ordinary bounded implementation, debugging, tests |
| `F3` | Strong: subtle/high-risk/weakly verifiable engineering, difficult debugging |
| `F4` | Frontier: long-horizon/high-risk work or evidence-backed escalation beyond F3 |

Use the lowest credible F for the leaf. Overall request size does not determine F.

## 2. Portable reasoning level: L

F and L are independent. L is the requested reasoning/power level inside the concrete model selected for F:

| Level | Meaning |
|---|---|
| `L1` | Lowest supported useful level |
| `L2` | Low-to-medium level; normal cost/quality balance for many tasks |
| `L3` | Strong/high reasoning |
| `L4` | Extra-high reasoning for demanding work |
| `L5` | Highest supported level; exceptional |

Providers with fewer native levels map adjacent L values to the same effective level in `MODEL_COMPATIBILITY.json`. Never invent unsupported effort names.

## 3. Classify before choosing F/L

- deterministic lookup/build/test/lint: use tools directly when no model judgment is needed;
- broad read-only exploration: normally F1/L1-L2;
- routine bounded implementation with strong validation: normally F2/L2;
- normal work whose correctness is less mechanically verifiable: F2/L3 or F3/L1-L2 depending on whether the gap is reasoning depth or model capability;
- architecture/security/concurrency/migration/weak-verification work: normally F3/L2-L3;
- frontier/long-horizon or repeated evidence-backed capability failure: F4 with the lowest credible L.

A newer/stronger model at low L may be cheaper and better than a weaker family at very high L. Escalate the axis implicated by evidence.

## 4. Verification changes the cheapest safe route

When deterministic validation is strong and failure is cheap to detect:

```text
lowest credible F/L -> deterministic validation
PASS -> stop
FAIL -> retain compact evidence -> raise L or F as justified -> validate again
```

When objective verification is weak and silent failure is costly, start stronger. Do not interpret “no tests” as “always F4/L5”; consider change size, reversibility, inspectability, and blast radius.

## 5. Provider independence is mandatory in new plans

Do not persist a concrete provider, model id, vendor tier name, or vendor effort name in a new TODO. Use only `model_family` and `model_level`.

Concrete current bindings are generated separately during planning in:

- `MODEL_COMPATIBILITY.json` — authoritative machine-readable mapping;
- `MODEL_COMPATIBILITY.md` — rendered human-readable table referenced by the plan/TODOs.

Switching provider resolves the same F/L through that table. It does not require re-planning unless task semantics changed.

## 6. Dynamic compatibility discovery

Read `PORTABLE_MODEL_ROUTING.md` while planning. The planning agent must check current local CLI/model information and current authoritative provider documentation instead of copying remembered model ids from this repository. The skill intentionally contains no durable concrete model catalog.

Refresh compatibility when switching provider, when a recorded model/effort is rejected or unavailable, or when current model hierarchy is uncertain. Refresh the binding, not the TODO.

## 7. Provider fallback is not technical escalation

Quota/rate-limit exhaustion, temporary capacity, unavailable models, or host interruption do not prove the task needs more intelligence. Preserve F/L and resolve it on another compatible provider. Functional/correctness evidence may raise L or F; provider availability alone may not.

## 8. DIRECT mode

DIRECT exits the planning harness, not economical model routing. Use deterministic tools first, keep useful current context, delegate only exploration that saves meaningful context, and choose capability from semantic risk/verifiability. Do not create an ORCHESTRATED plan merely to obtain a stronger model.

## 9. Stop when verified quality is reached

A stronger route is not a reward for retries. Stop when acceptance criteria and independent validation pass. Replan when evidence invalidates requirements, decomposition, dependencies, or context boundaries—not merely because a model/provider changed.
