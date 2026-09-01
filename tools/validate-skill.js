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
  'Treat context as a budget',
  'fresh isolated worker',
  'deterministic validation',
  'planning/control workspace',
  'implementation changes'
], 'agents/openai.yaml');
requireMax(metadata, 1400, 'agents/openai.yaml');

const skill = read('SKILL.md');
requireText(skill, [
  'Treat context as a budget',
  'original request',
  'references/ARTIFACT_WRITING.md',
  'references/ADAPTIVE_STUDY.md',
  'references/PLANNING_PROTOCOL.md',
  'references/EXECUTION_CONTEXT.md',
  'references/WORKFLOW.md',
  'references/MODEL_ROUTING.md',
  'references/TOKEN_EFFICIENCY.md',
  'contexts_minimal',
  'context_boundaries_sound',
  'planctl_concise.py',
  'studyctl_concise.py',
  'lifecyclectl_concise.py',
  'run_concise.py',
  'deterministic validation',
  'Preserve all implementation changes'
], 'SKILL.md');
requireMax(skill, 12000, 'SKILL.md');

const writing = read(path.join('references', 'ARTIFACT_WRITING.md'));
requireText(writing, [
  'one field, one job',
  'Vague wording rejected',
  'Derived-text budgets',
  'EARS-like',
  'original request',
  'final handoff'
], 'ARTIFACT_WRITING.md');
requireMax(writing, 14000, 'ARTIFACT_WRITING.md');

const planning = read(path.join('references', 'PLANNING_PROTOCOL.md'));
requireText(planning, [
  'context_boundary',
  'learning_targets',
  'contexts_minimal',
  'context_boundaries_sound',
  'Deterministic quality gates',
  'planctl_concise.py'
], 'PLANNING_PROTOCOL.md');
requireMax(planning, 12000, 'PLANNING_PROTOCOL.md');

const planSpec = read(path.join('references', 'PLAN_SPEC.md'));
requireText(planSpec, [
  'schema v4',
  'request_analysis',
  'execution_context',
  'context_boundary',
  'learning_targets',
  'planctl_concise.py'
], 'PLAN_SPEC.md');
requireMax(planSpec, 12000, 'PLAN_SPEC.md');

const workflow = read(path.join('references', 'WORKFLOW.md'));
requireText(workflow, [
  'planctl_concise.py',
  'run_concise.py',
  'Fresh workers',
  'Never concatenate raw worker reports',
  'SUMMARY_INPUT.json'
], 'WORKFLOW.md');
requireMax(workflow, 12000, 'WORKFLOW.md');

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
  'Final summary uses compact authoritative state',
  'Never optimize away these quality anchors'
], 'TOKEN_EFFICIENCY.md');
requireMax(tokenProtocol, 10000, 'TOKEN_EFFICIENCY.md');

const artifactContract = read(path.join('scripts', 'artifact_contract.py'));
requireText(artifactContract, [
  'VAGUE_PATTERNS',
  'PLAN_BUDGETS',
  'STUDY_BUDGETS',
  'completion_summary',
  'render_task',
  'render_learning_artifact',
  'install_plan_contract',
  'install_study_contract'
], 'artifact_contract.py');

const runnerContract = read(path.join('scripts', 'runner_contract.py'));
requireText(runnerContract, [
  'output_tail',
  'SUMMARY_INPUT.json',
  'completion_summary',
  'Return only the handoff Markdown'
], 'runner_contract.py');

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
if (completionSchema.properties?.summary?.maxLength !== 360) fail('completion summary must be capped at 360 chars.');
if (completionSchema.properties?.validations?.items?.properties?.details?.maxLength !== 600) fail('validation details must be capped at 600 chars.');
if (completionSchema.properties?.risks?.maxItems !== 8 || completionSchema.properties?.follow_ups?.maxItems !== 8) {
  fail('completion risks/follow_ups must be capped at 8 items.');
}
if (completionSchema.properties?.reusable_learnings?.items?.properties?.guidance?.maxLength !== 320) {
  fail('reusable learning guidance must be capped at 320 chars.');
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
