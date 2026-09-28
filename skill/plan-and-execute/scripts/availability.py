#!/usr/bin/env python3
"""Bounded availability failover, independent of reasoning-failure counters.

The runner lease serializes these atomic per-task ledgers. No credentials, raw
provider output or commands are retained here. A cooldown is a local observation,
not a claim about a provider's actual quota reset time.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time
from pathlib import Path
from typing import Any, Callable

import planctl
import routing_config

MAX_STATE_BYTES = 32768
CONFIGURATION = re.compile(r'unknown (?:argument|option)|unrecognized arguments|invalid (?:argument|option|model)|unsupported (?:argument|option|effort)|unexpected argument', re.I)
CATEGORIES = {
    'authentication': re.compile(r'not authenticated|authentication (?:required|failed)|login required|please (?:log|sign) in|invalid api key|\bunauthorized\b', re.I),
    'quota': re.compile(r'\b429\b|rate[ -]?limit|usage limit|quota exceeded|insufficient_quota|too many requests|credits? (?:exhausted|depleted|used|limit)', re.I),
    'capacity': re.compile(r'capacity limit|service unavailable|server overloaded|\bHTTP\s*503\b', re.I),
}


class AvailabilityError(RuntimeError):
    pass


class AvailabilityPaused(AvailabilityError):
    """The pending TODO can be resumed; it is not a technical failure."""


def classify(return_code: int, text: str, retry_codes: list[int]) -> str | None:
    """Only classify unsuccessful CLI calls; cancellation/configuration never rotate."""
    if return_code in (0, 130, -2, -15, 143, 124):
        return None
    if return_code == 127 and text.strip() == 'Provider executable disappeared after preflight':
        return 'missing_cli'
    tail = text[-16000:]
    if CONFIGURATION.search(tail):
        return 'configuration'
    for category, pattern in CATEGORIES.items():
        if pattern.search(tail):
            return category
    return 'configured_exit' if return_code in retry_codes else None


def _path(plan_dir: Path, task_id: str) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', task_id):
        raise AvailabilityError('Invalid availability task identifier')
    path = plan_dir / 'results' / f'{task_id}-availability.json'
    if path.is_symlink() or path.parent.is_symlink():
        raise AvailabilityError('Availability ledger must not be a symlink')
    return path


def read(plan_dir: Path, task_id: str) -> dict[str, Any]:
    path = _path(plan_dir, task_id)
    if not path.exists():
        return {'version': 1, 'cooldowns': {}, 'phases': {}, 'events': []}
    try:
        with path.open('rb') as source:
            raw = source.read(MAX_STATE_BYTES + 1)
        if len(raw) > MAX_STATE_BYTES:
            raise ValueError('oversized')
        state = json.loads(raw)
        if not isinstance(state, dict) or state.get('version') != 1:
            raise ValueError('invalid version')
        if not isinstance(state.get('cooldowns'), dict) or not isinstance(state.get('phases'), dict):
            raise ValueError('invalid state')
        if not isinstance(state.get('events'), list) or len(state['events']) > 32:
            raise ValueError('invalid events')
        if set(state['phases']) - {'design', 'implementation'}:
            raise ValueError('invalid phase')
        for provider, item in state['cooldowns'].items():
            until = item.get('until') if isinstance(item, dict) else None
            if provider not in routing_config.PROVIDERS or type(until) not in (float, int) or not math.isfinite(until) or until < 0:
                raise ValueError('invalid cooldown')
        return state
    except (OSError, ValueError, TypeError) as exc:
        raise AvailabilityError('Invalid availability ledger; preserve it and repair before resuming') from exc


def _save(plan_dir: Path, task_id: str, state: dict[str, Any]) -> None:
    path = _path(plan_dir, task_id)
    planctl.atomic_write_json(path, state)


def unavailable(plan_dir: Path, task_id: str, phase: str, route: dict[str, str],
                category: str, config: dict[str, Any], *, now: float | None = None) -> None:
    if phase not in {'design', 'implementation'} or category not in {*CATEGORIES, 'configured_exit', 'missing_cli'}:
        raise AvailabilityError('Invalid availability event')
    state = read(plan_dir, task_id)
    now = time.time() if now is None else now
    provider = route['provider']
    if provider not in routing_config.PROVIDERS:
        raise AvailabilityError('Invalid availability provider')
    seconds = config.get('availability', {}).get('cooldown_seconds', 300)
    state['cooldowns'][provider] = {'until': now + seconds, 'reason': category}
    state['events'] = (state['events'] + [{
        'at': now, 'phase': phase, 'provider': provider, 'category': category,
        'tier': route['tier'], 'requested_effort': route.get('requested_effort', route['effort']),
    }])[-32:]
    _save(plan_dir, task_id, state)


def select(plan_dir: Path, task: dict[str, Any], config: dict[str, Any], intent: dict[str, str],
           override: str | None, phase: str, visited: set[str], available: Callable[[str], bool],
           clamp: Callable[[dict[str, Any], str, str], str], *, now: float | None = None,
           persist: bool = True) -> dict[str, str]:
    """Map an already chosen logical rung to another provider, never its ladder."""
    if phase not in {'design', 'implementation'}:
        raise AvailabilityError('Invalid dispatch phase')
    now = time.time() if now is None else now
    state = read(plan_dir, task['id'])
    # The fingerprint excludes current_route: claiming an availability retry must
    # not itself raise the stagnation floor on the next invocation.
    policy = {key: task.get(key) for key in ('provider', 'model_tier', 'reasoning_effort',
              'allow_provider_fallback', 'functional_failures', 'failure_classes', 'validation_stagnation')}
    policy['override'] = override
    policy['configuration'] = {key: config.get(key) for key in ('tier_routes', 'provider_order',
                               'allow_provider_fallback', 'functional_failures_per_provider', *sorted(routing_config.PROVIDERS))}
    fingerprint = hashlib.sha256(json.dumps(policy, sort_keys=True).encode()).hexdigest()
    previous = state['phases'].get(phase, {})
    logical = previous.get('logical_route', {}) if isinstance(previous, dict) and previous.get('fingerprint') == fingerprint else {}
    tier = logical.get('tier', intent['tier'])
    effort = logical.get('requested_effort', intent.get('requested_effort', intent['effort']))
    if tier not in routing_config.TIER_ORDER or effort not in routing_config.EFFORT_ORDER:
        raise AvailabilityError('Invalid persisted logical availability route')
    chain = routing_config.provider_chain(task, config, override, tier=tier)
    # Genuine technical failures keep their established provider rotation. Do not
    # return to a technically exhausted provider as an availability workaround.
    slot = int(task.get('functional_failures', 0)) // max(1, int(config.get('functional_failures_per_provider', 4)))
    chain = chain[min(slot, len(chain) - 1):]
    state['phases'][phase] = {'fingerprint': fingerprint, 'logical_route': {'tier': tier, 'requested_effort': effort}}
    if persist:
        _save(plan_dir, task['id'], state)
    skipped: list[str] = []
    for provider in chain:
        if provider in visited:
            skipped.append(f'{provider}:tried')
            continue
        cooldown = state['cooldowns'].get(provider, {})
        if cooldown.get('until', 0) > now:
            skipped.append(f'{provider}:cooldown')
            continue
        model = config[provider].get('models', {}).get(tier)
        if not isinstance(model, str) or not model.strip():
            raise AvailabilityError(f'No model configured for {provider}/{tier}; configure before dispatch')
        route = {'provider': provider, 'tier': tier, 'model': model,
                 'effort': clamp(config[provider], tier, effort), 'requested_effort': effort}
        if not available(provider):
            visited.add(provider)
            skipped.append(f'{provider}:missing_cli')
            if persist:
                unavailable(plan_dir, task['id'], phase, route, 'missing_cli', config, now=now)
            continue
        return route
    raise AvailabilityPaused(f"Task {task['id']} pending: no allowed provider for {phase}/{tier} ({', '.join(skipped)}). Resume after availability recovers or update configuration.")
