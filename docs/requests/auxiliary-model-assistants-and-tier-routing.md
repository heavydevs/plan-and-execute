# Request v2: safe auxiliary assistants and configurable tier routing

Status: approved for implementation, 2026-09-28. Original draft is preserved in git
and the retained plan's REQUEST.md. This is a FINAL_PLAN input, not primary staging.
Research and tradeoffs: [AUXILIARY_ROUTING.md](../research/AUXILIARY_ROUTING.md).
Implementation plan: `.ai-work/20260928-auxiliary-routing/manifest.json`.

## Purpose and evidence

The current runner records quota events without rotating its provider selection,
so repeated invocations can select the same exhausted CLI. Fix this independently
of reasoning-quality escalation. Add a secondary diagnostic model only when its
bounded advice can help an ambiguous validation failure. More agents are not
intrinsically cheaper or more accurate; deterministic tools stay the first choice.

Keep one authoritative owner per TODO. Assistants cannot edit the product,
complete tasks, select authoritative failure classes, launch other assistants or
replace deterministic tests. No debate/voting or always-on second model.

## R001 - Evidence-based design

Use primary research and current provider documentation. Record the observed base
behavior, selected design, measurable acceptance and unverified platform claims.
Do not promise billed-token savings from character counts or mock benchmarks.

## R002 - Layered tier configuration

Support a user-global `orchestrator.config.json` and per-plan overrides. Resolve
in this order: built-in defaults < global < explicit per-plan values < explicit
CLI provider selection. Global location follows `PAE_CONFIG_PATH`, then the
platform configuration directory. Never put credentials in these files.

For each `economy`, `standard`, `strong`, `max` tier, configure one `primary` and
an ordered `fallbacks` list. Lists replace, objects merge; an empty fallback list
means no fallback. Legacy `provider_order` and complete v1 plan snapshots remain
valid explicit configuration. Newly generated plans inherit through small overlays.

Reject invalid object types, booleans-as-integers, unknown provider/tier names,
duplicate chain members, invalid model/effort combinations and unbounded new retry
settings before any model call. Keep explicit task provider and
`allow_provider_fallback` behavior, including a pinned unavailable provider.

## R003 - Availability is not reasoning failure

Quota, rate limit, capacity and classified CLI availability interruption advance
to the next allowed provider at the **same logical tier and requested effort**.
Actual provider effort caps are recorded separately. This works for both design
and implementation dispatch; it does not reset accumulated technical evidence.

Record availability events separately. They must not increase
`functional_failures`, append `failure_classes`, consume the technical-attempt
budget or trigger stronger-model escalation. Preserve the existing evidence-based
rotation for genuine technical failures. User cancellation is not provider failure.
Malformed arguments/configuration are not evidence that another model is needed.

## R004 - Bounded resumability

Persist provider cooldowns and the logical route associated with availability
failure. Do not retry an exhausted provider immediately or wait out a quota window
before trying an allowed alternative. If the entire chain is unavailable, pause
with durable pending state and a bounded diagnostic; a later resume rechecks it.
Never busy-loop, retry indefinitely, widen a forbidden chain or discard edits.

## R005 - Sequential interactive setup

Expose `pae configure` and a Python controller usable by a skill host. Ask exactly
one setting per multiple-choice question. Per tier: primary provider, then ordered
fallback providers. Ask enabling assistance separately from selecting its provider.
Offer model choices separately when a concrete mapping needs confirmation.

Use numbered choices in plain terminals. Keep question/answer logic separable so a
host can render structured choices. Cancellation/EOF must leave configuration
unchanged. Validate everything before an atomic write and print a summary/path.

Only offer installed, authenticated providers. Executable presence is not proof
of authentication: use bounded non-generative status probes where documented.
For a provider without a reliable status probe, report unknown and require explicit
user authentication confirmation separately; never read or print credential data.
Probe timeout/auth failure cannot trigger a billed generation call.

## R006 - Concrete models and effort

Preserve user-defined model names and `models_without_effort`. Some Antigravity
IDs embed effort and reject a separate `--effort`; recognize or explicitly confirm
that capability when choosing a model. Reject contradictory known capability
settings before dispatch. Do not silently replace configured models with the
catalog default. Logical tier names describe routing, not measured equivalence
between different vendors' models.

## R007 - Opt-in advisory validation triage

Default off, preferred provider Antigravity, independently overridable. Default
one advisory attempt per task, with bounded evidence/output and wall-clock limits.
Reserve the attempt before dispatch; timeout, invalid output and interruption
still consume it. Deduplicate identical evidence across resumes.

Trigger only after a configurable repeated-failure, unhealthy-sample or stall
threshold. Skip deterministic lint/type/format checks whose output already gives
the diagnosis. A successful validation must never dispatch an assistant.

Inputs are allowlisted, redacted, bounded evidence: validation ID/command,
first-failure window, output tail, unhealthy resource samples/log excerpts and
signature/age. Never send other tasks, full plan, raw full logs or chat history.
Explicit opt-in authorizes this limited data transfer; redaction is best effort.

Return strict JSON: suggested class, finite confidence, short hypothesis and
bounded evidence references. Label it advisory/unverified. Reject unknown fields,
oversized output, invalid classes/confidence and references outside the supplied
evidence. The deterministic classifier remains authoritative even on disagreement.
Advice may enter a small next-worker capsule; it must not inflate normal prompts.
Assistant errors never replace the original failure, count as worker defects or
block the core workflow. Report missing safety/auth/capabilities as a skip.

## R008 - Genuine read-only boundary

The assistant profile must be independent of the coding-worker profile. A fresh
working directory, `skip_permissions: false`, or `sandbox: true` alone does not
prove read-only access. In particular Antigravity's sandbox allows workspace writes.

Use an enforced no-write/tool-less provider profile or a verified operating-system
isolation boundary; never inherit unrestricted worker flags, hooks, extensions or
MCP tools. Pass evidence in the prompt, not repository write permissions. If this
cannot be guaranteed on a provider/OS/version, fail closed and continue without
advice. Document supported and unsupported native profiles honestly.

## R009 - Checkpoints and delivery

Use plan-and-execute's manifest, task definitions, subtask controls, service-map
validation and final review. Preserve the plan (`cleanup_on_success: false`) because
the user requested resumability. Commit and push each validated task, including
its checkpoint and test evidence. Host-managed execution is allowed when worker
CLIs are unavailable, but must not be presented as isolated multi-model execution.

## R010 - Whole-skill compatibility

Add negative, recovery and integration tests. Preserve direct-mode escape,
planning/study/lifecycle contracts, explicit provider overrides and deterministic
validation. Update focused references and both READMEs. Fix existing prompt-budget
violations through concision, not increased limits. Package the complete skill.

## Acceptance matrix

- Config: global inheritance; nested plan override; legacy snapshot; unknown or
  malformed values; duplicate chains; pinned providers; effort-embedded model.
- Availability: quota then fallback success; design fallback; unequal vendor
  ladders; chain exhaustion; cooldown/resume; cancellation; real-failure escalation.
- Setup: each setting is a separate question; ordered fallbacks; no installed CLI;
  unknown authentication; cancellation; invalid choice; atomic saved configuration.
- Advice: default-off and common-path zero calls; deterministic skip; trigger
  thresholds; redaction; no writes; invalid/malicious output; timeout/call budget;
  repeat deduplication; authoritative decision unchanged; bounded failure capsule.
- Delivery: retained plan passes controller audits; full tests and fixed budgets;
  identify native-provider/Windows limits separately from mocks and local checks.
