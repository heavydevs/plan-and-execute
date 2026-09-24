# Final whole-skill review for skill changes

Use this only when the target being changed is `plan-and-execute` itself. Add it as the last TODO in that implementation plan, after all code, docs, and focused validation changes. It is not a generic step for client projects.

## Review order

1. Read the entrypoint and reference map; verify the runtime path loads only the references needed for the active phase.
2. Trace each changed flow from documented instruction to CLI/controller/script, schema, persisted state, and cleanup behavior. Confirm command names, fields, defaults, path rules, and failure outcomes agree.
3. Check route floors, provider ladders, fallback, model/effort compatibility, interruption/resume, and evidence-based escalation. Stagnation or provider availability must not bypass the route policy.
4. Search all references to changed concepts and affected filenames/fields. Repair stale links, contradictory rules, duplicate normative text, old examples, and missing reference-map entries.
5. Review tool affordances: does deterministic code already exist for repetitive lookup, mapping, monitoring, cleanup, or compact reporting? Add a script only when it removes recurring model work and has bounded inputs/output, safe path handling, and a clear command contract.
6. Review token surfaces: static prompt prefixes, task-specific suffixes, repeated manifest history, raw logs/reports, research outputs, examples, and summaries. Preserve the latest diagnostic evidence while excluding superseded material from default prompts.
7. Confirm resource-map discovery, freshness checks, plan audit, runtime/toolchain preflight, in-run monitoring, and cleanup agree. The fast path should compare fingerprints and expose only changed paths.
8. Record concise findings and unresolved limits in the skill's durable Markdown research/review notes. The reviewer should receive the diff plus this checklist and return only actionable findings.

## Acceptance

- No changed instruction conflicts with another entrypoint/reference/provider contract.
- Every new behavior has a documented trigger, default, persisted evidence, and recovery outcome.
- Every new script has one bounded job; no model is asked to rediscover facts that deterministic tooling can cache.
- Raw diagnostic files needed to understand an active failure remain available, while workers see only the latest compact evidence by default.
- The final TODO records any platform limitation or behavior that could not be verified.
