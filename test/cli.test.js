import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'bin', 'plan-and-execute.js');

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

test('CLI installs, reports and uninstalls both workspace copies', () => {
  const workspace = temporaryDirectory();
  try {
    const install = run(['install', 'both', '--cwd', workspace, '--json']);
    assert.equal(install.status, 0, install.stderr);
    const installed = JSON.parse(install.stdout);
    assert.equal(installed.length, 2);
    assert.ok(installed.every((item) => item.action === 'installed'));

    const status = run(['status', '--agent', 'both', '--workspace', workspace, '--json']);
    assert.equal(status.status, 0, status.stderr);
    assert.ok(JSON.parse(status.stdout).every((item) => item.managed && !item.modified));

    const remove = run(['uninstall', 'both', '--cwd', workspace, '--json']);
    assert.equal(remove.status, 0, remove.stderr);
    assert.ok(JSON.parse(remove.stdout).every((item) => item.action === 'uninstalled'));
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('CLI paths, dry-run and version are automation friendly', () => {
  const workspace = temporaryDirectory();
  try {
    const paths = run(['paths', 'both', '--cwd', workspace, '--json']);
    assert.equal(paths.status, 0, paths.stderr);
    assert.equal(JSON.parse(paths.stdout).length, 2);

    const dryRun = run(['install', 'claude', '--cwd', workspace, '--dry-run', '--json']);
    assert.equal(dryRun.status, 0, dryRun.stderr);
    assert.equal(JSON.parse(dryRun.stdout)[0].action, 'would-install');
    assert.equal(fs.existsSync(path.join(workspace, '.claude')), false);

    const version = run(['--version']);
    assert.equal(version.status, 0, version.stderr);
    assert.match(version.stdout, /^0\.2\.0\s*$/);
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});

test('CLI returns a distinct safety exit code for modified installs', () => {
  const workspace = temporaryDirectory();
  try {
    const install = run(['install', 'claude', '--cwd', workspace]);
    assert.equal(install.status, 0, install.stderr);
    const skill = path.join(workspace, '.claude', 'skills', 'plan-and-execute', 'SKILL.md');
    fs.appendFileSync(skill, '\nlocal edit\n', 'utf8');

    const update = run(['install', 'claude', '--cwd', workspace]);
    assert.equal(update.status, 3);
    assert.match(update.stderr, /alteracoes locais/);
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});
