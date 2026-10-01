# Jev advisory profile

Load only when `assistant.enabled` is true and `assistant.provider` is `jev`, or when diagnosing that profile.

## Purpose and boundary

Jev is used for one narrow `Choice`: select the most useful diagnostic focus for already-failed validation evidence from `mechanical`, `semantic`, `environmental`, `budget`, `plan_defect`, or `unknown`. It does not generate implementation, choose coding models, remove context, approve tests, or alter plan state.

This is intentionally the only Jev use in the skill until measured outcome data demonstrates another use is better than the normal deterministic/worker flow. Planning, model routing, context omission, acceptance, cleanup and resource monitoring remain unchanged.

## Activation

Both explicit configuration and `TYPESAFE_API_KEY` are required. A key by itself never enables advice. Missing key returns immediately to normal failure handling without creating a reservation. The key is read only at dispatch, passed only in the fixed TypeSafe Authorization header, never persisted, printed, added to the prompt, or copied to worker context.

The default model is pinned to `jev-1.13.0`. `assistant.jev_model` may override it deliberately. Do not silently replace a pinned version with `jev-latest` because confidence thresholds may behave differently after an alias moves.

The transport uses the fixed `https://api.typesafe.ai/v1/systemone` endpoint, Python standard library only, no proxy inheritance, no redirects, and no automatic retry. A valid response must contain the expected Choice distribution, finite confidence, returned model, and nonnegative API usage counts.

## Cost and failure behavior

Use the general one-call-per-task and four-calls-per-plan reservation budgets from `ASSISTANTS.md`. The existing evidence cap also bounds the Jev state. Jev calls use at most eight seconds even when the generic assistant timeout is larger.

`401`, `402`/`403`, `429`, `529`, network failure, redirect, invalid response, timeout, or other provider failure consumes only a reservation that was actually dispatched and then returns to the ordinary worker/validator path. No Jev retry or fallback adviser is started. The 402/403 mapping is defensive: TypeSafe's public API documentation explicitly documents 401, 422, 429 and 529, not a universal exhausted-credit status.

`unknown` or confidence below `assistant.jev_min_confidence` (default `0.60`) is stored as a skipped advisory result and is not shown to the next worker. The API-reported token usage is retained when the response was valid, so later evaluation can measure actual dispatch cost.

## Why only this call

The evidence set is already bounded and produced after deterministic failure handling; the answer space is finite and maps to existing diagnostic concepts. That makes Choice a reasonable optional second opinion. By contrast, task decomposition, route selection, context deletion, and acceptance can silently damage correctness when a classifier is wrong and currently lack workload-specific calibration in this project.

Official references reviewed 2026-09-30:
- https://docs.typesafe.ai/api
- https://docs.typesafe.ai/primitives/choice
- https://docs.typesafe.ai/models
