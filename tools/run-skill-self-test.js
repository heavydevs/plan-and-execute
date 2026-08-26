#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scripts = [
  path.join(root, 'skill', 'plan-and-execute', 'scripts', 'self_test.py'),
  path.join(root, 'skill', 'plan-and-execute', 'scripts', 'study_self_test.py')
];
const candidates = process.platform === 'win32'
  ? [['py', ['-3']], ['python', []], ['python3', []]]
  : [['python3', []], ['python', []]];

let selected = null;
for (const [command, prefixArgs] of candidates) {
  const probe = spawnSync(command, [...prefixArgs, '--version'], {
    cwd: root,
    stdio: 'ignore',
    windowsHide: true
  });
  if (!probe.error && probe.status === 0) {
    selected = [command, prefixArgs];
    break;
  }
}

if (!selected) {
  console.error('Python 3 was not found. Install Python 3.10+ to run the skill self-tests.');
  process.exit(1);
}

const [command, prefixArgs] = selected;
for (const script of scripts) {
  const result = spawnSync(command, [...prefixArgs, script], {
    cwd: root,
    stdio: 'inherit',
    windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  });
  if (result.status !== 0) {
    process.exit(result.status ?? 1);
  }
}
