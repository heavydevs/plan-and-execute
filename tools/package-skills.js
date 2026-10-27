#!/usr/bin/env node
/** Build one independently installable ZIP per skill from the canonical sources. */
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';
import { SKILLS, normalizeSkill, stageSkillSource } from '../lib/skill-source.js';
import { validateBundledSkill } from '../lib/installer.js';

let output = path.resolve('dist');
let skill = 'all';
for (let i = 2; i < process.argv.length; i++) {
  const arg = process.argv[i];
  if (!['--output', '--skill'].includes(arg) || !process.argv[i + 1]) {
    throw new Error('Usage: node tools/package-skills.js [--output DIR] [--skill NAME|all]');
  }
  if (arg === '--output') output = path.resolve(process.argv[++i]);
  else skill = normalizeSkill(process.argv[++i], true);
}
const candidates = process.platform === 'win32' ? [['python', []], ['py', ['-3']], ['python3', []]] : [['python3', []], ['python', []]];
const python = candidates.find(([cmd, prefix]) => spawnSync(cmd, [...prefix, '--version'], { windowsHide: true, timeout: 5000 }).status === 0);
if (!python) throw new Error('Python 3.10+ is required for packaging.');
const pack = String.raw`
import os, stat, sys, tempfile, zipfile
from pathlib import Path
root, target = map(Path, sys.argv[1:3])
target.parent.mkdir(parents=True, exist_ok=True)
if target.is_symlink(): raise SystemExit('Refusing symlink output')
fd, name = tempfile.mkstemp(prefix='.' + target.name + '.', suffix='.tmp', dir=target.parent)
temporary = Path(name)
try:
    with os.fdopen(fd, 'wb') as handle, zipfile.ZipFile(handle, 'w', zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(root.rglob('*')):
            if source.is_symlink(): raise SystemExit('Symlinks are not packaged')
            if not source.is_file(): continue
            if '__pycache__' in source.parts or source.suffix == '.pyc': continue
            info = zipfile.ZipInfo((Path(root.name) / source.relative_to(root)).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | (source.stat().st_mode & 0o777)) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, source.read_bytes())
    if temporary.stat().st_size > 25 * 1024 * 1024: raise SystemExit('Skill exceeds 25 MiB')
    os.replace(temporary, target)
finally:
    temporary.unlink(missing_ok=True)
`;
for (const name of skill === 'all' ? SKILLS : [skill]) {
  const staged = stageSkillSource(name);
  try {
    validateBundledSkill(staged.directory, name);
    const destination = path.join(output, name, 'skill.zip');
    const result = spawnSync(python[0], [...python[1], '-c', pack, staged.directory, destination], { stdio: 'inherit', windowsHide: true });
    if (result.status !== 0) throw new Error(`Packaging ${name} failed (${result.status})`);
    console.log(`${name}: ${destination} (${fs.statSync(destination).size} bytes)`);
  } finally { staged.cleanup(); }
}
