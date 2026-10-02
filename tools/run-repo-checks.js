#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const checks = [
  ['tools/doc_baseline.py', 'check', '--baseline', 'docs/research/ROUTING_DOC_BASELINE.json'],
  ['tools/routing_eval_predeclaration_self_test.py'],
  ['tools/routing_eval_self_test.py'],
  ['tools/skill_benchmark_self_test.py']
];
const candidates = process.platform === 'win32'
  ? [['python', []], ['python3', []], ['py', ['-3']]]
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
  console.error('Python 3 nao foi encontrado. Instale Python 3.10+ para executar os checks do repositorio.');
  process.exit(1);
}
for (const args of checks) {
  const [command, prefix] = python;
  const result = spawnSync(command, [...prefix, ...args], {
    cwd: root,
    stdio: 'inherit',
    windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
