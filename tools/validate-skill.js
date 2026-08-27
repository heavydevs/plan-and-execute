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

function fail(message) {
  console.error(message);
  process.exit(1);
}

function requireFile(relativePath) {
  const absolute = path.join(SKILL_SOURCE, relativePath);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    fail(`Bundled skill is missing ${relativePath}.`);
  }
  return absolute;
}

function requireText(text, needles, label) {
  for (const needle of needles) {
    if (!text.includes(needle)) fail(`${label} is missing required text: ${needle}`);
  }
}

validateBundledSkill();

const skillFiles = [];
function walk(directory, output) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(absolute, output);
    else if (entry.isFile()) output.push(absolute);
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
  if (path.relative(process.cwd(), file) === path.join('tools', 'validate-skill.js')) continue;
  const buffer = fs.readFileSync(file);
  for (const [needle, matches] of forbidden) {
    if (buffer.includes(Buffer.from(needle))) matches.push(path.relative(process.cwd(), file));
  }
}
for (const [needle, matches] of forbidden) {
  if (matches.length > 0) fail(`Forbidden legacy reference ${needle} found in: ${matches.join(', ')}`);
}

for (const relative of [
  'SKILL.md',
  path.join('agents', 'openai.yaml'),
  path.join('references', 'ADAPTIVE_STUDY.md'),
  path.join('references', 'EXECUTION_CONTEXT.md'),
  path.join('references', 'PLANNING_PROTOCOL.md'),
  path.join('references', 'PLAN_SPEC.md'),
  path.join('references', 'WORKFLOW.md'),
  path.join('references', 'LIFECYCLE.md'),
  path.join('references', 'MODEL_ROUTING.md'),
  path.join('references', 'completion-report.schema.json'),
  path.join('references', 'plan-spec.example.json'),
  path.join('references', 'study-spec.example.json'),
  path.join('scripts', 'studyctl.py'),
  path.join('scripts', 'study_self_test.py'),
  path.join('scripts', 'context_self_test.py'),
  path.join('scripts', 'lifecycle_self_test.py'),
  path.join('scripts', 'task_memory_self_test.py'),
  path.join('scripts', 'provider_self_test.py')
]) requireFile(relative);

const metadata = fs.readFileSync(requireFile(path.join('agents', 'openai.yaml')), 'utf8');
requireText(metadata, [
  'display_name: Plan and Execute',
  'adaptive study',
  'resume',
  'execution context',
  'context_boundaries_sound',
  'validated-learning',
  'resumable'
], 'agents/openai.yaml');

const skill = fs.readFileSync(requireFile('SKILL.md'), 'utf8');
requireText(skill, [
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
  'context_boundaries_sound',
  'Assigned execution context',
  'Assigned validated learnings',
  'Resumable subtask checklist',
  'Gemini CLI',
  'Qwen Code',
  'Kimi Code CLI',
  'Trae Agent'
], 'SKILL.md');

const studyProtocol = fs.readFileSync(requireFile(path.join('references', 'ADAPTIVE_STUDY.md')), 'utf8');
requireText(studyProtocol, [
  'Classify the request before broad repository inspection',
  'Fixed study choices for complex requests',
  'Pacotes relacionados',
  'Busca por palavras-chave em todo o workspace',
  'Projeto completo',
  'Sem estudo externo',
  'Pesquisa focalizada',
  'Pesquisa ampla',
  'user_requested',
  'version_sensitive',
  'security_sensitive',
  'studyctl.py attach',
  'internal_study.plan_finding'
], 'ADAPTIVE_STUDY.md');

const studyExample = JSON.parse(fs.readFileSync(requireFile(path.join('references', 'study-spec.example.json')), 'utf8'));
if (
  studyExample.schema_version !== 2 ||
  studyExample.complexity_assessment?.level !== 'complex' ||
  studyExample.internal_study?.selection_source !== 'user' ||
  studyExample.internal_study?.depth !== 'workspace_keywords' ||
  studyExample.external_research?.selection_source !== 'user' ||
  studyExample.external_research?.depth !== 'focused' ||
  !studyExample.synthesis?.ready_for_planning
) {
  fail('study-spec.example.json must demonstrate the ready schema-v2 complex-request choice contract.');
}

const contextProtocol = fs.readFileSync(requireFile(path.join('references', 'EXECUTION_CONTEXT.md')), 'utf8');
requireText(contextProtocol, [
  'Omission is the default',
  'CONTEXT.md',
  'Scoped context files',
  'single TODO',
  'source_refs',
  'contexts_minimal',
  'Validated execution learnings',
  'learning_files_read'
], 'EXECUTION_CONTEXT.md');

const planctl = fs.readFileSync(requireFile(path.join('scripts', 'planctl.py')), 'utf8');
requireText(planctl, [
  'SCHEMA_VERSION = 4',
  'SUPPORTED_SCHEMA_VERSIONS = {1, 2, 3, 4}',
  'CONTEXT_BOUNDARY_REVIEW_CHECK = "context_boundaries_sound"',
  'VALID_SUBTASK_STATUSES',
  'VALID_LEARNING_KINDS',
  'normalize_execution_context',
  'validate_context_artifacts',
  'materialize_learning_artifacts',
  'subtask-start',
  'subtask-complete',
  'provider_order": ["claude", "codex"]'
], 'planctl.py');
for (const provider of ['claude', 'codex', 'gemini', 'qwen', 'kimi', 'trae']) {
  if (!planctl.includes(`"${provider}"`)) fail(`planctl.py must support provider ${provider}.`);
}

const completionSchema = JSON.parse(
  fs.readFileSync(requireFile(path.join('references', 'completion-report.schema.json')), 'utf8')
);
for (const field of [
  'context_files_read',
  'learning_files_read',
  'completed_subtask_ids',
  'reusable_learnings'
]) {
  if (!completionSchema.required?.includes(field)) {
    fail(`completion-report.schema.json must require ${field}.`);
  }
}

const planExample = JSON.parse(
  fs.readFileSync(requireFile(path.join('references', 'plan-spec.example.json')), 'utf8')
);
if (!planExample.tasks?.length || !planExample.tasks.every((task) => (
  task.context_boundary && Array.isArray(task.subtasks) && task.subtasks.length > 0
))) {
  fail('plan-spec.example.json must contain schema-v4 context boundaries and subtasks.');
}
if (planExample.plan_review?.context_boundaries_sound !== true) {
  fail('plan-spec.example.json must approve context_boundaries_sound.');
}

const readme = fs.readFileSync(path.join(process.cwd(), 'README.md'), 'utf8');
requireText(readme, [
  '# Plan and Execute',
  '## Supported AI workers',
  '## Quick start: Claude Code and Codex',
  '## Why TODO boundaries matter',
  '## Resumable subtasks inside every TODO',
  '## Selective validated learning',
  '## Adaptive study gate',
  '## Progressive execution context',
  'Gemini CLI',
  'Qwen Code',
  'Kimi Code CLI',
  'Trae Agent',
  '"provider_order": ["claude", "codex"]'
], 'README.md');
const readmePt = fs.readFileSync(path.join(process.cwd(), 'README.pt-BR.md'), 'utf8');
requireText(readmePt, [
  '## IAs suportadas para execução',
  '## Tutorial rápido: Claude Code e Codex',
  '## Por que a fronteira dos TODOs importa',
  '## Subtarefas retomáveis dentro de cada TODO',
  '## Aprendizado validado e seletivo'
], 'README.pt-BR.md');

const packageMetadata = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8'));
if (packageMetadata.version !== '0.7.0') {
  fail(`Expected package version 0.7.0, found ${packageMetadata.version}.`);
}
if (!packageMetadata.repository?.url?.includes('heavydevs/plan-and-execute')) {
  fail('package.json must point to heavydevs/plan-and-execute.');
}

console.log(`Skill ${SKILL_NAME} validated (${skillFiles.length} files, sha256 ${computeDirectoryHash(SKILL_SOURCE)}).`);
