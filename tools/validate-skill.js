#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import {
  SKILL_NAME,
  SKILL_SOURCE,
  computeDirectoryHash,
  validateBundledSkill
} from '../lib/installer.js';

validateBundledSkill();

const files = [];
function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      walk(absolute);
    } else if (entry.isFile()) {
      files.push(absolute);
    }
  }
}
walk(SKILL_SOURCE);

const legacyName = 'long-task-orchestrator';
const legacyOccurrences = [];
for (const file of files) {
  const buffer = fs.readFileSync(file);
  if (buffer.includes(Buffer.from(legacyName))) {
    legacyOccurrences.push(path.relative(process.cwd(), file));
  }
}

if (legacyOccurrences.length > 0) {
  console.error(`Nome antigo encontrado em: ${legacyOccurrences.join(', ')}`);
  process.exit(1);
}

const metadata = fs.readFileSync(path.join(SKILL_SOURCE, 'agents', 'openai.yaml'), 'utf8');
if (!metadata.includes('display_name: "Plan and Execute"')) {
  console.error('agents/openai.yaml nao possui o display_name esperado.');
  process.exit(1);
}

console.log(
  `Skill ${SKILL_NAME} validada (${files.length} arquivos, sha256 ${computeDirectoryHash(SKILL_SOURCE)}).`
);
