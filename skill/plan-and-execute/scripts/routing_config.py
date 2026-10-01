#!/usr/bin/env python3
"""Validated routing overlays. No model calls, credential reads, or file writes on load."""
from __future__ import annotations

import copy
import json
import math
import os
import re
from pathlib import Path
from typing import Any

from routingctl import TIER_ORDER, EFFORT_ORDER

PROVIDERS = ('claude', 'codex', 'antigravity', 'gemini', 'qwen', 'kimi', 'trae')
ASSISTANT_PROVIDERS = (*PROVIDERS, 'jev')
MAX_CONFIG_BYTES = 256 * 1024
EXTRA_DEFAULTS = {
    'tier_routes': {},
    'availability': {'cooldown_seconds': 300, 'max_attempts_per_run': 7},
    'assistant': {
        'enabled': False, 'provider': 'antigravity', 'model_tier': 'economy',
        'reasoning_effort': 'low', 'max_calls_per_task': 1, 'max_calls_per_plan': 4,
        'max_input_chars': 6000, 'max_output_chars': 2000, 'timeout_seconds': 30,
        'jev_model': 'jev-1.13.0', 'jev_min_confidence': 0.60,
        'repetition_threshold': 2, 'unhealthy_threshold': 2, 'stall_seconds': 300,
    },
}


class ConfigError(ValueError):
    """Invalid local configuration; never silently substitute defaults."""


def merge(base: dict, overlay: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        result[key] = merge(result[key], value) if isinstance(value, dict) and isinstance(result.get(key), dict) else copy.deepcopy(value)
    return result


def global_path(env: dict | None = None, *, home: Path | None = None, platform: str | None = None) -> Path:
    env = os.environ if env is None else env
    if env.get('PAE_CONFIG_PATH'):
        return Path(env['PAE_CONFIG_PATH']).expanduser()
    home = Path.home() if home is None else home
    windows = (os.name if platform is None else platform) == 'nt'
    base = Path(env.get('APPDATA') or home / 'AppData' / 'Roaming') if windows else Path(env.get('XDG_CONFIG_HOME') or home / '.config')
    return base / 'plan-and-execute' / 'orchestrator.config.json'


def read(path: Path, *, optional: bool = False) -> dict:
    try:
        with path.open('rb') as stream:
            data = stream.read(MAX_CONFIG_BYTES + 1)
        if len(data) > MAX_CONFIG_BYTES:
            raise ConfigError(f'Configuration exceeds {MAX_CONFIG_BYTES} bytes: {path}')
        value = json.loads(data.decode('utf-8'), parse_constant=lambda value: (_ for _ in ()).throw(ConfigError('Non-finite JSON number')))
    except FileNotFoundError:
        if optional:
            return {}
        raise ConfigError(f'Configuration not found: {path}') from None
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigError(f'Cannot read configuration {path}: {type(exc).__name__}') from exc
    if not isinstance(value, dict):
        raise ConfigError(f'Configuration must be an object: {path}')
    return value


def _object(value: Any, name: str) -> dict:
    if not isinstance(value, dict):
        raise ConfigError(f'{name} must be an object')
    return value


def _integer(value: Any, name: str, low: int, high: int) -> None:
    if type(value) is not int or not low <= value <= high:
        raise ConfigError(f'{name} must be an integer in [{low}, {high}]')


def _boolean(value: Any, name: str) -> None:
    if type(value) is not bool:
        raise ConfigError(f'{name} must be a boolean')


def _names(value: Any, name: str, *, empty: bool = True, allowed=PROVIDERS) -> list:
    if not isinstance(value, list) or (not empty and not value) or any(not isinstance(x, str) or x not in allowed for x in value) or len(value) != len(set(value)):
        raise ConfigError(f'{name} must contain distinct supported values')
    return value


def embedded_effort_model(model: str) -> bool:
    # Only Antigravity uses these effort-bearing concrete slugs. Do not guess
    # capabilities for other providers or generic model names ending in "high".
    return bool(re.fullmatch(r'(?:claude|gemini)-[a-z0-9.-]+-(?:thinking|low|medium|high|xhigh|max)', model.lower()))


def validate(config: dict, *, partial: bool = False) -> None:
    _object(config, 'configuration')
    if 'version' in config and (type(config['version']) is not int or config['version'] not in (1, 2)):
        raise ConfigError('Unsupported configuration version; expected 1 or 2')
    if 'provider_order' in config:
        _names(config['provider_order'], 'provider_order', empty=False)
    for key in ('allow_provider_fallback', 'strict_fresh_context', 'auto_cleanup', 'stream_provider_output'):
        if key in config:
            _boolean(config[key], key)
    for key, low, high in (('functional_failures_per_provider', 1, 50), ('task_timeout_seconds', 0, 604800), ('validation_timeout_seconds', 1, 604800)):
        if key in config:
            _integer(config[key], key, low, high)
    limits = _object(config.get('rate_limit', {}), 'rate_limit')
    if 'auto_wait' in limits:
        _boolean(limits['auto_wait'], 'rate_limit.auto_wait')
    for key, low in (('wait_seconds', 0), ('max_wait_cycles', 0)):
        if key in limits:
            _integer(limits[key], f'rate_limit.{key}', low, 86400)
    for tier, route in _object(config.get('tier_routes', {}), 'tier_routes').items():
        if tier not in TIER_ORDER:
            raise ConfigError(f'Unknown tier: {tier}')
        _object(route, f'tier_routes.{tier}')
        if set(route) - {'primary', 'fallbacks'} or (('primary' in route or not partial) and route.get('primary') not in PROVIDERS):
            raise ConfigError(f'tier_routes.{tier} requires a supported primary and optional fallbacks')
        fallbacks = _names(route.get('fallbacks', []), f'tier_routes.{tier}.fallbacks')
        if route.get('primary') in fallbacks:
            raise ConfigError(f'tier_routes.{tier}: primary cannot repeat in fallbacks')
    for provider in PROVIDERS:
        if provider not in config:
            continue
        cfg = _object(config[provider], provider)
        if 'command' in cfg:
            cmd = cfg['command']
            if not ((isinstance(cmd, str) and cmd.strip()) or (isinstance(cmd, list) and cmd and all(isinstance(x, str) and x.strip() for x in cmd))):
                raise ConfigError(f'{provider}.command must be a nonempty command or argv')
        for key in ('extra_args', 'models_without_effort'):
            if key in cfg and (not isinstance(cfg[key], list) or any(not isinstance(x, str) or not x.strip() for x in cfg[key])):
                raise ConfigError(f'{provider}.{key} must be an array of nonempty strings')
        for tier, model in _object(cfg.get('models', {}), f'{provider}.models').items():
            if tier not in TIER_ORDER or not isinstance(model, str) or not model.strip() or len(model) > 200 or any(c.isspace() for c in model):
                raise ConfigError(f'{provider}.models contains an invalid tier or model')
        for tier, cap in _object(cfg.get('max_effort_by_tier', {}), f'{provider}.max_effort_by_tier').items():
            if tier not in TIER_ORDER or cap not in EFFORT_ORDER:
                raise ConfigError(f'{provider}.max_effort_by_tier contains an invalid tier or effort')
        if 'retry_exit_codes' in cfg:
            for code in _names_codes(cfg['retry_exit_codes'], provider):
                _integer(code, f'{provider}.retry_exit_codes', 1, 255)
        if provider == 'antigravity' and any(embedded_effort_model(m) for m in cfg.get('models', {}).values()):
            args = cfg.get('extra_args', [])
            if any(x in ('--effort', '--reasoning-effort') or x.startswith(('--effort=', '--reasoning-effort=')) for x in args):
                raise ConfigError('Antigravity effort-bearing model IDs cannot be combined with explicit effort flags')
    availability = _object(config.get('availability', {}), 'availability')
    if set(availability) - {'cooldown_seconds', 'max_attempts_per_run'}:
        raise ConfigError('Unknown availability setting')
    for key, bounds in {'cooldown_seconds': (1, 86400), 'max_attempts_per_run': (1, 32)}.items():
        if key in availability:
            _integer(availability[key], f'availability.{key}', *bounds)
    assistant = _object(config.get('assistant', {}), 'assistant')
    if set(assistant) - set(EXTRA_DEFAULTS['assistant']):
        raise ConfigError('Unknown assistant setting')
    if 'enabled' in assistant:
        _boolean(assistant['enabled'], 'assistant.enabled')
    for key, values in (('provider', ASSISTANT_PROVIDERS), ('model_tier', TIER_ORDER), ('reasoning_effort', EFFORT_ORDER)):
        if key in assistant and assistant[key] not in values:
            raise ConfigError(f'Invalid assistant.{key}')
    for key, bounds in {'max_calls_per_task': (1, 3), 'max_calls_per_plan': (1, 32), 'max_input_chars': (512, 12000), 'max_output_chars': (256, 4000), 'timeout_seconds': (1, 120), 'repetition_threshold': (2, 20), 'unhealthy_threshold': (1, 20), 'stall_seconds': (1, 3600)}.items():
        if key in assistant:
            _integer(assistant[key], f'assistant.{key}', *bounds)
    if 'jev_model' in assistant:
        model = assistant['jev_model']
        if not isinstance(model, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]{0,99}', model):
            raise ConfigError('Invalid assistant.jev_model')
    if 'jev_min_confidence' in assistant:
        value = assistant['jev_min_confidence']
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ConfigError('assistant.jev_min_confidence must be a finite number in [0, 1]')


def _names_codes(value: Any, provider: str) -> list:
    if not isinstance(value, list) or any(type(x) is not int for x in value) or len(set(value)) != len(value):
        raise ConfigError(f'{provider}.retry_exit_codes must be distinct integers')
    return value


def load(defaults: dict, plan_path: Path | None = None, *, global_config: Path | None = None) -> dict:
    global_config = global_path() if global_config is None else global_config
    global_raw = read(global_config, optional=not bool(os.environ.get('PAE_CONFIG_PATH')))
    plan_raw = read(plan_path) if plan_path is not None else {}
    validate(global_raw, partial=True)
    validate(plan_raw, partial=True)
    # Complete v1 snapshots predate global routing. Preserve their exact explicit
    # execution policy; migrate deliberately to v2 overlays through configure.
    snapshot = plan_raw.get('version', 1) == 1 and all(p in plan_raw for p in PROVIDERS) and 'provider_order' in plan_raw
    result = merge(merge(defaults, EXTRA_DEFAULTS), {} if snapshot else global_raw)
    result = merge(result, plan_raw)
    validate(result)
    agy = result.get('antigravity', {})
    no_effort = agy.setdefault('models_without_effort', [])
    for model in agy.get('models', {}).values():
        if embedded_effort_model(model) and model not in no_effort:
            no_effort.append(model)
    return result


def plan_overlay() -> dict:
    """Empty sections retain easy manual editing without freezing the catalog."""
    return {'version': 2, 'rate_limit': {}, 'summary': {}, **{p: {} for p in PROVIDERS}}


def provider_chain(task: dict, config: dict, override: str | None = None, *, tier: str | None = None) -> list[str]:
    tier = tier or task.get('model_tier', 'standard')
    route = config.get('tier_routes', {}).get(tier)
    order = [route['primary'], *route.get('fallbacks', [])] if route else list(config.get('provider_order', ['claude', 'codex']))
    requested = override or task.get('provider', 'auto')
    if requested != 'auto':
        if requested not in PROVIDERS:
            raise ConfigError(f'Unsupported provider: {requested}')
        order = [requested, *(p for p in order if p != requested)]
    fallback = task.get('allow_provider_fallback', True) and config.get('allow_provider_fallback', True)
    return order if fallback else order[:1]
