#!/usr/bin/env python3
"""Pure workload eligibility and explicit quota identities; no implicit model ranking.

Opt-in profiles compose with, never replace, the technical-failure ladder.
An absent section preserves the previous provider/model behavior exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from typing import Any, Callable

from routingctl import TIER_ORDER, EFFORT_ORDER

WORKLOADS = ('implementation', 'frontend_design', 'validation_repair', 'log_monitoring')
NAME = re.compile(r'[a-z][a-z0-9_-]{0,63}')
MODEL = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}')
CONFIG_KEYS = {'enabled', 'manager_provider', 'preserve_manager_quota', 'profiles', 'routes'}
PROFILE_KEYS = {'provider', 'model', 'quota_pool', 'min_tier', 'max_tier', 'max_effort', 'workloads',
                'evidence', 'enabled', 'observed_models', 'native_effort'}


class WorkloadError(ValueError):
    pass


def validate(section: Any, providers: tuple[str, ...]) -> None:
    if not isinstance(section, dict) or set(section) - CONFIG_KEYS:
        raise WorkloadError('workload_routing must be an object with documented keys')
    for key in ('enabled', 'preserve_manager_quota'):
        if key in section and type(section[key]) is not bool:
            raise WorkloadError(f'workload_routing.{key} must be boolean')
    if section.get('manager_provider', 'auto') not in ('auto', *providers):
        raise WorkloadError('Unsupported manager_provider')
    profiles = section.get('profiles', {})
    if not isinstance(profiles, dict) or len(profiles) > 32:
        raise WorkloadError('At most 32 workload profiles are allowed')
    for name, profile in profiles.items():
        if not isinstance(name, str) or not NAME.fullmatch(name) or not isinstance(profile, dict) or set(profile) - PROFILE_KEYS:
            raise WorkloadError('Invalid workload profile name or keys')
        if profile.get('provider') not in providers:
            raise WorkloadError(f'{name}: unsupported provider')
        model = profile.get('model')
        if not isinstance(model, str) or not MODEL.fullmatch(model) or model == 'default':
            raise WorkloadError(f'{name}: explicit discovered model ID required')
        if not isinstance(profile.get('quota_pool'), str) or not NAME.fullmatch(profile['quota_pool']):
            raise WorkloadError(f'{name}: explicit safe quota_pool required')
        lo, hi = profile.get('min_tier', 'economy'), profile.get('max_tier')
        if lo not in TIER_ORDER or hi not in TIER_ORDER or TIER_ORDER.index(lo) > TIER_ORDER.index(hi):
            raise WorkloadError(f'{name}: invalid tier interval')
        if profile.get('max_effort') not in EFFORT_ORDER:
            raise WorkloadError(f'{name}: max_effort required')
        native = profile.get('native_effort')
        if native is not None and native not in EFFORT_ORDER:
            raise WorkloadError(f'{name}: invalid native_effort')
        roles = profile.get('workloads')
        if not isinstance(roles, list) or not roles or any(not isinstance(r, str) or r not in WORKLOADS for r in roles) or len(set(roles)) != len(roles):
            raise WorkloadError(f'{name}: distinct supported workloads required')
        if type(profile.get('enabled', True)) is not bool:
            raise WorkloadError(f'{name}: enabled must be boolean')
        evidence = profile.get('evidence')
        if not isinstance(evidence, str) or not 8 <= len(evidence.strip()) <= 400:
            raise WorkloadError(f'{name}: bounded evidence or user-policy rationale required')
        observed = profile.get('observed_models')
        if not isinstance(observed, list) or not observed or len(observed) > 256 or any(not isinstance(m, str) or not MODEL.fullmatch(m) for m in observed) or model not in observed:
            raise WorkloadError(f'{name}: model must occur in the explicitly observed account inventory')
        if profile['provider'] == 'antigravity' and model.startswith('claude-') and TIER_ORDER.index(hi) > TIER_ORDER.index('advanced'):
            raise WorkloadError(f'{name}: Antigravity Claude is conservatively capped at advanced; hardest work uses another profile')
        embedded = re.search(r'-(low|medium|high|xhigh|max)$', model) if profile['provider'] == 'antigravity' else None
        if embedded and (native != embedded[1] or EFFORT_ORDER.index(profile['max_effort']) > EFFORT_ORDER.index(embedded[1])):
            raise WorkloadError(f'{name}: native_effort must match the embedded model effort')
        if native is not None and EFFORT_ORDER.index(native) < EFFORT_ORDER.index(profile['max_effort']):
            raise WorkloadError(f'{name}: native effort cannot claim a higher logical ceiling')
    routes = section.get('routes', {})
    if not isinstance(routes, dict) or set(routes) - set(WORKLOADS):
        raise WorkloadError('Invalid workload routes')
    for role, names in routes.items():
        if not isinstance(names, list) or len(names) > 32 or any(not isinstance(n, str) or n not in profiles for n in names) or len(set(names)) != len(names):
            raise WorkloadError(f'{role}: routes must reference distinct configured profiles')
        if any(role not in profiles[n]['workloads'] for n in names):
            raise WorkloadError(f'{role}: profile has no evidence for this workload')


def identity(route: dict[str, Any]) -> str:
    """One dispatch candidate; legacy callers still use provider strings."""
    return f"profile:{route['route_profile']}" if route.get('route_profile') else route['provider']


def model_key(route: dict[str, Any]) -> str:
    digest = hashlib.sha256(route['model'].encode()).hexdigest()[:20]
    return f"model/{route['provider']}/{digest}"


def cooldown_key(route: dict[str, Any], category: str) -> str:
    # Authentication and missing binaries are host-wide. Quota is credential-
    # family scoped, capacity model-scoped. Legacy routes retain old semantics.
    if not route.get('quota_pool') or category in ('authentication', 'missing_cli'):
        return route['provider']
    if category == 'capacity':
        return model_key(route)
    return f"pool/{route['quota_pool']}"


def cooldown_keys(route: dict[str, Any]) -> tuple[str, ...]:
    if not route.get('quota_pool'):
        return (route['provider'],)
    return (route['provider'], f"pool/{route['quota_pool']}", model_key(route))


def valid_cooldown_key(key: str, providers: tuple[str, ...]) -> bool:
    if key in providers:
        return True
    if key.startswith('pool/'):
        return bool(NAME.fullmatch(key[5:]))
    parts = key.split('/')
    return len(parts) == 3 and parts[0] == 'model' and parts[1] in providers and bool(re.fullmatch(r'[0-9a-f]{20}', parts[2]))


def candidates(task: dict[str, Any], config: dict[str, Any], chain: list[str], tier: str,
               effort: str, clamp: Callable, override: str | None = None) -> list[dict[str, Any]]:
    """Apply role fit before quota preference. Never expand an explicit provider chain."""
    section = config.get('workload_routing', {})
    enabled = section.get('enabled', False)
    role = task.get('workload', 'implementation')
    if role not in WORKLOADS:
        raise WorkloadError(f'Unsupported workload: {role}')
    ranked = []
    profiles = section.get('profiles', {}) if enabled else {}
    for name in section.get('routes', {}).get(role, []) if enabled else []:
        p = profiles[name]
        if not p.get('enabled', True) or p['provider'] not in chain:
            continue
        if not TIER_ORDER.index(p.get('min_tier', 'economy')) <= TIER_ORDER.index(tier) <= TIER_ORDER.index(p['max_tier']):
            continue
        if EFFORT_ORDER.index(effort) > EFFORT_ORDER.index(p['max_effort']):
            continue
        native = p.get('native_effort') or clamp(config[p['provider']], tier, effort)
        if EFFORT_ORDER.index(native) < EFFORT_ORDER.index(effort):
            continue
        ranked.append({'provider': p['provider'], 'tier': tier, 'model': p['model'], 'effort': native,
                       'requested_effort': effort, 'route_profile': name, 'quota_pool': p['quota_pool'],
                       'workload': role})
    requested = override or task.get('provider', 'auto')
    # Explicit provider wins even over an economy profile on another host.
    if requested != 'auto':
        ranked.sort(key=lambda r: r['provider'] != requested)
    elif enabled and section.get('preserve_manager_quota', False):
        manager = section.get('manager_provider', 'auto')
        # Only profiles eligible for the exact logical floor can move ahead.
        ranked.sort(key=lambda r: r['provider'] == manager)
    legacy = []
    for provider in chain:
        model = config[provider].get('models', {}).get(tier)
        if not isinstance(model, str) or not model.strip():
            # Empty tiers are a configuration error on legacy paths, but a
            # role profile may explicitly fill them without inventing a model.
            if not enabled and not ranked:
                raise WorkloadError(f'No model configured for {provider}/{tier}; configure before dispatch')
            continue
        restricted = [p for p in profiles.values() if p['provider'] == provider]
        if restricted:
            # An opted-in host uses explicit profiles only: a generic model must
            # not bypass a family cooldown, workload restriction or tier cap.
            continue
        if enabled and provider == 'antigravity' and model.startswith('claude-') and tier in ('strong', 'max'):
            continue
        legacy.append({'provider': provider, 'tier': tier, 'model': model,
                       'effort': clamp(config[provider], tier, effort), 'requested_effort': effort})
    if requested != 'auto':
        result = [r for r in ranked + legacy if r['provider'] == requested]
        result += [r for r in ranked + legacy if r['provider'] != requested]
        return result
    return ranked + legacy


def inventory_models(raw: Any) -> list[str]:
    """Accept documented list/id envelopes, not guessed model names in prose."""
    rows = raw.get('models') if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or len(rows) > 256:
        raise WorkloadError('Expected a model list or {"models": [...]} from the installed CLI')
    out = []
    for row in rows:
        value = row.get('id', row.get('model_id')) if isinstance(row, dict) else row
        if not isinstance(value, str) or not MODEL.fullmatch(value):
            raise WorkloadError('Model list contains an unsupported entry; do not guess its ID')
        if value not in out:
            out.append(value)
    return out


def antigravity_preset(models: list[str], manager: str = 'claude') -> dict[str, Any]:
    """Generate an explicit opt-in policy from account discovery, never a live claim.

    Only known verified families receive a preset; missing variants are omitted.
    The caller can edit/add measured profiles for other hosts and workloads.
    """
    profiles = {}
    definitions = [
        ('agy-flash-monitor', ('gemini-3.8-flash-medium', 'gemini-3.8-flash-high'), 'antigravity-gemini', 'economy', 'standard', ['log_monitoring']),
        ('agy-claude-intermediate', ('claude-opus-5-5-high', 'claude-opus-5-5-medium'), 'antigravity-claude-gpt', 'standard', 'advanced', ['implementation', 'frontend_design', 'validation_repair']),
    ]
    for name, options, pool, lo, hi, roles in definitions:
        model = next((m for m in options if m in models), None)
        if model is None:
            continue
        native = model.rsplit('-', 1)[-1]
        profiles[name] = {'provider': 'antigravity', 'model': model, 'quota_pool': pool,
                          'min_tier': lo, 'max_tier': hi, 'max_effort': native, 'native_effort': native,
                          'workloads': roles, 'observed_models': [model],
                          'evidence': 'User-selected conservative policy; ID observed in account CLI inventory. Not a cross-host quality benchmark.'}
    return {'workload_routing': {'enabled': True, 'manager_provider': manager, 'preserve_manager_quota': True,
            'profiles': profiles, 'routes': {role: [n for n, p in profiles.items() if role in p['workloads']] for role in WORKLOADS}}}


def main(argv: list[str] | None = None) -> int:
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    preset = sub.add_parser('preset')
    preset.add_argument('--models-file', required=True)
    preset.add_argument('--manager', default='claude')
    explain = sub.add_parser('explain')
    explain.add_argument('--config', required=True)
    explain.add_argument('--workload', choices=WORKLOADS, default='implementation')
    explain.add_argument('--tier', choices=TIER_ORDER, default='standard')
    explain.add_argument('--effort', choices=EFFORT_ORDER, default='medium')
    args = parser.parse_args(argv)
    try:
        if args.command == 'preset':
            result = antigravity_preset(inventory_models(json.loads(Path(args.models_file).read_text())), args.manager)
            import routing_config
            validate(result['workload_routing'], routing_config.PROVIDERS)
            result['notice'] = 'Merge workload_routing into configuration and allow antigravity in the provider chain. No authentication or billing claim.'
        else:
            import routing_config, planctl
            config = routing_config.load(planctl.default_config(), Path(args.config))
            task = {'provider': 'auto', 'workload': args.workload, 'model_tier': args.tier}
            def clamp(cfg, tier, effort):
                cap = cfg.get('max_effort_by_tier', {}).get(tier, 'max')
                return EFFORT_ORDER[min(EFFORT_ORDER.index(cap), EFFORT_ORDER.index(effort))]
            result = {'workload': args.workload, 'floor': {'tier': args.tier, 'effort': args.effort},
                      'candidates': candidates(task, config, routing_config.provider_chain(task, config), args.tier, args.effort, clamp),
                      'note': 'Eligibility only. No provider invoked; availability is checked at dispatch.'}
        print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(2, f'workload routing: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
