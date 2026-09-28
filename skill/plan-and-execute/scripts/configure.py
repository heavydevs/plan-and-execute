#!/usr/bin/env python3
"""Sequential, non-generative routing setup. Questions are independent of the UI."""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import routing_config as rc
import routingctl
import planctl
from run_isolated import command_prefix


class Cancelled(Exception):
    """No configuration has been saved."""


@dataclass(frozen=True)
class Question:
    id: str
    prompt: str
    choices: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {'id': self.id, 'prompt': self.prompt, 'choices': list(self.choices)}


def terminal_ask(question: Question, *, read=input, write=print) -> str:
    """A host can replace this function with its own single-choice renderer."""
    while True:
        write(question.prompt)
        for i, choice in enumerate(question.choices, 1):
            write(f'  {i}. {choice}')
        try:
            value = read('Numero (q cancela): ' if question.choices else 'Valor (q cancela): ').strip()
        except (EOFError, KeyboardInterrupt):
            raise Cancelled from None
        if value.lower() in ('q', 'quit'):
            raise Cancelled
        if not question.choices:
            if value:
                return value
        elif value.isdigit() and 1 <= int(value) <= len(question.choices):
            return question.choices[int(value) - 1]
        write('Escolha invalida; responda somente a esta pergunta.')


def discover(config: dict, *, which=shutil.which, probe=subprocess.run) -> dict:
    """Probe only documented status commands; never generate text or read secrets."""
    result = {}
    for provider in rc.PROVIDERS:
        prefix = command_prefix(config[provider]['command'])
        installed = bool(which(prefix[0]))
        auth = 'unknown' if installed else 'not_installed'
        # A custom wrapper may interpret arguments differently. Do not probe it.
        native = len(prefix) == 1 and Path(prefix[0]).stem.lower() in (provider, provider + '.exe')
        args = {'claude': ['auth', 'status'], 'codex': ['login', 'status']}.get(provider)
        if installed and native and args:
            try:
                status = probe(prefix + args, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=3, check=False).returncode
                auth = 'authenticated' if status == 0 else ('unauthenticated' if status == 1 else 'unknown')
            except (OSError, subprocess.TimeoutExpired):
                auth = 'unknown'
        result[provider] = {'installed': installed, 'authentication': auth}
    return result


def _ask(ask: Callable[[Question], str], id: str, prompt: str, choices=()) -> str:
    choices = tuple(choices)
    answer = ask(Question(id, prompt, choices))
    if choices and answer not in choices:
        raise rc.ConfigError(f'Invalid answer for {id}')
    return answer


def wizard(config: dict, installed: dict, ask: Callable[[Question], str]) -> dict:
    """Return only selected overrides. No writes, implicit logins, or generation."""
    ready = []
    for p in rc.PROVIDERS:
        status = installed.get(p, {})
        if not status.get('installed'):
            continue
        auth = status.get('authentication')
        if auth == 'authenticated':
            ready.append(p)
        elif auth == 'unknown' and _ask(ask, f'auth.{p}',
                f'{p}: autenticacao desconhecida. Voce confirmou o login nesta CLI?', ('Nao', 'Sim')) == 'Sim':
            ready.append(p)
    if not ready:
        raise rc.ConfigError('Nenhuma CLI autenticada disponivel. Instale e autentique um provedor antes de configurar.')
    result = {'version': 2, 'tier_routes': {}}
    selected = set()
    for tier in rc.TIER_ORDER:
        primary = _ask(ask, f'{tier}.primary', f'{tier}: provedor principal?', ready)
        remaining = [p for p in ready if p != primary]
        fallbacks = []
        while remaining:
            p = _ask(ask, f'{tier}.fallback.{len(fallbacks) + 1}',
                     f'{tier}: proximo fallback (ordem de tentativa)?', ['Concluir', *remaining])
            if p == 'Concluir':
                break
            fallbacks.append(p)
            remaining.remove(p)
        result['tier_routes'][tier] = {'primary': primary, 'fallbacks': fallbacks}
        selected.update((p, tier) for p in [primary, *fallbacks])
    enabled = _ask(ask, 'assistant.enabled',
                   'Ativar conselho de diagnostico? Envia evidencia limitada/redigida; seguranca nao suportada resulta em skip.',
                   ('Nao', 'Sim')) == 'Sim'
    result['assistant'] = {'enabled': enabled}
    if enabled:
        preferred = sorted(ready, key=lambda p: (p != config['assistant']['provider'], ready.index(p)))
        provider = _ask(ask, 'assistant.provider', 'Provedor do assistente? Somente Claude bare/tool-less e suportado; exige ANTHROPIC_API_KEY e cobra na API, nao na assinatura. Outros perfis resultam em skip.', preferred)
        result['assistant']['provider'] = provider
        selected.add((provider, config['assistant']['model_tier']))
    for provider, tier in sorted(selected, key=lambda x: (rc.PROVIDERS.index(x[0]), rc.TIER_ORDER.index(x[1]))):
        previous = config[provider]['models'][tier]
        choices = list(dict.fromkeys([previous, *config[provider]['models'].values()])) + ['Outro ID']
        model = _ask(ask, f'{provider}.{tier}.model',
                     f'{provider}/{tier}: modelo? Catalogo local, nao comprova acesso; agy models lista IDs atuais.', choices)
        if model == 'Outro ID':
            model = _ask(ask, f'{provider}.{tier}.model_id', 'ID exato do modelo confirmado na CLI:')
        # Validate a manual ID before exposing it in another terminal prompt.
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/+-]{0,199}', model):
            raise rc.ConfigError('Invalid model ID; use the exact CLI identifier without spaces or controls')
        entry = result.setdefault(provider, {'models': {}})
        entry['models'][tier] = model
        cap = config[provider]['max_effort_by_tier'][tier]
        cap = _ask(ask, f'{provider}.{tier}.effort_cap',
                   f'{provider}/{tier}: esforco maximo suportado por este modelo?',
                   list(dict.fromkeys([cap, *rc.EFFORT_ORDER])))
        entry.setdefault('max_effort_by_tier', {})[tier] = cap
        if provider == 'antigravity':
            no_effort = entry.setdefault('models_without_effort', list(config[provider].get('models_without_effort', [])))
            embedded = rc.embedded_effort_model(model)
            if embedded or model in no_effort:
                omit = True
            else:
                omit = _ask(ask, f'{provider}.{tier}.omit_effort',
                            'Este ID exige omitir --effort (por exemplo, esforco embutido)?', ('Nao', 'Sim')) == 'Sim'
            if omit and model not in no_effort:
                no_effort.append(model)
    rc.validate(rc.merge(config, result))
    return result


def safe_path(path: Path) -> Path:
    """Refuse symlinks, including parents, rather than overwrite through a link."""
    path = Path(os.path.abspath(path.expanduser()))
    for p in (path, *path.parents):
        if p.is_symlink():
            raise rc.ConfigError(f'Refusing symlink configuration path: {p}')
    if path.exists() and not path.is_file():
        raise rc.ConfigError('Configuration target is not a regular file')
    return path


def snapshot(path: Path) -> bytes | None:
    path = safe_path(path)
    try:
        with path.open('rb') as f:
            data = f.read(rc.MAX_CONFIG_BYTES + 1)
    except FileNotFoundError:
        return None
    if len(data) > rc.MAX_CONFIG_BYTES:
        raise rc.ConfigError('Configuration exceeds size limit')
    return data


def save(path: Path, value: dict, expected: bytes | None) -> None:
    """Atomic replacement + concurrent-wizard lock + optimistic external-edit check."""
    rc.validate(value, partial=True)
    payload = (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    if len(payload) > rc.MAX_CONFIG_BYTES:
        raise rc.ConfigError('Configuration exceeds size limit')
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_path(path)
    lock = path.with_name(path.name + '.configure.lock')
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise rc.ConfigError('Configuration is locked; resolve an interrupted/concurrent wizard before saving') from None
    tmp = None
    try:
        os.close(fd)
        if snapshot(path) != expected:
            raise rc.ConfigError('Configuration changed during setup; restart and reconcile')
        fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
        tmp = Path(name)
        with os.fdopen(fd, 'wb') as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        # Recheck immediately before replacement; arbitrary editors do not share our lock.
        if snapshot(path) != expected:
            raise rc.ConfigError('Configuration changed during setup; restart and reconcile')
        os.replace(tmp, path)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)


def summary(config: dict) -> dict:
    """Allowlisted summary: never echo credentials, raw commands, or extra args."""
    return {'tier_routes': copy.deepcopy(config.get('tier_routes', {})),
            'models': {p: copy.deepcopy(config[p].get('models', {})) for p in rc.PROVIDERS},
            'assistant': copy.deepcopy(config['assistant'])}


def configure(path: Path, *, plan: bool = False, dry_run: bool = False, show: bool = False,
              ask=terminal_ask, discover_fn=discover, write=print) -> dict:
    path = safe_path(path)
    before = snapshot(path)
    raw = rc.read(path) if before is not None else {}
    defaults = routingctl.install_current_model_catalog(planctl).default_config()
    # A missing explicit setup destination is valid even when PAE_CONFIG_PATH is set.
    if plan:
        if not path.parent.is_dir() or not (path.parent / planctl.MANIFEST).is_file():
            raise rc.ConfigError('--plan must name an existing plan with a manifest')
        inherited = rc.load(defaults, global_config=rc.global_path())
        snapshot_v1 = raw.get('version', 1) == 1 and all(p in raw for p in rc.PROVIDERS) and 'provider_order' in raw
        if snapshot_v1:
            inherited = rc.merge(defaults, rc.EXTRA_DEFAULTS)
    else:
        inherited = rc.merge(defaults, rc.EXTRA_DEFAULTS)
    effective = rc.merge(inherited, raw)
    rc.validate(effective)
    if show:
        output = {'path': str(path), **summary(effective)}
        write(json.dumps(output, indent=2, ensure_ascii=False))
        return output
    overrides = wizard(effective, discover_fn(effective), ask)
    value = rc.merge(raw, overrides)
    # Preserve unrelated explicit values; only selected routing settings change.
    resolved = rc.merge(inherited, value)
    rc.validate(resolved)
    write(json.dumps({'path': str(path), **summary(resolved)}, indent=2, ensure_ascii=False))
    if not dry_run:
        if _ask(ask, 'save', 'Gravar esta configuracao? (credenciais e acesso a modelos nao sao garantidos)', ('Nao', 'Sim')) != 'Sim':
            raise Cancelled
        save(path, value, before)
        write(f'Configuracao salva: {path}')
    return value


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--config', type=Path, help='Configuration file; default is user-global')
    group.add_argument('--plan', type=Path, help='Existing plan directory; save an explicit per-plan overlay')
    parser.add_argument('--show', action='store_true', help='Show allowlisted effective configuration; no probing')
    parser.add_argument('--json', action='store_true', help='With --show only')
    parser.add_argument('--dry-run', action='store_true', help='Ask and preview without saving')
    args = parser.parse_args(argv)
    if args.json and not args.show:
        parser.error('--json requires --show; interactive questions are separate')
    path = args.plan / planctl.CONFIG if args.plan else args.config or rc.global_path()
    try:
        configure(path, plan=bool(args.plan), dry_run=args.dry_run, show=args.show)
        return 0
    except Cancelled:
        print('Configuracao cancelada; arquivo inalterado.')
        return 130
    except (rc.ConfigError, OSError, ValueError) as exc:
        print(f'Configuration error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
