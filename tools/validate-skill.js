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
function read(relativePath) {
  return fs.readFileSync(requireFile(relativePath), 'utf8');
}
function requireText(text, needles, label) {
  for (const needle of needles) {
    if (!text.includes(needle)) fail(`${label} is missing required text: ${needle}`);
  }
}
function requireMax(text, maximum, label) {
  if (text.length > maximum) fail(`${label} is too large: ${text.length} > ${maximum}`);
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
  path.join('references', 'ROUTING.md'),
  path.join('references', 'PROMOTION.md'),
  path.join('references', 'ORCHESTRATION.md'),
  path.join('references', 'routing-evals.json'),
  path.join('references', 'ADAPTIVE_STUDY.md'),
  path.join('references', 'ARTIFACT_WRITING.md'),
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
  path.join('scripts', 'promotectl.py'),
  path.join('scripts', 'routing_self_test.py'),
  path.join('scripts', 'promotion_self_test.py'),
  path.join('scripts', 'artifact_contract.py'),
  path.join('scripts', 'runner_contract.py'),
  path.join('scripts', 'planctl_concise.py'),
  path.join('scripts', 'studyctl_concise.py'),
  path.join('scripts', 'lifecyclectl_concise.py'),
  path.join('scripts', 'run_concise.py'),
  path.join('scripts', 'planctl.py'),
  path.join('scripts', 'studyctl.py'),
  path.join('scripts', 'run_isolated.py'),
  path.join('scripts', 'token_efficiency_self_test.py'),
  path.join('scripts', 'artifact_concision_self_test.py')
]) requireFile(relative);

const metadata = read(path.join('agents', 'openai.yaml'));
requireText(metadata, [
  'display_name: Plan and Execute',
  'DIRECT vs ORCHESTRATED',
  'cohesive small/medium work',
  'remaining outcomes',
  'provider/model tier/effort',
  'deterministic validation',
  'implementation changes',
  'allow_implicit_invocation: true'
], 'agents/openai.yaml');
requireMax(metadata, 1500, 'agents/openai.yaml');

const skill = read('SKILL.md');
requireText(skill, [
  'Treat context as a budget',
  'Decide DIRECT vs ORCHESTRATED',
  'DIRECT EXIT',
  'create no `.ai-work`',
  'When uncertain, prefer DIRECT',
  'references/ROUTING.md',
  'references/PROMOTION.md',
  'references/ORCHESTRATION.md',
  'remaining outcomes',
  '`provider`, `model_tier`, and `reasoning_effort`',
  'quota/rate-limit exhaustion',
  'without the previous chat transcript',
  'implementation changes'
], 'SKILL.md');
requireMax(skill, 7000, 'SKILL.md');
const frontmatter = skill.match(/^---\n([\s\S]*?)\n---/);
if (!frontmatter) fail('SKILL.md frontmatter is missing.');
if (frontmatter[1].length > 1700) fail('SKILL.md frontmatter is too broad for cheap routing.');
if (!frontmatter[1].includes('Do not use for routine bug fixes')) {
  fail('SKILL.md description must contain near-miss negative routing guidance.');
}
if (frontmatter[1].includes('Use for implementations, migrations, refactors')) {
  fail('SKILL.md description still contains the old catch-all implementation trigger.');
}
if (/^disable-model-invocation:\s*true$/m.test(frontmatter[1])) {
  fail('Bundled source must remain selective; explicit-only is an installer variant.');
}

const routing = read(path.join('references', 'ROUTING.md'));
requireText(routing, [
  'uncertainty -> DIRECT',
  'File count is weak evidence',
  'Context pressure is secondary evidence',
  '75-85%',
  'near-miss negatives'
], 'ROUTING.md');
requireMax(routing, 9000, 'ROUTING.md');

const promotion = read(path.join('references', 'PROMOTION.md'));
requireText(promotion, [
  'remaining implementation only',
  'Never create retroactive TODOs',
  'promotectl.py validate',
  'promotectl.py render',
  'model_tier',
  'reasoning_effort'
], 'PROMOTION.md');
requireMax(promotion, 9000, 'PROMOTION.md');

const orchestration = read(path.join('references', 'ORCHESTRATION.md'));
requireText(orchestration, [
  'TODO.md',
  'manifest.json',
  'provider',
  'model_tier',
  'reasoning_effort',
  'quota',
  'fresh worker',
  'cleanup'
], 'ORCHESTRATION.md');
requireMax(orchestration, 12000, 'ORCHESTRATION.md');

const tokenProtocol = read(path.join('references', 'TOKEN_EFFICIENCY.md'));
requireText(tokenProtocol, [
  'Avoid the harness when the harness does not pay for itself',
  'Fresh workers are not automatically cheaper',
  'Promote instead of restarting',
  'Progressive disclosure',
  'Search first, read second',
  'Preserve stable provider prefixes and logical routing',
  'Never optimize away quality anchors'
], 'TOKEN_EFFICIENCY.md');
requireMax(tokenProtocol, 10000, 'TOKEN_EFFICIENCY.md');

const writing = read(path.join('references', 'ARTIFACT_WRITING.md'));
requireText(writing, ['one field, one job', 'Vague wording rejected', 'Derived-text budgets'], 'ARTIFACT_WRITING.md');
const planning = read(path.join('references', 'PLANNING_PROTOCOL.md'));
requireText(planning, ['context_boundary', 'learning_targets', 'contexts_minimal', 'context_boundaries_sound'], 'PLANNING_PROTOCOL.md');
const planSpec = read(path.join('references', 'PLAN_SPEC.md'));
requireText(planSpec, ['schema v4', 'request_analysis', 'context_boundary', 'learning_targets', 'model_tier', 'reasoning_effort'], 'PLAN_SPEC.md');
const workflow = read(path.join('references', 'WORKFLOW.md'));
requireText(workflow, ['Fresh workers', 'SUMMARY_INPUT.json'], 'WORKFLOW.md');
const contextProtocol = read(path.join('references', 'EXECUTION_CONTEXT.md'));
requireText(contextProtocol, ['Omission is the default', 'CONTEXT.md', 'Validated execution learnings'], 'EXECUTION_CONTEXT.md');

const promotionController = read(path.join('scripts', 'promotectl.py'));
requireText(promotionController, [
  'SCHEMA_VERSION = 1',
  'remaining_outcomes',
  'context_pressure',
  'git_snapshot',
  'Plan and execute ONLY the remaining outcomes'
], 'promotectl.py');

const evalCorpus = JSON.parse(read(path.join('references', 'routing-evals.json')));
if (!Array.isArray(evalCorpus.cases) || evalCorpus.cases.length < 25) {
  fail('routing-evals.json must contain at least 25 routing regression cases.');
}
if (!evalCorpus.cases.some((item) => item.expected_route === 'direct' && item.near_miss)) {
  fail('routing-evals.json must contain direct near-miss negatives.');
}
if (!evalCorpus.cases.some((item) => item.expected_route === 'orchestrated')) {
  fail('routing-evals.json must contain positive orchestration cases.');
}
if (!evalCorpus.cases.some((item) => item.expected_route === 'promote')) {
  fail('routing-evals.json must contain late-promotion cases.');
}

const artifactContract = read(path.join('scripts', 'artifact_contract.py'));
requireText(artifactContract, ['VAGUE_PATTERNS', 'PLAN_BUDGETS', 'render_task'], 'artifact_contract.py');
const runnerContract = read(path.join('scripts', 'runner_contract.py'));
requireText(runnerContract, ['output_tail', 'SUMMARY_INPUT.json', 'completion_summary'], 'runner_contract.py');
const planctl = read(path.join('scripts', 'planctl.py'));
requireText(planctl, [
  'SCHEMA_VERSION = 4',
  'VALID_SUBTASK_STATUSES',
  'VALID_LEARNING_KINDS',
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
if (!planExample.tasks.every((task) => task.provider && task.model_tier && task.reasoning_effort)) {
  fail('plan-spec.example.json must preserve per-TODO provider/model tier/reasoning effort.');
}

const packageMetadata = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'package.json'), 'utf8'));
if (!packageMetadata.repository?.url?.includes('heavydevs/plan-and-execute')) {
  fail('package.json must point to heavydevs/plan-and-execute.');
}

console.log(`Skill ${SKILL_NAME} validated (${skillFiles.length} files, sha256 ${computeDirectoryHash(SKILL_SOURCE)}).`);
