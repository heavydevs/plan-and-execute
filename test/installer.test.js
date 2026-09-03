import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

import {
  ACTIVATION_MODES,
  INSTALL_MARKER,
  SKILL_NAME,
  SKILL_SOURCE,
  computeDirectoryHash,
  getStatus,
  installSkill,
  normalizeActivation,
  readSkillName,
  resolveTargets,
  runDoctor,
  uninstallSkill,
  validateBundledSkill
} from '../lib/installer.js';

const packageVersion = JSON.parse(
  fs.readFileSync(new URL('../package.json', import.meta.url), 'utf8')
).version;

function temporaryDirectory() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'plan-and-execute-test-'));
}

function cleanup(directory) {
  fs.rmSync(directory, { recursive: true, force: true });
}

function writeManualSkill(destination, name = SKILL_NAME) {
  fs.mkdirSync(destination, { recursive: true });
  fs.writeFileSync(
    path.join(destination, 'SKILL.md'),
    `---\nname: ${name}\ndescription: test skill\n---\n`,
    'utf8'
  );
}

function read(destination, relativePath) {
  return fs.readFileSync(path.join(destination, relativePath), 'utf8');
}

test('bundled skill is valid and uses the short name', () => {
  assert.equal(validateBundledSkill(), true);
  assert.deepEqual(ACTIVATION_MODES, ['selective', 'explicit']);
  assert.equal(normalizeActivation(undefined), 'selective');
  assert.equal(normalizeActivation('manual'), 'explicit');
});

test('bundled source remains selective and is never rewritten by explicit installs', () => {
  const skillBefore = read(SKILL_SOURCE, 'SKILL.md');
  const metadataBefore = read(SKILL_SOURCE, path.join('agents', 'openai.yaml'));
  assert.doesNotMatch(skillBefore, /^disable-model-invocation:\s*true$/m);
  assert.match(metadataBefore, /^\s*allow_implicit_invocation:\s*true$/m);

  const root = temporaryDirectory();
  try {
    installSkill({ agent: 'both', workspaceDir: root, activation: 'explicit' });
    assert.equal(read(SKILL_SOURCE, 'SKILL.md'), skillBefore);
    assert.equal(read(SKILL_SOURCE, path.join('agents', 'openai.yaml')), metadataBefore);
  } finally {
    cleanup(root);
  }
});

test('resolves workspace destinations for both agents', () => {
  const root = temporaryDirectory();
  try {
    const targets = resolveTargets({ agent: 'both', scope: 'workspace', workspaceDir: root });
    assert.deepEqual(targets.map((target) => target.destination), [
      path.join(root, '.claude', 'skills', SKILL_NAME),
      path.join(root, '.agents', 'skills', SKILL_NAME)
    ]);
    assert.ok(targets.every((target) => target.scope === 'workspace'));
  } finally {
    cleanup(root);
  }
});

test('optional execution providers are not skill installation targets', () => {
  const root = temporaryDirectory();
  try {
    for (const provider of ['gemini', 'qwen', 'kimi', 'trae']) {
      assert.throws(
        () => resolveTargets({ agent: provider, scope: 'workspace', workspaceDir: root }),
        /Agente invalido/
      );
    }
  } finally {
    cleanup(root);
  }
});

test('accepts local/project and user/global aliases', () => {
  const root = temporaryDirectory();
  const home = temporaryDirectory();
  try {
    const [local] = resolveTargets({ agent: 'claude', scope: 'project', projectDir: root });
    const [global] = resolveTargets({ agent: 'codex', scope: 'global', homeDir: home });
    assert.equal(local.destination, path.join(root, '.claude', 'skills', SKILL_NAME));
    assert.equal(local.scope, 'workspace');
    assert.equal(global.destination, path.join(home, '.agents', 'skills', SKILL_NAME));
    assert.equal(global.scope, 'user');
  } finally {
    cleanup(root);
    cleanup(home);
  }
});

test('selective is the default and installs managed copies for Claude and Codex', () => {
  const root = temporaryDirectory();
  try {
    const results = installSkill({ agent: 'both', scope: 'workspace', workspaceDir: root });
    assert.equal(results.length, 2);
    assert.ok(results.every((item) => item.action === 'installed'));
    assert.ok(results.every((item) => item.activation === 'selective'));

    for (const result of results) {
      assert.equal(readSkillName(result.destination), SKILL_NAME);
      assert.ok(fs.existsSync(path.join(result.destination, 'scripts', 'planctl.py')));
      assert.ok(fs.existsSync(path.join(result.destination, 'scripts', 'promotectl.py')));
      assert.ok(fs.existsSync(path.join(result.destination, 'references', 'PROMOTION.md')));
      assert.ok(fs.existsSync(path.join(result.destination, INSTALL_MARKER)));
      const marker = JSON.parse(read(result.destination, INSTALL_MARKER));
      assert.equal(marker.schemaVersion, 2);
      assert.equal(marker.activation, 'selective');
      assert.equal(marker.installedHash, computeDirectoryHash(result.destination));
    }

    const claude = results.find((item) => item.agent === 'claude');
    const codex = results.find((item) => item.agent === 'codex');
    assert.doesNotMatch(read(claude.destination, 'SKILL.md'), /^disable-model-invocation:\s*true$/m);
    assert.match(read(codex.destination, path.join('agents', 'openai.yaml')), /^\s*allow_implicit_invocation:\s*true$/m);

    const status = getStatus({ agent: 'both', scope: 'workspace', workspaceDir: root });
    assert.ok(status.every((item) => item.installed && item.owned && item.valid));
    assert.ok(status.every((item) => item.managed && item.modified === false));
    assert.ok(status.every((item) => item.version === packageVersion));
    assert.ok(status.every((item) => item.sourceHash));
    assert.ok(status.every((item) => item.installedHash === item.currentHash));
    assert.ok(status.every((item) => item.activation === 'selective'));
  } finally {
    cleanup(root);
  }
});

test('explicit mode disables automatic model invocation per host without changing routing runtime', () => {
  const root = temporaryDirectory();
  try {
    const results = installSkill({ agent: 'both', workspaceDir: root, activation: 'explicit' });
    const claude = results.find((item) => item.agent === 'claude');
    const codex = results.find((item) => item.agent === 'codex');

    assert.match(read(claude.destination, 'SKILL.md'), /^disable-model-invocation:\s*true$/m);
    assert.match(
      read(codex.destination, path.join('agents', 'openai.yaml')),
      /^\s*allow_implicit_invocation:\s*false$/m
    );
    assert.equal(
      read(codex.destination, 'SKILL.md').includes('`provider`, `model_tier`, and `reasoning_effort`'),
      true
    );

    const status = getStatus({ agent: 'both', workspaceDir: root });
    assert.ok(status.every((item) => item.managed && item.modified === false));
    assert.ok(status.every((item) => item.activation === 'explicit'));
    assert.ok(status.every((item) => item.installedHash === item.currentHash));
    assert.ok(results.some((item) => item.installedHash !== item.sourceHash));
  } finally {
    cleanup(root);
  }
});

test('switches activation mode safely without force when managed copy is untouched', () => {
  const root = temporaryDirectory();
  try {
    installSkill({ agent: 'both', workspaceDir: root, activation: 'explicit' });
    const switched = installSkill({ agent: 'both', workspaceDir: root, activation: 'selective' });
    assert.ok(switched.every((item) => item.action === 'updated'));

    const status = getStatus({ agent: 'both', workspaceDir: root });
    assert.ok(status.every((item) => item.activation === 'selective' && !item.modified));
    const claude = status.find((item) => item.agent === 'claude');
    const codex = status.find((item) => item.agent === 'codex');
    assert.doesNotMatch(read(claude.destination, 'SKILL.md'), /^disable-model-invocation:\s*true$/m);
    assert.match(read(codex.destination, path.join('agents', 'openai.yaml')), /allow_implicit_invocation:\s*true/);
  } finally {
    cleanup(root);
  }
});

test('rejects an invalid activation mode', () => {
  const root = temporaryDirectory();
  try {
    assert.throws(
      () => installSkill({ agent: 'claude', workspaceDir: root, activation: 'always' }),
      /Modo de ativacao invalido/
    );
  } finally {
    cleanup(root);
  }
});

test('reinstall is idempotent when activation and installed hash are current', () => {
  const root = temporaryDirectory();
  try {
    installSkill({ agent: 'claude', workspaceDir: root, activation: 'explicit' });
    const [second] = installSkill({ agent: 'claude', workspaceDir: root, activation: 'explicit' });
    assert.equal(second.action, 'already-current');
  } finally {
    cleanup(root);
  }
});

test('detects local edits and requires force before updating', () => {
  const root = temporaryDirectory();
  try {
    const [target] = installSkill({ agent: 'claude', workspaceDir: root });
    fs.writeFileSync(path.join(target.destination, 'local-change.txt'), 'keep me', 'utf8');
    const [status] = getStatus({ agent: 'claude', workspaceDir: root });
    assert.equal(status.modified, true);
    assert.throws(
      () => installSkill({ agent: 'claude', workspaceDir: root }),
      /alteracoes locais/
    );
    assert.ok(fs.existsSync(path.join(target.destination, 'local-change.txt')));
    const [updated] = installSkill({ agent: 'claude', workspaceDir: root, force: true });
    assert.equal(updated.action, 'updated');
    assert.equal(fs.existsSync(path.join(target.destination, 'local-change.txt')), false);
    assert.equal(getStatus({ agent: 'claude', workspaceDir: root })[0].modified, false);
  } finally {
    cleanup(root);
  }
});

test('recognizes legacy schema-v1 managed installs as selective', () => {
  const root = temporaryDirectory();
  try {
    const destination = path.join(root, '.claude', 'skills', SKILL_NAME);
    fs.cpSync(SKILL_SOURCE, destination, { recursive: true });
    const sourceHash = computeDirectoryHash(destination);
    fs.writeFileSync(path.join(destination, INSTALL_MARKER), JSON.stringify({
      schemaVersion: 1,
      skill: SKILL_NAME,
      package: '@luizcgvrj/plan-and-execute',
      version: '0.7.0',
      sourceHash,
      installedAt: new Date().toISOString()
    }, null, 2));
    const [status] = getStatus({ agent: 'claude', workspaceDir: root });
    assert.equal(status.managed, true);
    assert.equal(status.modified, false);
    assert.equal(status.activation, 'selective');
  } finally {
    cleanup(root);
  }
});

test('manual copy with the same name requires force before adoption', () => {
  const root = temporaryDirectory();
  try {
    const destination = path.join(root, '.claude', 'skills', SKILL_NAME);
    writeManualSkill(destination);
    assert.throws(
      () => installSkill({ agent: 'claude', workspaceDir: root }),
      /instalada manualmente/
    );
    const [result] = installSkill({ agent: 'claude', workspaceDir: root, force: true });
    assert.equal(result.action, 'updated');
    assert.equal(getStatus({ agent: 'claude', workspaceDir: root })[0].managed, true);
  } finally {
    cleanup(root);
  }
});

test('force never replaces an unrelated directory', () => {
  const root = temporaryDirectory();
  try {
    const destination = path.join(root, '.claude', 'skills', SKILL_NAME);
    writeManualSkill(destination, 'another-skill');
    assert.throws(
      () => installSkill({ agent: 'claude', workspaceDir: root, force: true }),
      /nao pertence/
    );
    assert.equal(readSkillName(destination), 'another-skill');
  } finally {
    cleanup(root);
  }
});

test('supports user scope with a custom home directory', () => {
  const home = temporaryDirectory();
  try {
    const [result] = installSkill({ agent: 'codex', scope: 'user', homeDir: home });
    assert.equal(result.destination, path.join(home, '.agents', 'skills', SKILL_NAME));
    assert.equal(readSkillName(result.destination), SKILL_NAME);
  } finally {
    cleanup(home);
  }
});

test('dry-run explicit mode does not create files', () => {
  const root = temporaryDirectory();
  try {
    const results = installSkill({
      agent: 'both', scope: 'workspace', workspaceDir: root, activation: 'explicit', dryRun: true
    });
    assert.ok(results.every((result) => result.action === 'would-install'));
    assert.ok(results.every((result) => result.activation === 'explicit'));
    assert.equal(fs.existsSync(path.join(root, '.claude')), false);
    assert.equal(fs.existsSync(path.join(root, '.agents')), false);
  } finally {
    cleanup(root);
  }
});

test('uninstall preserves modified content unless force is explicit', () => {
  const root = temporaryDirectory();
  try {
    const [target] = installSkill({ agent: 'claude', workspaceDir: root, activation: 'explicit' });
    fs.appendFileSync(path.join(target.destination, 'SKILL.md'), '\nlocal edit\n', 'utf8');
    assert.throws(
      () => uninstallSkill({ agent: 'claude', workspaceDir: root }),
      /alteracoes locais/
    );
    assert.ok(fs.existsSync(target.destination));
    const [removed] = uninstallSkill({ agent: 'claude', workspaceDir: root, force: true });
    assert.equal(removed.action, 'uninstalled');
    assert.equal(fs.existsSync(target.destination), false);
  } finally {
    cleanup(root);
  }
});

test('uninstalls only the selected target', () => {
  const root = temporaryDirectory();
  try {
    installSkill({ agent: 'both', workspaceDir: root });
    uninstallSkill({ agent: 'claude', workspaceDir: root });
    const status = getStatus({ agent: 'both', workspaceDir: root });
    assert.equal(status.find((item) => item.agent === 'claude').installed, false);
    assert.equal(status.find((item) => item.agent === 'codex').installed, true);
  } finally {
    cleanup(root);
  }
});

test('hash ignores the installer marker but detects content changes', () => {
  const root = temporaryDirectory();
  try {
    writeManualSkill(root);
    const initial = computeDirectoryHash(root);
    fs.writeFileSync(path.join(root, INSTALL_MARKER), '{}\n', 'utf8');
    assert.equal(computeDirectoryHash(root), initial);
    fs.appendFileSync(path.join(root, 'SKILL.md'), '\nchanged\n', 'utf8');
    assert.notEqual(computeDirectoryHash(root), initial);
  } finally {
    cleanup(root);
  }
});

test('doctor reports activation policy while remaining scoped to standard installed CLIs', () => {
  const report = runDoctor();
  assert.equal(report.bundledSkillValid, true);
  assert.deepEqual(report.activationModes, ['selective', 'explicit']);
  assert.equal(report.defaultActivation, 'selective');
  assert.ok(Object.hasOwn(report, 'claude'));
  assert.ok(Object.hasOwn(report, 'codex'));
  assert.equal(Object.hasOwn(report, 'gemini'), false);
  assert.equal(Object.hasOwn(report, 'qwen'), false);
});

test('refuses to replace a symbolic-link destination', { skip: process.platform === 'win32' }, () => {
  const root = temporaryDirectory();
  const external = temporaryDirectory();
  try {
    writeManualSkill(external);
    const destination = path.join(root, '.claude', 'skills', SKILL_NAME);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.symlinkSync(external, destination, 'dir');
    assert.throws(
      () => installSkill({ agent: 'claude', workspaceDir: root, force: true }),
      /link simbolico/
    );
    assert.equal(fs.lstatSync(destination).isSymbolicLink(), true);
  } finally {
    cleanup(root);
    cleanup(external);
  }
});
