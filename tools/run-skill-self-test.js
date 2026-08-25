#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const testScript = path.join(root, 'skill', 'plan-and-execute', 'scripts', 'self_test.py');
const candidates = process.platform === 'win32'
  ? [['py', ['-3', testScript]], ['python', [testScript]], ['python3', [testScript]]]
  : [['python3', [testScript]], ['python', [testScript]]];

for (const [command, args] of candidates) {
  const result = spawnSync(command, args, {
    cwd: root,
    stdio: 'inherit',
    windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  });
  if (result.error?.code === 'ENOENT') {
    continue;
  }
  process.exit(result.status ?? 1);
}

console.error('Python 3 nao foi encontrado. Instale Python 3.10+ para executar o self-test da skill.');
process.exit(1);
