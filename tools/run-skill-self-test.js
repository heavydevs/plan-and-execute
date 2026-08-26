#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scriptDirectory = path.join(root, 'skill', 'plan-and-execute', 'scripts');
const testScripts = [
  path.join(scriptDirectory, 'self_test.py'),
  path.join(scriptDirectory, 'study_self_test.py'),
  path.join(scriptDirectory, 'lifecycle_self_test.py'),
  path.join(scriptDirectory, 'context_self_test.py')
];
const candidates = process.platform === 'win32'
  ? [['py', ['-3']], ['python', []], ['python3', []]]
  : [['python3', []], ['python', []]];
let python = null;
for (const [command, prefix] of candidates) {
  const probe = spawnSync(command, [...prefix, '--version'], { cwd: root, encoding: 'utf8', windowsHide: true });
  if (probe.error?.code === 'ENOENT') continue;
  if (probe.status === 0) { python = [command, prefix]; break; }
}
if (!python) {
  console.error('Python 3 nao foi encontrado. Instale Python 3.10+ para executar os self-tests da skill.');
  process.exit(1);
}
for (const testScript of testScripts) {
  const [command, prefix] = python;
  const result = spawnSync(command, [...prefix, testScript], {
    cwd: root, stdio: 'inherit', windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
