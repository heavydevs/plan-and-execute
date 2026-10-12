import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const cleaner = fileURLToPath(new URL('../tools/clean-generated.js', import.meta.url));

test('clean preserves .ai-work caches and removes generated files elsewhere', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pae-clean-'));
  try {
    for (const relative of ['.ai-work/__pycache__', 'src/__pycache__', 'node_modules/__pycache__']) {
      fs.mkdirSync(path.join(root, relative), { recursive: true });
      fs.writeFileSync(path.join(root, relative, 'fixture.pyc'), 'synthetic');
    }
    fs.writeFileSync(path.join(root, 'src', 'loose.pyc'), 'synthetic');
    fs.writeFileSync(path.join(root, 'src', 'keep.py'), 'synthetic');
    const result = spawnSync(process.execPath, [cleaner], { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
    assert.ok(fs.existsSync(path.join(root, '.ai-work', '__pycache__', 'fixture.pyc')));
    assert.ok(fs.existsSync(path.join(root, 'node_modules', '__pycache__', 'fixture.pyc')));
    assert.equal(fs.existsSync(path.join(root, 'src', '__pycache__')), false);
    assert.equal(fs.existsSync(path.join(root, 'src', 'loose.pyc')), false);
    assert.ok(fs.existsSync(path.join(root, 'src', 'keep.py')));
  } finally { fs.rmSync(root, { recursive: true, force: true }); }
});

test('clean skips unreadable directories', { skip: process.platform === 'win32' || os.userInfo().uid === 0 }, () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pae-clean-'));
  const locked = path.join(root, 'locked');
  try {
    fs.mkdirSync(locked);
    fs.chmodSync(locked, 0);
    const result = spawnSync(process.execPath, [cleaner], { cwd: root, encoding: 'utf8' });
    assert.equal(result.status, 0, result.stderr);
  } finally {
    fs.chmodSync(locked, 0o700);
    fs.rmSync(root, { recursive: true, force: true });
  }
});
