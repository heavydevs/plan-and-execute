import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'plan-and-execute.js');
const packageVersion = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8')).version;

function temporaryDirectory() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'plan-and-execute-cli-'));
}

function run(args, options = {}) {
  return spawnSync(process.execPath, [cli, ...args], {
    cwd: root,
    encoding: 'utf8',
    ...options
  });
}

test('help advertises selective/explicit activation and every execution provider', () => {
  const result = run(['--help']);
  assert.equal(result.status, 0, result.stderr);
  for (const provider of ['claude', 'codex', 'antigravity', 'gemini', 'qwen', 'kimi', 'trae']) {
    assert.match(result.stdout, new RegExp(`\\b${provider}\\b`));
  }
  assert.match(result.stdout, /install \[claude\|codex\|both\]/);
  assert.match(result.stdout, /--activation <selective\|explicit>/);
  assert.match(result.stdout, /tarefas pequenas\/medias coesas ficam no agente atual/);
  assert.match(result.stdout, /tutorial rapido continuam restritos a Claude Code e Codex/);
});

test('provider override accepts supported backends and rejects unknown names before execution', () => {
  const workspace = temporaryDirectory();
  try {
    for (const provider of ['claude', 'codex', 'antigravity', 'gemini', 'qwen', 'kimi', 'trae']) {
      const result = run(['current', '--cwd', workspace, '--provider', provider, '--json']);
      assert.equal(result.status, 0, `${provider}: ${result.stderr}`);
      assert.equal(JSON.parse(result.stdout).status, 'idle');
    }
    const invalid = run(['current', '--cwd', workspace, '--provider', 'unknown']);
    assert.equal(invalid.status, 2);
    assert.match(invalid.stderr, /Provedor invalido/);
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('CLI installs explicit variants, reports activation, and returns to selective without force', () => {
  const workspace = temporaryDirectory();
  try {
    const install = run(['install', 'both', '--cwd', workspace, '--activation', 'explicit', '--json']);
    assert.equal(install.status, 0, install.stderr);
    const installed = JSON.parse(install.stdout);
    assert.deepEqual(installed.map((item) => item.agent), ['claude', 'codex']);
    assert.ok(installed.every((item) => item.activation === 'explicit'));

    const claudeSkill = fs.readFileSync(
      path.join(workspace, '.claude', 'skills', 'plan-and-execute', 'SKILL.md'), 'utf8'
    );
    const codexMetadata = fs.readFileSync(
      path.join(workspace, '.agents', 'skills', 'plan-and-execute', 'agents', 'openai.yaml'), 'utf8'
    );
    assert.match(claudeSkill, /^disable-model-invocation:\s*true$/m);
    assert.match(codexMetadata, /allow_implicit_invocation:\s*false/);

    const status = run(['status', 'both', '--cwd', workspace, '--json']);
    assert.equal(status.status, 0, status.stderr);
    assert.ok(JSON.parse(status.stdout).every((item) => item.managed && !item.modified));
    assert.ok(JSON.parse(status.stdout).every((item) => item.activation === 'explicit'));

    const switchMode = run(['install', 'both', '--cwd', workspace, '--selective', '--json']);
    assert.equal(switchMode.status, 0, switchMode.stderr);
    assert.ok(JSON.parse(switchMode.stdout).every((item) => item.action === 'updated'));

    const optionalInstall = run(['install', 'gemini', '--cwd', workspace]);
    assert.equal(optionalInstall.status, 2);
    assert.match(optionalInstall.stderr, /Argumento desconhecido|Agente invalido/);

    const remove = run(['uninstall', 'both', '--cwd', workspace, '--json']);
    assert.equal(remove.status, 0, remove.stderr);
    assert.ok(JSON.parse(remove.stdout).every((item) => item.action === 'uninstalled'));
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('CLI rejects invalid activation before touching destination', () => {
  const workspace = temporaryDirectory();
  try {
    const invalid = run(['install', 'claude', '--cwd', workspace, '--activation', 'always']);
    assert.equal(invalid.status, 2);
    assert.match(invalid.stderr, /Modo de ativacao invalido/);
    assert.equal(fs.existsSync(path.join(workspace, '.claude')), false);
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('doctor and version output are automation friendly', () => {
  const version = run(['--version']);
  assert.equal(version.status, 0, version.stderr);
  assert.equal(version.stdout.trim(), packageVersion);

  const doctor = run(['doctor', '--json']);
  assert.equal(doctor.status, 0, doctor.stderr);
  const report = JSON.parse(doctor.stdout);
  assert.deepEqual(report.executionProviders, ['claude', 'codex', 'antigravity', 'gemini', 'qwen', 'kimi', 'trae']);
  assert.deepEqual(report.defaultProviderOrder, ['claude', 'codex']);
  assert.deepEqual(report.standardInstallTargets, ['claude', 'codex']);
  assert.deepEqual(report.activationModes, ['selective', 'explicit']);
  assert.equal(report.defaultActivation, 'selective');
  for (const provider of ['antigravity', 'gemini', 'qwen', 'kimi', 'trae']) {
    assert.ok(Object.hasOwn(report, provider));
  }
});

const scriptsDir = path.join(root, 'skill', 'plan-and-execute', 'scripts');

function python(args, options = {}) {
  const candidates = process.platform === 'win32' ? [['py', ['-3']], ['python', []], ['python3', []]] : [['python3', []], ['python', []]];
  for (const [command, prefix] of candidates) {
    const result = spawnSync(command, [...prefix, ...args], { encoding: 'utf8', windowsHide: true, ...options });
    if (!(result.error && result.error.code === 'ENOENT')) return result;
  }
  throw new Error('python not found');
}

const FIXTURE = [
  'import json, os, sys',
  'from datetime import datetime, timedelta, timezone',
  'from pathlib import Path',
  `sys.path.insert(0, ${JSON.stringify(scriptsDir)})`,
  'import lifecyclectl_concise, lifecyclectl, model_catalog as mc, model_catalogctl as mcc',
  'from planctl_concise import planctl',
  'from self_test import sample_spec',
  'repo, cache, age = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])',
  'spec = sample_spec()',
  'for t in spec["tasks"]:',
  '    t["model_tier"], t["provider"] = "standard", "auto"',
  'os.environ[mcc.ENV_CACHE_DIR] = str(cache)',
  'plan = planctl.create_plan(repo, spec, ".ai-work", "p")',
  '_, manifest = planctl.load_plan(plan)',
  'lifecyclectl.write_active(plan, manifest)',
  'overlay = {"version": 2, "model_resolution": "snapshot", "kimi": {"command": [sys.executable, "-c", "raise SystemExit(1)"]}}',
  '(plan / planctl.CONFIG).write_text(json.dumps(overlay), encoding="utf-8")',
  'store = mcc.CatalogStore(cache)',
  'observed = store.now() - timedelta(days=age)',
  'record = mcc.bootstrap_record("claude", observed)',
  'record["provider"], record["catalog_version"] = "kimi", "kimi-test"',
  'for entry in record["models"].values():',
  '    for facet in mc.FACETS:',
  '        entry[facet]["observed_at"] = mcc._iso(observed)',
  'store.write("kimi", record)',
  'print(plan)'
].join('\n');

function planFixture(workspace, cache, ageDays) {
  const result = python(['-c', FIXTURE, workspace, cache, String(ageDays)]);
  assert.equal(result.status, 0, result.stderr);
  return result.stdout.trim();
}

function envFor(cache, extra = {}) {
  return { ...process.env, PAE_MODEL_CATALOG_CACHE: cache, PYTHONIOENCODING: 'utf-8', ...extra };
}

test('help lists models, profile setup and the profile providers', () => {
  const result = run(['--help']);
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /pae models status/);
  assert.match(result.stdout, /pae models refresh --provider/);
  assert.match(result.stdout, /pae configure --profile/);
  for (const provider of ['muse', 'glm', 'deepseek']) assert.match(result.stdout, new RegExp(`\\b${provider}\\b`));
});

test('provider flag accepts muse, glm and deepseek and models validates its action', () => {
  const workspace = temporaryDirectory();
  try {
    for (const provider of ['muse', 'glm', 'deepseek']) {
      const result = run(['current', '--cwd', workspace, '--provider', provider, '--json']);
      assert.equal(result.status, 0, `${provider}: ${result.stderr}`);
    }
    const bad = run(['models', 'explode']);
    assert.equal(bad.status, 2);
    assert.match(bad.stderr, /Argumento desconhecido/);
    const noTarget = run(['models', 'refresh', '--cwd', workspace]);
    assert.notEqual(noTarget.status, 0);
    assert.match(noTarget.stderr, /--provider ou --plan/);
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('doctor reports no optional provider profile by default and never leaks credentials', () => {
  const workspace = temporaryDirectory();
  const config = path.join(workspace, 'orchestrator.config.json');
  const cache = path.join(workspace, 'c');
  try {
    const baseline = run(['doctor', '--json', '--config', config], { env: envFor(cache) });
    assert.equal(baseline.status, 0, baseline.stderr);
    const empty = JSON.parse(baseline.stdout);
    assert.deepEqual(empty.routingProfiles.configured, []);
    assert.deepEqual(empty.routingProfiles.providers, {});
    assert.deepEqual(empty.defaultProviderOrder, ['claude', 'codex']);

    const setup = run(['configure', '--profile', 'glm', '--config', config], { env: envFor(cache) });
    assert.equal(setup.status, 0, setup.stderr);
    const secret = 'sk-never-print-this';
    const report = run(['doctor', '--json', '--config', config], {
      env: envFor(cache, { ZAI_API_KEY: secret, ZAI_BASE_URL: 'https://secret.example.invalid' })
    });
    assert.equal(report.status, 0, report.stderr);
    assert.ok(!report.stdout.includes(secret) && !report.stdout.includes('secret.example'));
    const glm = JSON.parse(report.stdout).routingProfiles.providers.glm;
    assert.deepEqual(Object.keys(glm).sort(), [
      'base_url_env', 'base_url_set', 'catalog', 'command', 'command_found', 'harness', 'token_env', 'token_set'
    ]);
    assert.equal(glm.token_env, 'ZAI_API_KEY');
    assert.equal(glm.token_set, true);
    assert.equal(glm.harness, 'claude');

    const unset = run(['doctor', '--json', '--config', config], { env: envFor(cache, { ZAI_API_KEY: '' }) });
    assert.equal(JSON.parse(unset.stdout).routingProfiles.providers.glm.token_set, false);

    const shown = run(['configure', '--show', '--json', '--config', config], { env: envFor(cache) });
    assert.equal(shown.status, 0, shown.stderr);
    assert.equal(JSON.parse(shown.stdout).profiles.glm.token_env, 'ZAI_API_KEY');

    const deepseek = run(['configure', '--profile', 'deepseek', '--harness', 'codex', '--config', config], { env: envFor(cache) });
    assert.equal(deepseek.status, 0, deepseek.stderr);
    assert.equal(JSON.parse(fs.readFileSync(config, 'utf8')).profiles.deepseek.harness, 'codex');
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('models status, show and refresh --plan print stable output and the digest change', () => {
  const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'pae-m-'));
  const cache = path.join(workspace, 'c');
  const env = envFor(cache);
  try {
    const status = run(['models', 'status', '--json', '--cache-dir', cache], { env });
    assert.equal(status.status, 0, status.stderr);
    assert.ok(Object.hasOwn(JSON.parse(status.stdout).providers, 'claude'));
    const show = run(['models', 'show', '--provider', 'claude', '--cache-dir', cache], { env });
    assert.equal(show.status, 0, show.stderr);
    assert.ok(JSON.parse(show.stdout).digest);

    const plan = planFixture(workspace, cache, 0);
    const diff = run(['models', 'diff', '--plan', plan, '--cache-dir', cache], { env });
    assert.equal(diff.status, 0, diff.stderr);
    assert.deepEqual(JSON.parse(diff.stdout).models_removed, []);
    const refresh = run(['models', 'refresh', '--plan', plan, '--cache-dir', cache], { env });
    assert.equal(refresh.status, 0, refresh.stderr);
    assert.match(refresh.stdout, /Digest: [0-9a-f]{64} -> [0-9a-f]{64} \((inalterado|alterado)\)/);
    const json = run(['models', 'refresh', '--plan', plan, '--cache-dir', cache, '--json'], { env });
    assert.ok(JSON.parse(json.stdout).new_digest);
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('resume --provider absent from the snapshot: fresh catalog proceeds, stale one fails with guidance (HD002)', () => {
  for (const [age, fresh] of [[0, true], [400, false]]) {
    const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'pae-r-'));
    const cache = path.join(workspace, 'c');
    try {
      const plan = planFixture(workspace, cache, age);
      const matrixPath = path.join(plan, 'MODEL_MATRIX.json');
      const before = fs.readFileSync(matrixPath, 'utf8');
      const result = run(['resume', '--cwd', workspace, '--provider', 'kimi', '--once', '--no-wait', '--no-cleanup'], {
        env: envFor(cache), timeout: 120000
      });
      const after = fs.readFileSync(matrixPath, 'utf8');
      const output = `${result.stdout}${result.stderr}`;
      if (fresh) {
        assert.doesNotMatch(output, /is not in this plan's MODEL_MATRIX snapshot/);
        assert.ok(JSON.parse(after).audit.some((entry) => entry.op === 'resume_provider' && entry.provider === 'kimi'), output);
      } else {
        assert.notEqual(result.status, 0);
        assert.match(output, /MODEL_MATRIX snapshot and its shared catalog is (stale|expired)/);
        assert.match(output, /refresh --plan/);
        assert.equal(after, before);
      }
    } finally {
      fs.rmSync(workspace, { recursive: true, force: true });
    }
  }
});

test('lifecycle commands remain workspace-aware and resumable', () => {
  const workspace = temporaryDirectory();
  try {
    const current = run(['current', '--cwd', workspace, '--json']);
    assert.equal(current.status, 0, current.stderr);
    assert.equal(JSON.parse(current.stdout).action, 'create_request');

    const cancel = run(['cancel', '--cwd', workspace, '--json']);
    assert.equal(cancel.status, 0, cancel.stderr);
    assert.equal(JSON.parse(cancel.stdout).implementation_changes_preserved, true);

    const reset = run(['reset', '--cwd', workspace, '--json']);
    assert.equal(reset.status, 0, reset.stderr);
    assert.equal(JSON.parse(reset.stdout).status, 'idle');
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});
