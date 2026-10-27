# Workload routing and optional observer

Use tools for routine polling and log filtering. An AI is optional diagnosis of new anomalous evidence, not the process supervisor or cleanup authority.

## Independent decisions

Select workload affinity, logical capability floor, actual host/model, and credential/quota pool independently. Keep the manager's model stable. `frontend_design`, `validation_repair`, `implementation` and `log_monitoring` are distinct roles; competence in one does not prove quality in another.

A frontend assignment needs explicit design constraints and validation of responsive layouts, interactions, browser errors, keyboard behavior and accessibility. Use reviewed screenshots plus behavioral assertions. Do not auto-accept changed screenshot baselines or silently weaken acceptance to lower model cost.

The workload configuration is opt-in and leaves existing installations unchanged. `workload_routing.profiles` requires explicit observed model IDs, a quota-pool name, tier/effort limits, supported workloads and a bounded evidence/rationale field. `workload_routing.routes` supplies ordered profile names for each role. A profile cannot lower the task's floor or silently add an unapproved execution provider. A host with explicit profiles uses those profiles only, so generic defaults cannot bypass a cap or cooldown.

## Antigravity discovery and policy

Run `agy models` in the actual authenticated account. Save the observed IDs as a UTF-8 JSON array, or use the installed CLI's documented JSON output if available. Do not substitute a display name for a CLI ID. Then:

```bash
python <skill-dir>/scripts/workload_routing.py preset --models-file agy-models.json --manager claude
```

The preset emits only known IDs present in that inventory. Merge its `workload_routing` object into your global routing configuration or an explicit configuration file; the command does not save, authenticate, change billing or invoke a model. Permit Antigravity in the execution provider chain separately.

The policy prefers observed Gemini 3.8 Flash for monitoring and Antigravity Claude Opus 5.5 for standard/advanced work when preserving a Claude manager's quota. Antigravity Claude is capped below strong/max. This is a conservative user policy, not a measured claim that the same model name has identical capability across products. Highest-risk work still requires a qualified stronger route. Native effort embedded in an ID is preserved rather than overridden by a contradictory flag.

Gemini and Claude/GPT pools are distinct for the documented consumer account policy. Quota exhaustion blocks the configured pool; authentication blocks the whole host; capacity is model-scoped. Enterprise/custom credentials can behave differently: name pools from actual account policy. Local cooldowns are observations, not promised reset times. No universal cheapest-model or measured token-saving claim is made.

## Optional anomaly advice

Enable an `observer` overlay only after reviewing data confidentiality and adapters:

```json
{
  "observer": {
    "enabled": true,
    "max_calls": 1,
    "max_candidates": 3,
    "timeout_seconds": 30,
    "allow_claude_api": false
  }
}
```

Configure an explicit `log_monitoring` profile chain as well. `advise` does nothing when disabled, when no anomaly exists, when no new evidence remains, or when its reservation budget is spent:

```bash
python <skill-dir>/scripts/validatectl.py advise --validation UNIT --config routing.json
```

The default budget is one diagnostic request with at most three candidate attempts sharing a 30-second deadline. Persist reservations before attempts; a crash cannot silently rebill the same evidence. If a candidate is unavailable, fall back within eligible monitoring profiles without raising the repair tier. The observer has no authority to approve tests, change a plan, run repairs, kill arbitrary processes or delete logs.

### Adapter boundaries

Antigravity uses a generated tool-less agent in a temporary workspace. Before sending evidence, require the streaming `init` event to confirm an empty tool list, the requested agent/model/cwd and review-mode permissions. Reject unexpected tool steps, malformed output, overflow or timeouts. Known global hooks/MCP/sidecars/plugins are conservatively rejected rather than disabled or edited. A CLI with an incompatible protocol safely skips. The trusted native CLI may maintain its normal account/session metadata; this is not an OS sandbox against the CLI itself.

Claude fallback reuses the bare tool-less adapter, requiring both `allow_claude_api: true` and an explicitly supplied `ANTHROPIC_API_KEY`. This can incur API billing; it does not silently convert subscription OAuth into API use. Other providers remain valid implementation backends but are skipped for external observer invocation until a tool-less boundary is verified. Never replace that boundary with a natural-language request to be read-only.

Advice is schema-validated and explicitly unverified. Preserve the deterministic failure classification and acceptance result. After a passing validation and handoff, cleanup can remove owned observer/evidence cursors; it never allows the model to select deletion paths.
