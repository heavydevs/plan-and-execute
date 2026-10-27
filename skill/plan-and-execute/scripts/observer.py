#!/usr/bin/env python3
"""Opt-in, bounded diagnostic advice with workload fallback; never a test authority.

The supervisor and its deterministic checks work without this module. No model
receives evidence until its tool-less execution contract has been verified.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable

import assistant_triage as advice
import process_tree
import workload_routing

DEFAULTS = {'enabled': False, 'max_calls': 1, 'max_candidates': 3,
            'timeout_seconds': 30, 'max_input_chars': 6000, 'max_output_chars': 2000,
            'allow_claude_api': False}
LIMITS = {'max_calls': (1, 3), 'max_candidates': (1, 3), 'timeout_seconds': (5, 120),
          'max_input_chars': (1500, 12000), 'max_output_chars': (1000, 4000)}
CAPTURE_LIMIT = 32768
STATE_LIMIT = 24000
AGY_FLAGS = ('--input-format', '--output-format', '--agent', '--model', '--json-schema', '--print-timeout')


class ObserverError(ValueError):
    pass


class Unavailable(advice.Skip):
    def __init__(self, reason: str, *, submitted: bool = False):
        super().__init__(reason)
        self.submitted = submitted


def validate(raw: Any) -> None:
    if not isinstance(raw, dict) or set(raw) - set(DEFAULTS):
        raise ObserverError('observer must contain only documented options')
    for name in ('enabled', 'allow_claude_api'):
        if name in raw and type(raw[name]) is not bool:
            raise ObserverError(f'observer.{name} must be boolean')
    for name, (low, high) in LIMITS.items():
        if name in raw and (type(raw[name]) is not int or not low <= raw[name] <= high):
            raise ObserverError(f'observer.{name} must be an integer in [{low},{high}]')


def options(config: dict) -> dict:
    raw = config.get('observer', {})
    validate(raw)
    return {**DEFAULTS, **raw}


def routes(config: dict) -> list[dict]:
    """Monitoring has its own explicit preference, never manager-quota reordering."""
    section = config.get('workload_routing', {})
    if not section.get('enabled'):
        return []
    result = []
    for name in section.get('routes', {}).get('log_monitoring', []):
        profile = section['profiles'][name]
        if not profile.get('enabled', True):
            continue
        # The diagnostic is an economy leaf, not an excuse to spend a frontier
        # model. A user must deliberately expose that model at the economy tier.
        if profile.get('min_tier', 'economy') != 'economy':
            continue
        result.append({'provider': profile['provider'], 'model': profile['model'],
                       'tier': 'economy', 'effort': profile.get('native_effort', 'low'),
                       'requested_effort': 'low', 'route_profile': name,
                       'quota_pool': profile['quota_pool'], 'workload': 'log_monitoring'})
    return result


def clean_environment(work: Path, *, cached_auth: bool) -> dict:
    names = ('PATH', 'SYSTEMROOT', 'WINDIR', 'LANG', 'LC_ALL', 'SSL_CERT_FILE', 'SSL_CERT_DIR')
    if cached_auth:
        names += ('HOME', 'USERPROFILE', 'APPDATA', 'LOCALAPPDATA')
    env = {key: os.environ[key] for key in names if key in os.environ}
    env.update(TMPDIR=str(work), TEMP=str(work), TMP=str(work))
    # Never forward API keys, custom endpoints, NODE_OPTIONS or arbitrary CLI
    # configuration overrides to the subscription-backed observer.
    return env


def agy_startup_guard(home: Path) -> None:
    """Reject executable global customizations before even spawning the CLI.

    Inspect documented metadata only, never credential files. This is deliberately
    conservative: nonempty plugins/MCP/sidecars skip rather than auto-disable them.
    """
    paths = ('config/hooks.json', 'config/mcp_config.json', 'config/sidecars.json',
             'antigravity-cli/mcp_config.json', 'antigravity-cli/sidecars.json')
    base = home / '.gemini'
    for name in paths:
        path = base / name
        if any(p.is_symlink() for p in (base, path.parent, path)):
            raise Unavailable('global_customization_symlink')
        if path.exists():
            with path.open('rb') as source:
                raw = source.read(65537)
            if len(raw) > 65536:
                raise Unavailable('global_customizations_unverified')
            try:
                data = advice.strict_json(raw.decode('utf-8'))
            except (ValueError, UnicodeError):
                raise Unavailable('global_customizations_unverified') from None
            # An empty object is safe. Do not guess at a changing disabled schema.
            if data != {}:
                raise Unavailable('global_customizations_present')
    for name in ('config/plugins', 'antigravity-cli/plugins', 'config/sidecars'):
        path = base / name
        if any(p.is_symlink() for p in (path.parent, path)):
            raise Unavailable('global_customization_symlink')
        if path.exists() and (not path.is_dir() or next(path.iterdir(), None) is not None):
            raise Unavailable('global_customizations_present')


def agy_stream(argv: list[str], prompt: str, work: Path, env: dict, model: str,
               agent: str, timeout: float) -> dict:
    """One prompt after a verified init; bounded stdout/stderr and process tree.

    A mismatched/old CLI receives no evidence. Runtime data is never executed.
    The native CLI is a trusted executable, not an OS sandbox against that CLI.
    """
    events: queue.Queue = queue.Queue(maxsize=64)
    overflow = threading.Event()
    total = [0]
    total_lock = threading.Lock()
    submitted = False
    input_done = threading.Event()
    input_failed = threading.Event()
    process = process_tree.launch(argv, cwd=work, env=env, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 start_new_session=True)

    def drain(stream, parse: bool) -> None:
        buffer = b''
        try:
            while block := stream.read1(4096):
                with total_lock:
                    total[0] += len(block)
                    if total[0] > CAPTURE_LIMIT:
                        overflow.set()
                if overflow.is_set():
                    continue  # Keep pipes drained until the owning thread kills.
                if parse:
                    buffer += block
                    while b'\n' in buffer:
                        line, _, buffer = buffer.partition(b'\n')
                        try:
                            item = advice.strict_json(line.decode('utf-8'))
                        except (ValueError, UnicodeError):
                            item = {'event': 'invalid'}
                        try:
                            events.put_nowait(item)
                        except queue.Full:
                            overflow.set()
            if parse and buffer.strip():
                try:
                    events.put_nowait({'event': 'invalid'})
                except queue.Full:
                    overflow.set()
        except (OSError, ValueError):
            overflow.set()
        finally:
            if parse:
                try:
                    events.put_nowait({'event': 'eof'})
                except queue.Full:
                    overflow.set()

    threads = [threading.Thread(target=drain, args=(process.stdout, True), daemon=True),
               threading.Thread(target=drain, args=(process.stderr, False), daemon=True)]
    for thread in threads:
        thread.start()
    def submit(message: bytes) -> None:
        # Pipes can fill even for bounded input (especially on Windows). A bad
        # CLI must not stall the deadline-owning thread while receiving data.
        try:
            process.stdin.write(message)
            process.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            input_failed.set()
        finally:
            input_done.set()

    deadline = time.monotonic() + timeout
    init_deadline = min(deadline, time.monotonic() + 5)
    initialized = False
    try:
        while True:
            if overflow.is_set():
                raise Unavailable('output_limit', submitted=submitted)
            if input_failed.is_set():
                raise Unavailable('input_pipe_failed', submitted=submitted)
            now = time.monotonic()
            if now >= deadline or (not initialized and now >= init_deadline):
                raise Unavailable('timeout', submitted=submitted)
            try:
                item = events.get(timeout=min(.1, deadline - now))
            except queue.Empty:
                continue
            if not isinstance(item, dict):
                raise Unavailable('invalid_protocol', submitted=submitted)
            kind = item.get('event')
            if not initialized:
                init = item.get('init') or {}
                if (kind != 'init' or not isinstance(init, dict) or init.get('tools') != []
                        or init.get('model') != model or init.get('agent') != agent
                        or init.get('permission_mode') != 'request-review'
                        or not isinstance(init.get('cwd'), str) or Path(init['cwd']).resolve() != work.resolve()):
                    raise Unavailable('tool_less_init_unverified')
                initialized = True
                message = advice.dumps({'event': 'user', 'message': {'content': prompt}}) + '\n'
                submitted = True  # Reserve conservatively before a partial pipe write.
                writer = threading.Thread(target=submit, args=(message.encode('utf-8'),), daemon=True)
                threads.append(writer)
                writer.start()
                continue
            if kind == 'step_update':
                step = item.get('step_update')
                if not isinstance(step, dict) or step.get('step_type') not in ('user_input', 'agent_response', 'checkpoint'):
                    raise Unavailable('unexpected_tool_or_step', submitted=submitted)
            elif kind == 'result':
                if not input_done.wait(max(0, min(.1, deadline - time.monotonic()))) or input_failed.is_set():
                    raise Unavailable('input_pipe_failed', submitted=submitted)
                result = item.get('result') or {}
                if not isinstance(result, dict) or result.get('status') != 'SUCCESS':
                    # The only retained result is a fixed category, never raw errors.
                    import availability
                    category = availability.classify(1, advice.dumps(result), []) or 'provider_error'
                    raise Unavailable(category, submitted=submitted)
                return result.get('structured_output')
            else:
                raise Unavailable('invalid_protocol', submitted=submitted)
    finally:
        process_tree.terminate(process)
        for thread in threads:
            thread.join(timeout=1)
        for stream in (process.stdin, process.stdout, process.stderr):
            try:
                stream.close()
            except (OSError, ValueError):
                pass
        process_tree.close(process)


def native_invoke(config: dict, route: dict, prompt: str, refs: set[str], timeout: float) -> dict:
    """Only audited tool-less adapters. Unsupported hosts fail closed, not writable."""
    provider = route['provider']
    opt = options(config)
    if provider == 'claude':
        if not opt['allow_claude_api']:
            raise Unavailable('claude_api_billing_not_enabled')
        actual = copy.deepcopy(config)
        actual['assistant'] = {**actual.get('assistant', {}), 'provider': 'claude', 'model_tier': 'economy',
            'reasoning_effort': route['effort'], 'timeout_seconds': timeout, 'idle_timeout_seconds': 0}
        actual['claude'] = copy.deepcopy(config.get('claude', {}))
        actual['claude'].setdefault('models', {})['economy'] = route['model']
        return advice.native_invoke(actual, prompt, refs)
    if provider != 'antigravity':
        raise Unavailable('unsupported_tool_less_adapter')
    raw_command = config.get('antigravity', {}).get('command', 'agy')
    if isinstance(raw_command, list) and len(raw_command) == 1:
        raw_command = raw_command[0]
    if not isinstance(raw_command, str) or Path(raw_command).name.lower() not in ('agy', 'agy.exe'):
        raise Unavailable('unsupported_command_wrapper')
    executable = shutil.which(raw_command)
    if not executable:
        raise Unavailable('cli_not_installed')
    agy_startup_guard(Path.home())
    deadline = time.monotonic() + timeout
    with tempfile.TemporaryDirectory(prefix='pae-observer-') as tmp:
        work = Path(tmp)
        agent = 'pae-observer-' + hashlib.sha256(tmp.encode()).hexdigest()[:16]
        folder = work / '.agents' / 'agents'
        folder.mkdir(parents=True)
        (folder / f'{agent}.md').write_text(
            f'---\nname: {agent}\ndescription: Diagnose only the supplied log evidence\n'
            'tools: []\nmainAgent: true\nsubagent: false\nmodel: inherit\n'
            "commandExecutionPolicy: 'off'\nmcpServers: []\nskills: []\nplugins: []\n---\n"
            + advice.SYSTEM + '\n', encoding='utf-8')
        env = clean_environment(work, cached_auth=True)
        help_text = advice.bounded_process([executable, '--help'], '', work, env, min(3, timeout), 65536)
        if any(flag not in help_text for flag in AGY_FLAGS):
            raise Unavailable('cli_capabilities_unverified')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise Unavailable('timeout')
        argv = [executable, '--input-format', 'stream-json', '--output-format', 'stream-json',
                '--agent', agent, '--model', route['model'], '--json-schema', advice.dumps(advice.schema(refs)),
                '--print-timeout', f'{max(1, int(remaining))}s']
        return agy_stream(argv, prompt, work, env, route['model'], agent, remaining)


def load_state(path: Path) -> dict:
    if path.is_symlink() or path.parent.is_symlink():
        raise ObserverError('Unsafe observer state path')
    if not path.exists():
        return {'version': 1, 'requests': []}
    with path.open('rb') as source:
        raw = source.read(STATE_LIMIT + 1)
    value = advice.strict_json(raw.decode('utf-8'))
    if (len(raw) > STATE_LIMIT or not isinstance(value, dict) or set(value) != {'version', 'requests'}
            or value['version'] != 1 or not isinstance(value['requests'], list) or len(value['requests']) > 3):
        raise ObserverError('Invalid observer state')
    for item in value['requests']:
        allowed = {'signature', 'status', 'attempts', 'failure_counter', 'advice'}
        if (not isinstance(item, dict) or set(item) - allowed
                or not re.fullmatch(r'[0-9a-f]{64}', str(item.get('signature', '')))
                or item.get('status') not in ('reserved', 'advice', 'skipped', 'interrupted')
                or type(item.get('failure_counter')) is not int or item['failure_counter'] < 0
                or not isinstance(item.get('attempts'), list) or len(item['attempts']) > 3):
            raise ObserverError('Invalid observer request')
        for attempt in item['attempts']:
            if (not isinstance(attempt, dict)
                    or set(attempt) - {'provider', 'route_profile', 'model', 'quota_pool', 'status', 'reason'}
                    or not all(isinstance(attempt.get(key), str) and len(attempt[key]) <= 160
                               for key in ('provider', 'route_profile', 'model', 'quota_pool'))
                    or attempt.get('status') not in ('reserved', 'advice', 'skipped', 'invalid', 'interrupted')
                    or ('reason' in attempt and not re.fullmatch(r'[a-z_]{1,64}', str(attempt['reason'])))):
                raise ObserverError('Invalid observer attempt')
    return value


def diagnose(config: dict, prompt: str, refs: set[str], signature: str, path: Path,
             *, failure_counter: int = 0, invoke: Callable | None = None) -> dict:
    """Explicit anomaly only. Atomic reservation, duplicate suppression and one total deadline.

    The caller owns the state directory and the deterministic eligibility gate.
    Success is advice, never permission to change a manifest, route or acceptance.
    """
    opt = options(config)
    if not opt['enabled']:
        return {'status': 'skipped', 'reason': 'disabled'}
    if len(prompt) > opt['max_input_chars'] or not re.fullmatch('[0-9a-f]{64}', signature):
        raise ObserverError('Invalid evidence budget or signature')
    if path.is_symlink() or path.parent.is_symlink() or not path.parent.is_dir():
        raise ObserverError('Unsafe observer state directory')
    lock = path.with_suffix('.lock')
    owned = False
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        owned = True
        state = load_state(path)
        if any(r['signature'] == signature for r in state['requests']):
            return {'status': 'skipped', 'reason': 'duplicate_evidence'}
        if len(state['requests']) >= opt['max_calls']:
            return {'status': 'skipped', 'reason': 'attempt_budget'}
        candidates = routes(config)[:opt['max_candidates']]
        if not candidates:
            return {'status': 'skipped', 'reason': 'no_monitoring_profiles'}
        request = {'signature': signature, 'status': 'reserved', 'attempts': [], 'failure_counter': failure_counter}
        state['requests'].append(request)
        advice.write_state(path, state)
        deadline = time.monotonic() + opt['timeout_seconds']
        blocked: set[str] = set()
        for route in candidates:
            if any(key in blocked for key in workload_routing.cooldown_keys(route)):
                continue
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            attempt = {key: route[key] for key in ('provider', 'route_profile', 'model', 'quota_pool')}
            attempt['status'] = 'reserved'
            request['attempts'].append(attempt)
            advice.write_state(path, state)  # Persist BEFORE even probing a model.
            try:
                raw = (invoke or native_invoke)(config, route, prompt, refs, remaining)
                parsed = advice.validate_advice(raw, refs, opt['max_output_chars'])
                attempt['status'] = 'advice'
                request.update(status='advice', advice=parsed)
                advice.write_state(path, state)
                return {'status': 'advice', 'route_profile': route['route_profile'], 'advice': parsed,
                        'authoritative': False, 'attempts': len(request['attempts'])}
            except advice.Skip as exc:
                reason = str(exc)
                # All native reasons are fixed enums; injected adapters still
                # cannot store arbitrary provider output or secrets here.
                reason = reason if re.fullmatch(r'[a-z_]{1,64}', reason) else 'provider_error'
                attempt.update(status='skipped', reason=reason)
                if reason in ('quota', 'capacity', 'authentication', 'missing_cli'):
                    blocked.add(workload_routing.cooldown_key(route, reason))
            except KeyboardInterrupt:
                attempt['status'] = 'interrupted'
                request['status'] = 'interrupted'
                advice.write_state(path, state)
                raise
            except (ValueError, TypeError, KeyError, OSError, RecursionError):
                attempt.update(status='invalid', reason='invalid_or_failed_advice')
            advice.write_state(path, state)
        request['status'] = 'skipped'
        advice.write_state(path, state)
        return {'status': 'skipped', 'reason': 'no_safe_available_observer', 'attempts': request['attempts']}
    except FileExistsError:
        return {'status': 'skipped', 'reason': 'observer_locked'}
    finally:
        if owned:
            lock.unlink(missing_ok=True)


def plan_path(plan: Path, task_id: str) -> Path:
    return advice.state_path(plan, task_id).with_name(f'{task_id}-observer.json')


def triage_plan(plan: Path, task: dict, results: list[dict], config: dict) -> dict:
    opt = options(config)
    triggers = {**config.get('assistant', {}), 'enabled': opt['enabled']}
    reason, failed = advice.trigger(task, results, triggers)
    if not reason:
        return {'status': 'skipped', 'reason': 'not_eligible'}
    prompt, refs, signature = advice.evidence(task, failed, reason, opt['max_input_chars'])
    return diagnose(config, prompt, refs, signature, plan_path(plan, str(task['id'])),
                    failure_counter=task.get('functional_failures', 0))


def hint(plan: Path, task: dict, config: dict) -> str:
    if not options(config)['enabled'] or not task.get('last_error'):
        return ''
    try:
        state = load_state(plan_path(plan, str(task['id'])))
        item = next((r for r in reversed(state['requests']) if r.get('status') == 'advice'), None)
        if item and item.get('failure_counter') == task.get('functional_failures', 0):
            result = advice.validate_advice(item['advice'], {'E1', 'E2', 'E3'}, options(config)['max_output_chars'])
            return '\nUnverified diagnostic data; verify independently:\n' + advice.dumps(result) + '\n'
    except (ObserverError, advice.Skip, OSError, ValueError, TypeError, KeyError):
        pass
    return ''
