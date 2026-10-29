# Architecture and scope decision

Date: 2026-10-28. This is preparation for one implementation plan, not execution of its tasks.

## Source architecture

The 0.11.0 code has a selective skill router, request/preplanning/study controllers, a schema-v4 plan engine, context/pattern contracts, model catalog and availability layers, fresh-worker adapters, independent validation, process/resource monitors, job/watchdog recovery, a standalone validation companion, and installer/packaging/evaluation tooling. The production entrypoint is `run_concise.py`; it composes `artifact_contract`, `routingctl`, `runner_contract` and `pattern_runner_contract` over the raw runner. Tests must exercise this composition, not only isolated helper functions.

`BASELINE_INVENTORY.json` classifies every tracked baseline file and pins its content hash. `INTERNAL_EVIDENCE.json` adds source lines and symbols for the 32 feature read sets. Classification and indexing do not mean every line was independently reviewed. The feature reports contain the actual targeted observations, decisions and unknowns.

## Proposed execution organization

Keep the 86 stable task IDs to preserve request traceability. Convert the 32 research IDs into concrete implementation contracts and their successor reviews into code-review/correction contracts. Repurpose initial audit/inventory work into deterministic regression infrastructure. Replace the former Plan2 synthesis/generation slots with integration, correction, packaging and release-readiness tasks. The final whole-skill review remains last.

Do not recreate a universal maximum-model planning gate. Independent reviews remain required before accepting their implementations, but an unrelated missing reviewer does not prevent research preparation. Serialize overlapping source-write scopes through explicit dependencies. Each worker reads its assigned report and relevant source targets, not all 32 reports or a transcript.

## Verified baseline versus new work

The prepared reports recommend changes; no product file under `skill/`, `bin/` or `lib/` is changed by this conversion. The former baseline test logs are retained as historical evidence and are not new passes. All transformed implementation tasks start pending. Research prepared in this session is tracked separately from implementation and independent reviewer state.

## Evidence and economic rules

External source findings are registered in `SOURCES.json` with URL, access date and actual reading scope. Public book excerpts/chapters are not represented as full-book study. Quality/cost recommendations are engineering decisions, not measured live savings. No account quota, model availability, sandbox behavior or maximum reviewer identity is invented. Use deterministic tools for monitoring; reserve paid inference for ambiguity or work that needs model capability.

## Remaining contract checks

Implementation must retain the original twelve provider-switch acceptance cases, legacy/off defaults, phase and quota separation, redaction before truncation, independent validation and safe installed-copy boundaries. The implementation receipt format distinguishes actual tests, proposed tests and unverified platforms. Authorized live provider tests and independent model reviews remain future activities; they are not replaced by report existence.
