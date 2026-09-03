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
  for (const provider of ['claude', 'codex', 'gemini', 'qwen', 'kimi', 'trae']) {
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
    for (const provider of ['claude', 'codex', 'gemini', 'qwen', 'kimi', 'trae']) {
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
  assert.deepEqual(report.executionProviders, ['claude', 'codex', 'gemini', 'qwen', 'kimi', 'trae']);
  assert.deepEqual(report.defaultProviderOrder, ['claude', 'codex']);
  assert.deepEqual(report.standardInstallTargets, ['claude', 'codex']);
  assert.deepEqual(report.activationModes, ['selective', 'explicit']);
  assert.equal(report.defaultActivation, 'selective');
  for (const provider of ['gemini', 'qwen', 'kimi', 'trae']) {
    assert.ok(Object.hasOwn(report, provider));
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
