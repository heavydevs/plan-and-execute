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

function read(relativePath) {
  return fs.readFileSync(requireFile(relativePath), 'utf8');
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

const forbidden = [
  'long-task-orchestrator',
  'github.com/luizcgvrj/plan-and-execute',
  'github:luizcgvrj/plan-and-execute'
];
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
  for (const needle of forbidden) {
    if (buffer.includes(Buffer.from(needle))) {
      fail(`Forbidden legacy reference ${needle} found in ${path.relative(process.cwd(), file)}`);
    }
  }
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
  path.join('references', 'TOKEN_EFFICIENCY.md'),
  path.join('references', 'completion-report.schema.json'),
  path.join('references', 'plan-spec.example.json'),
  path.join('references', 'study-spec.example.json'),
  path.join('scripts', 'planctl.py'),
  path.join('scripts', 'studyctl.py'),
  path.join('scripts', 'run_isolated.py'),
  path.join('scripts', 'token_efficiency_self_test.py')
]) requireFile(relative);

const metadata = read(path.join('agents', 'openai.yaml'));
requireText(metadata, [
  'display_name: Plan and Execute',
  'Treat context as a budget',
  'fresh isolated worker',
  'deterministic validation',
  'planning/control workspace',
  'implementation changes'
], 'agents/openai.yaml');
if (metadata.length > 1400) fail(`agents/openai.yaml is too large for the always-loaded surface: ${metadata.length}`);

const skill = read('SKILL.md');
requireText(skill, [
  'Treat context as a budget',
  'Route lifecycle commands first',
  'Pass the adaptive study gate',
  'references/ADAPTIVE_STUDY.md',
  'references/PLANNING_PROTOCOL.md',
  'references/EXECUTION_CONTEXT.md',
  'references/WORKFLOW.md',
  'references/MODEL_ROUTING.md',
  'references/TOKEN_EFFICIENCY.md',
  'contexts_minimal',
  'context_boundaries_sound',
  'fresh worker',
  'deterministic validation',
  'planctl.py cleanup',
  'Preserve all implementation changes'
], 'SKILL.md');
if (skill.length > 14000) fail(`SKILL.md is too large for the always-loaded control plane: ${skill.length}`);

const studyProtocol = read(path.join('references', 'ADAPTIVE_STUDY.md'));
requireText(studyProtocol, [
  'Classify the request before broad repository inspection',
  'Pacotes relacionados',
  'Busca por palavras-chave em todo o workspace',
  'Projeto completo',
  'Sem estudo externo',
  'Pesquisa focalizada',
  'Pesquisa ampla',
  'studyctl.py attach'
], 'ADAPTIVE_STUDY.md');

const planningProtocol = read(path.join('references', 'PLANNING_PROTOCOL.md'));
requireText(planningProtocol, [
  'context_boundary',
  'learning_targets',
  'contexts_minimal',
  'context_boundaries_sound'
], 'PLANNING_PROTOCOL.md');

const contextProtocol = read(path.join('references', 'EXECUTION_CONTEXT.md'));
requireText(contextProtocol, [
  'Omission is the default',
  'CONTEXT.md',
  'source_refs',
  'Validated execution learnings',
  'learning_files_read'
], 'EXECUTION_CONTEXT.md');

const tokenProtocol = read(path.join('references', 'TOKEN_EFFICIENCY.md'));
requireText(tokenProtocol, [
  'Spend model tokens only on judgment',
  'Progressive disclosure beats one large prompt',
  'Search first, read second',
  'Fresh workers are cheaper than polluted long histories',
  'Preserve stable prefixes for provider prompt caching',
  'Bound tool and report output',
  'Never optimize away these quality anchors'
], 'TOKEN_EFFICIENCY.md');

const planctl = read(path.join('scripts', 'planctl.py'));
requireText(planctl, [
  'SCHEMA_VERSION = 4',
  'CONTEXT_BOUNDARY_REVIEW_CHECK = "context_boundaries_sound"',
  'VALID_SUBTASK_STATUSES',
  'VALID_LEARNING_KINDS',
  'materialize_learning_artifacts',
  'def cleanup_plan',
  'shutil.rmtree(plan_dir)'
], 'planctl.py');
for (const provider of ['claude', 'codex', 'gemini', 'qwen', 'kimi', 'trae']) {
  if (!planctl.includes(`"${provider}"`)) fail(`planctl.py must support provider ${provider}.`);
}

const completionSchema = JSON.parse(read(path.join('references', 'completion-report.schema.json')));
for (const field of ['context_files_read', 'learning_files_read', 'completed_subtask_ids', 'reusable_learnings']) {
  if (!completionSchema.required?.includes(field)) fail(`completion-report.schema.json must require ${field}.`);
}

const studyExample = JSON.parse(read(path.join('references', 'study-spec.example.json')));
if (studyExample.schema_version !== 2 || !studyExample.synthesis?.ready_for_planning) {
  fail('study-spec.example.json must demonstrate a ready schema-v2 study.');
}

const planExample = JSON.parse(read(path.join('references', 'plan-spec.example.json')));
if (!planExample.tasks?.length || !planExample.tasks.every((task) => task.context_boundary && task.subtasks?.length)) {
  fail('plan-spec.example.json must contain context boundaries and resumable subtasks.');
}
if (planExample.plan_review?.contexts_minimal !== true || planExample.plan_review?.context_boundaries_sound !== true) {
  fail('plan-spec.example.json must approve context minimality and context boundaries.');
}

const packageMetadata = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8'));
if (!packageMetadata.repository?.url?.includes('heavydevs/plan-and-execute')) {
  fail('package.json must point to heavydevs/plan-and-execute.');
}

console.log(`Skill ${SKILL_NAME} validated (${skillFiles.length} files, sha256 ${computeDirectoryHash(SKILL_SOURCE)}).`);
