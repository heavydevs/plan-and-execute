import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import test from 'node:test';
import { installSkill, uninstallSkill, getStatus, INSTALL_MARKER, SKILL_SOURCE, computeDirectoryHash } from '../lib/installer.js';
import { stageSkillSource, skillSource } from '../lib/skill-source.js';

const temp = () => fs.mkdtempSync(path.join(os.tmpdir(), 'pae-companion-test-'));
const cleanup = (p) => fs.rmSync(p, { recursive: true, force: true });
const python = process.platform === 'win32' ? 'python' : 'python3';
const run = (file, args, cwd) => spawnSync(python, [file, ...args], { cwd, encoding: 'utf8', timeout: 15000, windowsHide: true, env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' } });

test('companion payload is deterministic and its runtime matches canonical source hashes', () => {
  const a = stageSkillSource('validate-or-fix');
  const b = stageSkillSource('validate-or-fix');
  try {
    assert.equal(computeDirectoryHash(a.directory), computeDirectoryHash(b.directory));
    const provenance = JSON.parse(fs.readFileSync(path.join(a.directory, '_runtime', 'PROVENANCE.json')));
    assert.ok(Object.keys(provenance.files).length > 15);
    for (const [relative, hash] of Object.entries(provenance.files)) {
      for (const file of [path.join(a.directory, '_runtime', relative), path.join(SKILL_SOURCE, relative)]) {
        assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'), hash);
      }
    }
    assert.equal(fs.existsSync(path.join(a.directory, '_runtime', 'SKILL.md')), false);
    assert.equal(fs.existsSync(path.join(a.directory, '_runtime', 'scripts', 'self_test.py')), false);
  } finally { a.cleanup(); b.cleanup(); }
});

test('companion installs alone and wrappers run without sibling or planning state', () => {
  const root = temp();
  try {
    const options = { skill: 'validate-or-fix', agent: 'codex', workspaceDir: root };
    const target = installSkill(options)[0].destination;
    assert.equal(fs.existsSync(path.join(root, '.agents', 'skills', 'plan-and-execute')), false);
    assert.equal(JSON.parse(fs.readFileSync(path.join(target, INSTALL_MARKER))).skill, 'validate-or-fix');
    for (const file of ['validatectl.py', 'service_map.py', 'workload_routing.py']) {
      const result = run(path.join(target, 'scripts', file), ['--help'], root);
      assert.equal(result.status, 0, result.stderr);
    }
    const result = run(path.join(target, 'scripts', 'validatectl.py'), ['status', '--repo-root', root, '--validation', 'TEST'], root);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(result.stdout).status, 'absent');
    assert.equal(fs.existsSync(path.join(root, '.ai-work')), false);
    assert.equal(getStatus({ ...options, verify: true })[0].verified, true);
    assert.equal(uninstallSkill(options)[0].action, 'uninstalled');
  } finally { cleanup(root); }
});

test('both skills coexist and uninstalling companion preserves main exactly', () => {
  const root = temp();
  try {
    const options = { skill: 'all', agent: 'all', workspaceDir: root };
    assert.equal(installSkill(options).length, 4);
    assert.ok(getStatus({ ...options, verify: true }).every((t) => t.verified));
    const main = path.join(root, '.claude', 'skills', 'plan-and-execute');
    const hash = computeDirectoryHash(main);
    assert.equal(uninstallSkill({ ...options, skill: 'validate-or-fix' }).length, 2);
    assert.equal(computeDirectoryHash(main), hash);
    assert.equal(getStatus({ ...options, skill: 'plan-and-execute', verify: true })[0].verified, true);
  } finally { cleanup(root); }
});

test('all-skills preflight refuses local companion edits before changing main', () => {
  const root = temp();
  try {
    const options = { agent: 'codex', workspaceDir: root };
    const companion = installSkill({ ...options, skill: 'validate-or-fix' })[0].destination;
    fs.appendFileSync(path.join(companion, 'SKILL.md'), '\nLOCAL EDIT\n');
    assert.throws(() => installSkill({ ...options, skill: 'all' }), /alteracoes locais/);
    assert.equal(fs.existsSync(path.join(root, '.agents', 'skills', 'plan-and-execute')), false);
    assert.throws(() => uninstallSkill({ ...options, skill: 'all' }), /alteracoes locais/);
    assert.ok(fs.readFileSync(path.join(companion, 'SKILL.md'), 'utf8').includes('LOCAL EDIT'));
  } finally { cleanup(root); }
});

test('companion explicit activation and updates preserve managed ownership protections', () => {
  const root = temp();
  try {
    const options = { skill: 'validate-or-fix', agent: 'both', workspaceDir: root, activation: 'explicit' };
    const results = installSkill(options);
    const claude = results.find((item) => item.agent === 'claude').destination;
    assert.match(fs.readFileSync(path.join(claude, 'SKILL.md'), 'utf8'), /^disable-model-invocation: true$/m);
    assert.ok(getStatus({ ...options, verify: true }).every((t) => t.verified));
    assert.ok(installSkill({ ...options, activation: 'selective' }).every((t) => t.action === 'updated'));
    assert.equal(fs.existsSync(path.join(skillSource('validate-or-fix'), '_runtime')), false);
  } finally { cleanup(root); }
});

test('prebuilt companion reinstalls with identical runtime and rejects tampering', () => {
  const root = temp();
  const source = stageSkillSource('validate-or-fix');
  try {
    const options = { skill: 'validate-or-fix', agent: 'codex', workspaceDir: root, sourceDirectory: source.directory };
    const target = installSkill(options)[0].destination;
    assert.equal(getStatus({ ...options, verify: true })[0].verified, true);
    fs.appendFileSync(path.join(target, '_runtime', 'scripts', 'validatectl.py'), '\n# altered\n');
    assert.equal(getStatus({ ...options, verify: true })[0].verified, false);
    assert.throws(() => installSkill(options), /alteracoes locais/);
  } finally { cleanup(root); source.cleanup(); }
});

test('fixed CLI passthrough supports validation and workload discovery', () => {
  const root = temp();
  const cli = path.resolve('bin/plan-and-execute.js');
  try {
    for (const command of ['validate', 'workloads']) {
      const result = spawnSync(process.execPath, [cli, command, '--cwd', root, '--help'], { encoding: 'utf8', timeout: 15000 });
      assert.equal(result.status, 0, result.stderr);
      assert.match(result.stdout, /usage:/i);
    }
    assert.equal(fs.existsSync(path.join(root, '.ai-work')), false);
    const result = spawnSync(process.execPath, [cli, 'install', 'codex', '--skill', 'validate-or-fix', '--cwd', root, '--json'], { encoding: 'utf8', timeout: 15000 });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(JSON.parse(result.stdout)[0].skill, 'validate-or-fix');
  } finally { cleanup(root); }
});

test('independently installed companion maps and supervises an actual validation', () => {
  const root = temp();
  try {
    const target = installSkill({ skill: 'validate-or-fix', agent: 'codex', workspaceDir: root })[0].destination;
    const mapScript = path.join(target, 'scripts', 'service_map.py');
    const mapPath = path.join(root, '.ai-work', 'SERVICE_MAP.md');
    let result = run(mapScript, ['init', '--repo-root', root], root);
    assert.equal(result.status, 0, result.stderr);
    let text = fs.readFileSync(mapPath, 'utf8');
    const match = text.match(/```json\s*([\s\S]*?)```/);
    assert.ok(match);
    const data = JSON.parse(match[1]);
    data.inventory_reviewed = true;
    data.resources = [];
    data.toolchains = [];
    data.validations = [{ id: 'TEST', command: [python, '-c', 'print("companion validation passed")'], resources: [], no_progress_timeout_seconds: 10 }];
    text = text.replace(match[1], `${JSON.stringify(data, null, 2)}\n`);
    fs.writeFileSync(mapPath, text);
    result = run(mapScript, ['stamp', '--repo-root', root, '--confirm-reconciled'], root);
    assert.equal(result.status, 0, result.stderr);
    result = run(path.join(target, 'scripts', 'validatectl.py'), ['run', '--repo-root', root, '--validation', 'TEST'], root);
    assert.equal(result.status, 0, result.stderr + result.stdout);
    assert.equal(JSON.parse(result.stdout).status, 'passed');
    assert.equal(fs.existsSync(path.join(root, '.ai-work', '.active-plan.json')), false);
    assert.equal(fs.existsSync(path.join(root, '.ai-work', 'validation', 'TEST', 'manifest.json')), false);
    assert.equal(getStatus({ skill: 'validate-or-fix', agent: 'codex', workspaceDir: root, verify: true })[0].verified, true);
  } finally { cleanup(root); }
});


test('packaging is reproducible and never deletes a foreign temporary file', () => {
  const root = temp();
  try {
    const output = path.join(root, 'validate-or-fix');
    fs.mkdirSync(output);
    const foreign = path.join(output, 'skill.zip.tmp');
    fs.writeFileSync(foreign, 'another packager owns this');
    const args = [path.resolve('tools/package-skills.js'), '--output', root, '--skill', 'validate-or-fix'];
    const pack = () => {
      const result = spawnSync(process.execPath, args, { encoding: 'utf8', timeout: 20000, windowsHide: true });
      assert.equal(result.status, 0, result.stderr + result.stdout);
      return crypto.createHash('sha256').update(fs.readFileSync(path.join(output, 'skill.zip'))).digest('hex');
    };
    assert.equal(pack(), pack());
    assert.equal(fs.readFileSync(foreign, 'utf8'), 'another packager owns this');
  } finally { cleanup(root); }
});
