# Plan 2 acceptance contract

Plan 2 is a future deliverable, not created or approved by the initial preparation.

1. Use only reviewed remaining decisions from the optimization backlog. Every feature
   has implement, retain or defer disposition; every accepted implementation decision
   maps to requirements and bounded TODOs. Provider-switch work completed in Plan 1
   is baseline evidence, never duplicated implementation.
2. Cite original request parts, source findings, numbered external evidence, ADRs,
   max-review receipts and the post-Plan-1 Git tree. Label hypotheses explicitly.
3. Every implementation TODO has one coherent outcome, exact source/test scope,
   dependencies, observable acceptance, deterministic mapped validation, resumable
   subtasks, logical provider/tier/effort and a fresh maximum-capability review gate.
4. Recompute implementation route floors from risk and verifiability; never copy
   research task routes automatically. Resolve actual models at execution time.
5. Use immutable narrow context and only justified cross-task contracts. Keep root
   route stable; isolate workers only where their independent context earns its cost.
6. Planctl validate/audit, studyctl validate-plan and service-map audit-plan must pass.
   Reports must include real outputs and exit codes. A dry-run must not invoke models.
7. No high-risk unknown may be hidden by approval. Unknown source capabilities,
   authenticated testing, Windows coverage and unmeasured costs remain explicit gates.
8. Keep input evidence in docs outside disposable Plan 1 state. The manager creates
   `.ai-work/<plan-2-id>/` only after checking source freshness. Do not auto-activate it
   or perform commit, push, PR, npm publication or authenticated runs without consent.
9. Final Plan 2 TODO uses SKILL_MAINTENANCE_REVIEW.md and reports actual tested limits.
