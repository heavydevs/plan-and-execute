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

const requiredSkillFiles = [
  'SKILL.md',
  path.join('agents', 'openai.yaml'),
  path.join('references', 'ADAPTIVE_STUDY.md'),
  path.join('references', 'study-spec.example.json'),
  path.join('scripts', 'studyctl.py'),
  path.join('scripts', 'study_self_test.py'),
  path.join('references', 'EXECUTION_CONTEXT.md'),
  path.join('scripts', 'context_self_test.py')
];
for (const relative of requiredSkillFiles) {
  if (!fs.existsSync(path.join(SKILL_SOURCE, relative))) {
    console.error(`Bundled skill is missing ${relative}.`);
    process.exit(1);
  }
}

const metadata = fs.readFileSync(path.join(SKILL_SOURCE, 'agents', 'openai.yaml'), 'utf8');
if (!metadata.includes('display_name: "Plan and Execute"')) {
  console.error('agents/openai.yaml does not contain the expected display_name.');
  process.exit(1);
}
if (!metadata.includes('adaptive study')) {
  console.error('agents/openai.yaml must mention the adaptive study gate.');
  process.exit(1);
}

if (!metadata.toLowerCase().includes('resume')) {
  console.error('agents/openai.yaml must mention resumable lifecycle and resume behavior.');
  process.exit(1);
}
if (!metadata.toLowerCase().includes('execution context')) {
  console.error('agents/openai.yaml must mention minimal execution context.');
  process.exit(1);
}

const skill = fs.readFileSync(path.join(SKILL_SOURCE, 'SKILL.md'), 'utf8');
for (const requiredText of [
  'No arguments: resume an implementation or create a request',
  '--move-request',
  'Pass the adaptive study gate before planning',
  'studyctl.py validate',
  'studyctl.py attach',
  'studyctl.py validate-plan',
  'Keep `TODO.md` intentionally terse',
  'references/ADAPTIVE_STUDY.md',
  'references/INTAKE.md',
  'lifecyclectl.py current',
  'references/LIFECYCLE.md',
  'cancel --repo-root',
  'Evaluate progressive execution context',
  'references/EXECUTION_CONTEXT.md',
  'contexts_minimal',
  'Assigned execution context'
]) {
  if (!skill.includes(requiredText)) {
    console.error(`SKILL.md is missing required workflow text: ${requiredText}`);
    process.exit(1);
  }
}

const studyProtocol = fs.readFileSync(
  path.join(SKILL_SOURCE, 'references', 'ADAPTIVE_STUDY.md'),
  'utf8'
);
for (const requiredText of [
  'Mandatory internal study',
  'Conditional external research',
  'user_requested',
  'version_sensitive',
  'security_sensitive',
  'studyctl.py attach',
  'exact-text rule'
]) {
  if (!studyProtocol.includes(requiredText)) {
    console.error(`ADAPTIVE_STUDY.md is missing required protocol text: ${requiredText}`);
    process.exit(1);
  }
}

const studyExample = JSON.parse(
  fs.readFileSync(path.join(SKILL_SOURCE, 'references', 'study-spec.example.json'), 'utf8')
);
if (studyExample.schema_version !== 1 || !studyExample.synthesis?.ready_for_planning) {
  console.error('study-spec.example.json must be a ready schema version 1 example.');
  process.exit(1);
}

const contextProtocol = fs.readFileSync(
  path.join(SKILL_SOURCE, 'references', 'EXECUTION_CONTEXT.md'),
  'utf8'
);
for (const requiredText of [
  'Omission is the default',
  'CONTEXT.md',
  'Scoped context files',
  'single TODO',
  'source_refs',
  'contexts_minimal'
]) {
  if (!contextProtocol.includes(requiredText)) {
    console.error(`EXECUTION_CONTEXT.md is missing required protocol text: ${requiredText}`);
    process.exit(1);
  }
}

const planctl = fs.readFileSync(path.join(SKILL_SOURCE, 'scripts', 'planctl.py'), 'utf8');
for (const requiredText of [
  'SCHEMA_VERSION = 3',
  'GLOBAL_CONTEXT_FILE = "CONTEXT.md"',
  'normalize_execution_context',
  'validate_context_artifacts',
  'contexts_minimal'
]) {
  if (!planctl.includes(requiredText)) {
    console.error(`planctl.py is missing execution-context support: ${requiredText}`);
    process.exit(1);
  }
}

const completionSchema = JSON.parse(
  fs.readFileSync(path.join(SKILL_SOURCE, 'references', 'completion-report.schema.json'), 'utf8')
);
if (!completionSchema.required?.includes('context_files_read')) {
  console.error('completion-report.schema.json must require context_files_read.');
  process.exit(1);
}

const readme = fs.readFileSync(path.join(process.cwd(), 'README.md'), 'utf8');
if (!readme.startsWith('# Plan and Execute\n\n**Turn large coding requests into an evidence-backed')) {
  console.error('README.md must begin with the evidence-backed outcome introduction.');
  process.exit(1);
}
if (!readme.includes('## Adaptive study gate')) {
  console.error('README.md must document the adaptive study gate.');
  process.exit(1);
}
if (!readme.includes('## Progressive execution context')) {
  console.error('README.md must document progressive execution context.');
  process.exit(1);
}
if (!fs.existsSync(path.join(process.cwd(), 'README.pt-BR.md'))) {
  console.error('README.pt-BR.md is required.');
  process.exit(1);
}

const packageMetadata = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8'));
if (packageMetadata.version !== '0.6.0') {
  console.error(`Expected package version 0.6.0, found ${packageMetadata.version}.`);
  process.exit(1);
}
if (!packageMetadata.repository?.url?.includes('heavydevs/plan-and-execute')) {
  console.error('package.json must point to heavydevs/plan-and-execute.');
  process.exit(1);
}

console.log(
  `Skill ${SKILL_NAME} validated (${skillFiles.length} files, sha256 ${computeDirectoryHash(SKILL_SOURCE)}).`
);
