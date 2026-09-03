#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scriptDirectory = path.join(root, 'skill', 'plan-and-execute', 'scripts');
const testScripts = [
  'self_test.py',
  'study_self_test.py',
  'lifecycle_self_test.py',
  'context_self_test.py',
  'task_memory_self_test.py',
  'provider_self_test.py',
  'token_efficiency_self_test.py',
  'artifact_concision_self_test.py',
  'study_choice_interaction_self_test.py',
  'routing_self_test.py',
  'promotion_self_test.py'
].map((name) => path.join(scriptDirectory, name));
const candidates = process.platform === 'win32'
  ? [['py', ['-3']], ['python', []], ['python3', []]]
  : [['python3', []], ['python', []]];
let python = null;
for (const [command, prefix] of candidates) {
  const probe = spawnSync(command, [...prefix, '--version'], {
    cwd: root,
    encoding: 'utf8',
    windowsHide: true
  });
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
    cwd: root,
    stdio: 'inherit',
    windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
