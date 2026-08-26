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

const skillFiles = [];
function walk(directory, output) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      walk(absolute, output);
    } else if (entry.isFile()) {
      output.push(absolute);
    }
  }
}
walk(SKILL_SOURCE, skillFiles);

const forbidden = new Map([
  ['long-task-orchestrator', []],
  ['github.com/luizcgvrj/plan-and-execute', []],
  ['github:luizcgvrj/plan-and-execute', []]
]);

const repositoryFiles = [];
for (const rootEntry of fs.readdirSync(process.cwd(), { withFileTypes: true })) {
  if (['.git', 'node_modules', '.ai-work'].includes(rootEntry.name)) continue;
  const absolute = path.join(process.cwd(), rootEntry.name);
  if (rootEntry.isDirectory()) walk(absolute, repositoryFiles);
  else if (rootEntry.isFile()) repositoryFiles.push(absolute);
}

for (const file of repositoryFiles) {
  if (path.relative(process.cwd(), file) === path.join('tools', 'validate-skill.js')) {
    continue;
  }
  const buffer = fs.readFileSync(file);
  for (const [needle, matches] of forbidden) {
    if (buffer.includes(Buffer.from(needle))) {
      matches.push(path.relative(process.cwd(), file));
    }
  }
}

for (const [needle, matches] of forbidden) {
  if (matches.length > 0) {
    console.error(`Forbidden legacy reference ${needle} found in: ${matches.join(', ')}`);
    process.exit(1);
  }
}

const metadata = fs.readFileSync(path.join(SKILL_SOURCE, 'agents', 'openai.yaml'), 'utf8');
if (!metadata.includes('display_name: "Plan and Execute"')) {
  console.error('agents/openai.yaml does not contain the expected display_name.');
  process.exit(1);
}

const skill = fs.readFileSync(path.join(SKILL_SOURCE, 'SKILL.md'), 'utf8');
for (const requiredText of [
  'No arguments: create an editable request draft',
  '--move-request',
  'Keep `TODO.md` intentionally terse',
  'references/INTAKE.md'
]) {
  if (!skill.includes(requiredText)) {
    console.error(`SKILL.md is missing required workflow text: ${requiredText}`);
    process.exit(1);
  }
}

const readme = fs.readFileSync(path.join(process.cwd(), 'README.md'), 'utf8');
if (!readme.startsWith('# Plan and Execute\n\n**Turn large coding requests')) {
  console.error('README.md must begin with the English outcome-focused introduction.');
  process.exit(1);
}
if (!fs.existsSync(path.join(process.cwd(), 'README.pt-BR.md'))) {
  console.error('README.pt-BR.md is required.');
  process.exit(1);
}

const packageMetadata = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8'));
if (packageMetadata.version !== '0.3.0') {
  console.error(`Expected package version 0.3.0, found ${packageMetadata.version}.`);
  process.exit(1);
}
if (!packageMetadata.repository?.url?.includes('heavydevs/plan-and-execute')) {
  console.error('package.json must point to heavydevs/plan-and-execute.');
  process.exit(1);
}

console.log(
  `Skill ${SKILL_NAME} validated (${skillFiles.length} files, sha256 ${computeDirectoryHash(SKILL_SOURCE)}).`
);
