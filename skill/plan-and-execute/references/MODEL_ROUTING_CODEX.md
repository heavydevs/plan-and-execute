# Codex model routing

Read only when Codex will execute the current work. `MODEL_ROUTING.md` owns provider-independent policy.

## Current capability map

| Tier | Model | Typical starting effort |
|---|---|---|
| `economy` | `gpt-5.6-luna` | `low` |
| `standard` | `gpt-5.6-terra` | `medium` |
| `strong` | `gpt-6-astra` | `low` or `medium` |
| `max` | `gpt-6-astra` | `xhigh` only when long-horizon evidence justifies it; `max` is exceptional |

Do **not** use GPT-5.6 Sol High as the default difficult-work route. Current OpenAI calibration places Astra Low/Medium as the successor to Sol High. Independent coding-agent measurements also show Astra's effort levels on the cost/quality frontier; because exact low-vs-Sol-high results vary by harness, use **Astra Medium as the safer difficult-work baseline when verification is weak**, while Astra Low is preferred when the task is bounded and objectively verifiable.

## DIRECT mode

Small or medium-small work stays without a plan when it is cohesive. Model routing still applies:

- one-off lookup/build/test/lint -> deterministic tool, no subagent;
- broad read-only discovery -> Luna Low; Luna Medium only for bounded multi-hop tracing;
- tiny mechanical edit with obvious local review or deterministic validation -> keep current useful context; delegate to Luna Medium only when isolation actually saves context;
- normal bounded implementation with good validation -> Terra Medium;
- normal implementation that exposes a reasoning gap -> Terra High or move directly to Astra Low when the failure is semantic rather than mechanical;
- small but subtle change with weak/no tests -> Astra Low when silent semantic failure would be materially costly; otherwise Terra Medium plus focused review is cheaper;
- difficult but strongly verifiable debugging/implementation -> Astra Low first, then Astra Medium from concrete failure evidence;
- high-blast-radius or weakly verifiable architecture/security/concurrency/migration decisions -> Astra Medium or High directly.

Do not create an ORCHESTRATED plan merely to obtain Astra. DIRECT can choose any justified route.

## ORCHESTRATED tasks

Choose the logical tier per TODO, not per parent request. Recommended effort behavior:

- `economy`: Luna Low; Medium only when the exploration itself requires multi-hop reasoning;
- `standard`: Terra Medium; High after an actual reasoning failure;
- `strong`: Astra Low when deterministic validation is strong, otherwise Astra Medium; High for high-risk/weak-verification work or evidence that Medium under-reasoned;
- `max`: Astra High/XHigh for genuinely demanding long-running work; Max only when lower efforts leave a plausible capability gap.

A failed compiler command does not automatically justify Astra. A wrong architecture decision may justify Astra before any retry.

## Exploration subagents

Use Luna to protect expensive context from disposable discovery:

- give the explorer a narrow question and the minimum starting paths/symbols;
- prefer a fresh/no-history child when model override would otherwise inherit expensive root context;
- request a compact evidence map, not narration or full files;
- keep explorers read-only unless the task is explicitly mechanical and independently verifiable;
- default to at most two simultaneous explorers.

The parent verifies material findings before consequential edits.

## Escalation ladder

For objectively verifiable work:

```text
Luna/Tools exploration
        -> Terra Medium implementation
        -> Terra High when the gap is local reasoning
        -> Astra Low when stronger model capability is useful
        -> Astra Medium/High from concrete failure evidence
        -> Astra XHigh/Max only for true long-horizon/frontier need
```

Skip irrelevant rungs. In particular, do not burn several high-effort Terra retries when one Astra Low attempt is more likely to solve a demonstrated capability gap.

## Sol compatibility

Sol is no longer a preferred default tier in this catalog. It may still be selected by an explicit local provider configuration when Astra is unavailable or a project-specific eval shows Sol wins for that workload. Availability/quota failure is not evidence to increase reasoning effort.
