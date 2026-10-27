# Plan-free validation and workload-aware routing

Load only when standalone supervision, workload profiles, family quotas or observer setup is relevant. Ordinary DIRECT work must not read this reference. Research and source links remain in repository `docs/research/VALIDATION_WORKLOAD_ROUTING.md`.

## DIRECT does not mean unmonitored

A fast local check stays direct with no tracking state. For slow, failure-prone or service-dependent validation, invoke `validate-or-fix` or the same `scripts/validatectl.py` bundled here. Neither path creates an implementation plan, TODO, study, manifest or active pointer. Only `.ai-work/validation/<ID>` receipts and the reusable `.ai-work/SERVICE_MAP.md` are allowed.

```bash
pae validate run --validation TEST_ID
pae validate status --validation TEST_ID
pae validate inspect --validation TEST_ID
pae validate recover --validation TEST_ID
pae validate cleanup --validation TEST_ID
```

Equivalent: `python <skill-dir>/scripts/validatectl.py ...`. For a missing/stale map, use `service_map.py check|init`, discover the real command and dependencies, edit only relevant entries, then `stamp --confirm-reconciled`. `list --validation ID` reads only selected prerequisites. Never stamp an unreviewed or incomplete inventory.

Reuse `resource_watch.py`, `process_tree.py`, progress policies and the canonical repair ladder; do not fork a second monitoring engine. A plan runner already supervising a test must not also start the standalone supervisor. Orchestrated acceptance/checkpoints remain authoritative; both paths use the same monitoring primitives.

Supervision starts immediately. Five minutes is an instrumentation cue, not delayed activation. `no_progress_timeout_seconds` is a sliding window, `validation_hard_timeout_seconds` an explicit ceiling, and `stop_on_unhealthy` an opt-in owned-process stop after a trustworthy mapped check fails beyond its grace period. Heartbeats are not completed work. Refactor for meaningful progress before raising timeouts.

`status` is read-only; `inspect` consumes bounded redacted evidence deltas. Capture keeps a bounded prefix and rolling tail, reporting omitted bytes. Failed/interrupted logs survive. Successful cleanup rejects unsafe paths and removes only recognized owned logs/cursors, never source, tests, external logs or the shared map. See the companion operations guide when maintaining the independent package.

## Four independent axes

1. Workload: `implementation`, `frontend_design`, `validation_repair`, `log_monitoring`.
2. Logical floor: existing canonical tier and effort, with the existing risk/validation modifiers.
3. Execution route: host, exact discovered model, supported native effort.
4. Availability: configured credential-family quota pool and model/host scope.

A task may add `workload`; absent means `implementation`, preserving legacy plans. Do not infer a universal model quality order from its name. Frontend/design selection must have workload-specific evidence; verify visual constraints, responsive screenshots, interaction/error cases and accessibility. Reviewed screenshot baselines complement tests, not replace them. Risky authentication/data changes in a frontend task still require their higher floor.

`routingctl.py route --signals log_monitoring` selects a deterministic tool. `log_diagnosis` selects economy/low; `frontend_design` and `validation_repair` start standard/medium before risk modifiers. Use `workload: log_monitoring` only for an actual bounded observation/diagnostic task, never a disguised implementation or cleanup task.

## Explicit profile configuration

Add `workload_routing` to the global configuration or a version-2 plan overlay. Absence/disabled state preserves old routing. No automatic root-model changes occur.

```json
{
  "version": 2,
  "provider_order": ["antigravity", "claude", "codex"],
  "workload_routing": {
    "enabled": true,
    "manager_provider": "claude",
    "preserve_manager_quota": true,
    "profiles": {
      "agy-opus-intermediate": {
        "provider": "antigravity",
        "model": "claude-opus-5-5-high",
        "quota_pool": "antigravity-claude-gpt",
        "min_tier": "standard",
        "max_tier": "advanced",
        "max_effort": "high",
        "native_effort": "high",
        "workloads": ["implementation", "frontend_design", "validation_repair"],
        "observed_models": ["claude-opus-5-5-high"],
        "evidence": "Example policy only: replace with the actual observed ID and record workload validation."
      }
    },
    "routes": {
      "implementation": ["agy-opus-intermediate"],
      "frontend_design": ["agy-opus-intermediate"],
      "validation_repair": ["agy-opus-intermediate"]
    }
  }
}
```

The example ID is conditional on the installed account inventory, not a guarantee every account has it. `observed_models` records evidence supplied by the host; it is not authentication or a live discovery call. Invalid/unavailable model errors require refreshing configuration, never inventing a replacement ID.

Profile fields: safe unique name; supported `provider`; explicit `model`; `quota_pool`; optional `min_tier` (economy); required `max_tier`, `max_effort`, `workloads`, `observed_models`, `evidence`; optional `native_effort`, `enabled`. Maximum 32 profiles. `routes` contains ordered, distinct profile names per role. Frontend evidence is independent of general coding affinity. For fixed effort-bearing Antigravity IDs, `native_effort` must match the ID and bound `max_effort`.

A profile must satisfy the exact floor and permitted execution-provider chain. Explicit provider selection still wins. `preserve_manager_quota` can prioritize another eligible host, not lower capability. A configured host is profile-only: default models cannot bypass workload restrictions, conservative caps or family cooldowns. Add all required fallback profiles for such a host. Unprofiled hosts retain legacy defaults.

Antigravity Claude is conservatively capped at `advanced`; strongest `strong`/`max` work remains with a qualified alternative. This is the requested policy, not a cross-host IQ benchmark. An empty eligible set blocks for configuration instead of downshifting.

## Inventory and explanation commands

Run `agy models` with the actual account, then record exact IDs in a JSON array (or use the installed CLI's documented JSON option when available). The preset emits only IDs present in that input:

```bash
pae workloads preset --models-file agy-models.json --manager claude
pae workloads explain --config routing.json --workload frontend_design --tier standard --effort medium
```

Merge only the emitted `workload_routing` section and explicitly allow execution providers. The preset does not edit settings or validate login. Explanation is eligibility only; it does not call models or assert live availability.

The monitoring preference is observed Gemini 3.8 Flash, not an unverified future name. A fixed named preset is deliberately conservative; newer available IDs can be configured with evidence rather than silently upgraded. No universal cheapest-price claim or measured savings is made.

## Quota identity and recovery

Quota errors cool down `pool/<quota_pool>`; capacity cools down the specific model; authentication and missing CLI cool down the host. Gemini and Claude/GPT are distinct documented consumer pools in Antigravity; enterprise/custom API credentials require account-specific identities. Old provider-wide ledger entries remain conservatively host-wide until expiry. The logical tier/effort and technical-failure counters survive availability fallback, including another model on the same host. Profile routes are not overwritten by plan snapshots or generic automatic selectors.

## Optional observer

Configure ordered economy-eligible `log_monitoring` profiles. Unlike implementation preferences, the observer respects that exact order, so manager preservation cannot displace Flash as first choice. Enable only after reviewing data confidentiality:

```json
{"observer":{"enabled":true,"max_calls":1,"max_candidates":3,"timeout_seconds":30,"allow_claude_api":false}}
```

Standalone: `pae validate advise --validation TEST_ID --config routing.json`. Orchestrated: the existing anomaly gate calls the observer only for repeated ambiguous failure, confirmed stall or repeated unhealthy evidence. With `observer` disabled/absent the previous advisory behavior remains unchanged.

One diagnostic request may try at most three configured candidates sharing one deadline. Persist reservations and evidence hashes before calls; the same evidence cannot silently rebill after interruption. Metadata-only state and schema-checked advice remain bounded. A passing standalone validation followed by cleanup/new work can start a new observation budget.

Antigravity requires an empty-tool custom agent and a verified streaming init before evidence is sent, with explicit agent/model/cwd/review-mode checks. Known global executable customizations, incompatible protocol, unexpected tools, excessive output or timeout fail closed. It may write normal CLI/session metadata; this is not an OS sandbox against the native executable. Claude fallback requires explicit `allow_claude_api: true` and `ANTHROPIC_API_KEY`, using the existing bare tool-less adapter (API billing, not subscription OAuth). Other coding backends skip observer execution until their tool-less boundary is audited. Never substitute a writable sandbox or read-only prose.

Observers cannot approve tasks, override deterministic classifications, run fixes, terminate unrelated processes or choose deletion paths. Raw logs stay local; bounded redaction is best effort, not a guarantee against every secret. Keep high-risk evidence local unless its disclosure is authorized.
