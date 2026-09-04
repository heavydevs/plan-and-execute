import { spawnSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const moduleDirectory = path.dirname(fileURLToPath(import.meta.url));
const packageRoot = path.resolve(moduleDirectory, '..');
const packageMetadata = JSON.parse(
  fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')
);

export const PACKAGE_NAME = packageMetadata.name;
export const SKILL_NAME = 'plan-and-execute';
export const SKILL_SOURCE = path.join(packageRoot, 'skill', SKILL_NAME);
export const INSTALL_MARKER = '.plan-and-execute-install.json';
export const ACTIVATION_MODES = Object.freeze(['selective', 'explicit']);

const AGENT_CONFIG = Object.freeze({
  claude: path.join('.claude', 'skills'),
  codex: path.join('.agents', 'skills')
});

const HASH_EXCLUDED_BASENAMES = new Set([
  INSTALL_MARKER,
  '.DS_Store'
]);

function lstatIfPresent(targetPath) {
  try {
    return fs.lstatSync(targetPath);
  } catch (error) {
    if (error?.code === 'ENOENT') return null;
    throw error;
  }
}

function readJsonIfPresent(filePath) {
  if (!lstatIfPresent(filePath)) return null;
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return null;
  }
}

export function getPackageVersion() {
  return packageMetadata.version;
}

export function readSkillName(skillDirectory) {
  const skillFile = path.join(skillDirectory, 'SKILL.md');
  if (!lstatIfPresent(skillFile)) return null;
  const text = fs.readFileSync(skillFile, 'utf8');
  const frontmatter = text.match(/^---\s*\r?\n([\s\S]*?)^---\s*$/m);
  if (!frontmatter) return null;
  const name = frontmatter[1].match(/^name:\s*['"]?([^'"\r\n]+)['"]?\s*$/m);
  return name ? name[1].trim() : null;
}

function shouldExcludeFromHash(relativePath) {
  const normalized = relativePath.split(path.sep);
  const basename = normalized.at(-1);
  return (
    HASH_EXCLUDED_BASENAMES.has(basename)
    || normalized.includes('__pycache__')
    || basename.endsWith('.pyc')
  );
}

function collectFiles(rootDirectory, currentDirectory = rootDirectory, output = []) {
  const entries = fs.readdirSync(currentDirectory, { withFileTypes: true })
    .sort((left, right) => left.name.localeCompare(right.name));
  for (const entry of entries) {
    const absolutePath = path.join(currentDirectory, entry.name);
    const relativePath = path.relative(rootDirectory, absolutePath);
    if (shouldExcludeFromHash(relativePath)) continue;
    if (entry.isSymbolicLink()) {
      throw new Error(`Link simbolico nao permitido dentro da skill: ${relativePath}`);
    }
    if (entry.isDirectory()) {
      collectFiles(rootDirectory, absolutePath, output);
      continue;
    }
    if (entry.isFile()) output.push(relativePath);
  }
  return output;
}

export function computeDirectoryHash(directory) {
  const stat = lstatIfPresent(directory);
  if (!stat?.isDirectory() || stat.isSymbolicLink()) {
    throw new Error(`Diretorio invalido para hash: ${directory}`);
  }
  const hash = crypto.createHash('sha256');
  hash.update('plan-and-execute-directory-v1\0');
  for (const relativePath of collectFiles(directory)) {
    const normalizedPath = relativePath.split(path.sep).join('/');
    hash.update(normalizedPath);
    hash.update('\0');
    hash.update(fs.readFileSync(path.join(directory, relativePath)));
    hash.update('\0');
  }
  return hash.digest('hex');
}

export function validateBundledSkill(sourceDirectory = SKILL_SOURCE) {
  const stat = lstatIfPresent(sourceDirectory);
  if (!stat?.isDirectory() || stat.isSymbolicLink()) {
    throw new Error(`Diretorio da skill nao encontrado ou invalido: ${sourceDirectory}`);
  }
  const actualName = readSkillName(sourceDirectory);
  if (actualName !== SKILL_NAME) {
    throw new Error(
      `SKILL.md invalido: esperado name=${SKILL_NAME}, encontrado ${actualName ?? 'nenhum'}`
    );
  }
  const required = [
    'SKILL.md',
    path.join('agents', 'openai.yaml'),
    path.join('scripts', 'planctl.py'),
    path.join('scripts', 'requestctl.py'),
    path.join('scripts', 'run_isolated.py'),
    path.join('scripts', 'run_concise.py'),
    path.join('scripts', 'runner_contract.py'),
    path.join('scripts', 'self_test.py'),
    path.join('scripts', 'promotectl.py'),
    path.join('scripts', 'routing_self_test.py'),
    path.join('scripts', 'promotion_self_test.py'),
    path.join('references', 'INTAKE.md'),
    path.join('scripts', 'lifecyclectl.py'),
    path.join('scripts', 'lifecycle_self_test.py'),
    path.join('references', 'LIFECYCLE.md'),
    path.join('references', 'EXECUTION_CONTEXT.md'),
    path.join('references', 'ORCHESTRATION.md'),
    path.join('references', 'ROUTING.md'),
    path.join('references', 'PROMOTION.md'),
    path.join('references', 'routing-evals.json'),
    path.join('scripts', 'context_self_test.py'),
    path.join('scripts', 'task_memory_self_test.py'),
    path.join('scripts', 'provider_self_test.py'),
    path.join('assets', 'icon.svg')
  ];
  for (const relativePath of required) {
    const absolutePath = path.join(sourceDirectory, relativePath);
    if (!lstatIfPresent(absolutePath)?.isFile()) {
      throw new Error(`Arquivo obrigatorio ausente na skill: ${relativePath}`);
    }
  }
  computeDirectoryHash(sourceDirectory);
  return true;
}

function normalizeAgent(agent) {
  const value = String(agent ?? 'both').toLowerCase();
  if (!['claude', 'codex', 'both'].includes(value)) {
    throw new Error(`Agente invalido: ${agent}. Use claude, codex ou both.`);
  }
  return value;
}

function normalizeScope(scope) {
  const value = String(scope ?? 'workspace').toLowerCase();
  if (['workspace', 'project', 'local'].includes(value)) return 'workspace';
  if (['user', 'global', 'machine', 'personal'].includes(value)) return 'user';
  throw new Error(
    `Escopo invalido: ${scope}. Use workspace/project/local ou user/global.`
  );
}

export function normalizeActivation(activation) {
  const value = String(activation ?? 'selective').trim().toLowerCase();
  if (['selective', 'auto', 'automatic'].includes(value)) return 'selective';
  if (['explicit', 'manual', 'user-only', 'user_only'].includes(value)) return 'explicit';
  throw new Error(
    `Modo de ativacao invalido: ${activation}. Use selective ou explicit.`
  );
}

export function resolveTargets({
  agent = 'both',
  scope = 'workspace',
  workspaceDir,
  projectDir,
  homeDir = os.homedir()
} = {}) {
  const normalizedAgent = normalizeAgent(agent);
  const normalizedScope = normalizeScope(scope);
  const selectedAgents = normalizedAgent === 'both' ? ['claude', 'codex'] : [normalizedAgent];
  const workspace = workspaceDir ?? projectDir ?? process.cwd();
  const baseDirectory = normalizedScope === 'workspace'
    ? path.resolve(workspace)
    : path.resolve(homeDir);
  return selectedAgents.map((agentName) => ({
    agent: agentName,
    scope: normalizedScope,
    destination: path.join(baseDirectory, AGENT_CONFIG[agentName], SKILL_NAME)
  }));
}

function markerActivation(marker) {
  try {
    return normalizeActivation(marker?.activation ?? 'selective');
  } catch {
    return 'selective';
  }
}

function inspectOwnership(destination) {
  const stat = lstatIfPresent(destination);
  if (!stat) {
    return {
      exists: false, isDirectory: false, isSymlink: false, owned: false,
      valid: false, managed: false, modified: null, skillName: null,
      marker: null, currentHash: null, expectedInstalledHash: null,
      activation: null
    };
  }
  if (stat.isSymbolicLink()) {
    return {
      exists: true, isDirectory: false, isSymlink: true, owned: false,
      valid: false, managed: false, modified: null, skillName: null,
      marker: null, currentHash: null, expectedInstalledHash: null,
      activation: null
    };
  }
  if (!stat.isDirectory()) {
    return {
      exists: true, isDirectory: false, isSymlink: false, owned: false,
      valid: false, managed: false, modified: null, skillName: null,
      marker: null, currentHash: null, expectedInstalledHash: null,
      activation: null
    };
  }

  const skillName = readSkillName(destination);
  const marker = readJsonIfPresent(path.join(destination, INSTALL_MARKER));
  const schemaVersion = Number(marker?.schemaVersion ?? 0);
  const managed = (
    [1, 2].includes(schemaVersion)
    && marker?.skill === SKILL_NAME
    && typeof marker?.sourceHash === 'string'
  );
  const owned = skillName === SKILL_NAME || marker?.skill === SKILL_NAME;
  const expectedInstalledHash = managed
    ? (typeof marker?.installedHash === 'string' ? marker.installedHash : marker.sourceHash)
    : null;
  let currentHash = null;
  let modified = null;
  try {
    currentHash = computeDirectoryHash(destination);
    modified = managed ? currentHash !== expectedInstalledHash : null;
  } catch {
    modified = managed ? true : null;
  }
  return {
    exists: true,
    isDirectory: true,
    isSymlink: false,
    owned,
    valid: skillName === SKILL_NAME,
    managed,
    modified,
    skillName,
    marker,
    currentHash,
    expectedInstalledHash,
    activation: managed ? markerActivation(marker) : null
  };
}

function createUniqueSibling(destination, label) {
  const parent = path.dirname(destination);
  const token = `${process.pid}-${Date.now()}-${crypto.randomBytes(6).toString('hex')}`;
  return path.join(parent, `.${path.basename(destination)}.${label}-${token}`);
}

function removeIfPresent(targetPath) {
  if (lstatIfPresent(targetPath)) fs.rmSync(targetPath, { recursive: true, force: true });
}

function makeError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function setClaudeModelInvocation(skillFile, enabled) {
  const text = fs.readFileSync(skillFile, 'utf8');
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---(\r?\n|$)/);
  if (!match) throw new Error('SKILL.md sem frontmatter valido para configurar ativacao.');
  let frontmatter = match[1]
    .split(/\r?\n/)
    .filter((line) => !/^\s*disable-model-invocation\s*:/.test(line))
    .join('\n')
    .trimEnd();
  if (!enabled) frontmatter += '\ndisable-model-invocation: true';
  const replacement = `---\n${frontmatter}\n---${match[2] || '\n'}`;
  fs.writeFileSync(skillFile, replacement + text.slice(match[0].length), 'utf8');
}

function setCodexImplicitInvocation(metadataFile, enabled) {
  let text = fs.readFileSync(metadataFile, 'utf8');
  const value = enabled ? 'true' : 'false';
  if (/^\s*allow_implicit_invocation\s*:/m.test(text)) {
    text = text.replace(
      /^(\s*allow_implicit_invocation\s*:)\s*.*$/m,
      `$1 ${value}`
    );
  } else if (/^policy\s*:\s*$/m.test(text)) {
    text = text.replace(/^policy\s*:\s*$/m, `policy:\n  allow_implicit_invocation: ${value}`);
  } else {
    text = `${text.trimEnd()}\npolicy:\n  allow_implicit_invocation: ${value}\n`;
  }
  fs.writeFileSync(metadataFile, text, 'utf8');
}

function prepareVariant(sourceDirectory, agent, activation) {
  if (activation === 'selective') {
    return {
      directory: sourceDirectory,
      installedHash: computeDirectoryHash(sourceDirectory),
      cleanup: () => {}
    };
  }
  const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'plan-and-execute-variant-'));
  const variantDirectory = path.join(temporaryRoot, SKILL_NAME);
  fs.cpSync(sourceDirectory, variantDirectory, { recursive: true, errorOnExist: true });
  if (agent === 'claude') {
    setClaudeModelInvocation(path.join(variantDirectory, 'SKILL.md'), false);
  } else if (agent === 'codex') {
    setCodexImplicitInvocation(path.join(variantDirectory, 'agents', 'openai.yaml'), false);
  }
  return {
    directory: variantDirectory,
    installedHash: computeDirectoryHash(variantDirectory),
    cleanup: () => removeIfPresent(temporaryRoot)
  };
}

function installOne({
  preparedSourceDirectory,
  destination,
  version,
  sourceHash,
  installedHash,
  activation,
  agent,
  replacing
}) {
  const parent = path.dirname(destination);
  fs.mkdirSync(parent, { recursive: true });
  const temporary = createUniqueSibling(destination, 'tmp');
  const backup = createUniqueSibling(destination, 'backup');
  let backupCreated = false;
  try {
    fs.cpSync(preparedSourceDirectory, temporary, {
      recursive: true,
      errorOnExist: true,
      preserveTimestamps: true
    });
    const copiedHash = computeDirectoryHash(temporary);
    if (copiedHash !== installedHash) {
      throw new Error('A copia temporaria da skill nao corresponde a variante preparada.');
    }
    const marker = {
      schemaVersion: 2,
      skill: SKILL_NAME,
      package: PACKAGE_NAME,
      version,
      sourceHash,
      installedHash,
      activation,
      agent,
      installedAt: new Date().toISOString()
    };
    fs.writeFileSync(
      path.join(temporary, INSTALL_MARKER),
      `${JSON.stringify(marker, null, 2)}\n`,
      'utf8'
    );
    if (replacing) {
      fs.renameSync(destination, backup);
      backupCreated = true;
    }
    fs.renameSync(temporary, destination);
    if (backupCreated) removeIfPresent(backup);
  } catch (error) {
    removeIfPresent(temporary);
    if (backupCreated && !lstatIfPresent(destination) && lstatIfPresent(backup)) {
      fs.renameSync(backup, destination);
    }
    throw error;
  } finally {
    removeIfPresent(temporary);
    if (backupCreated && lstatIfPresent(backup) && lstatIfPresent(destination)) {
      removeIfPresent(backup);
    }
  }
}

export function inspectTarget(target) {
  const ownership = inspectOwnership(target.destination);
  return {
    ...target,
    installed: ownership.exists,
    owned: ownership.owned,
    valid: ownership.valid,
    managed: ownership.managed,
    modified: ownership.modified,
    symlink: ownership.isSymlink,
    version: ownership.marker?.version ?? null,
    installedAt: ownership.marker?.installedAt ?? null,
    sourceHash: ownership.marker?.sourceHash ?? null,
    installedHash: ownership.expectedInstalledHash,
    currentHash: ownership.currentHash,
    activation: ownership.activation
  };
}

function planInstallAction(ownership, sourceHash, installedHash, activation, force) {
  if (!ownership.exists) return 'install';
  if (ownership.isSymlink) {
    throw makeError(
      'ESYMLINK',
      'Recusando substituir um link simbolico. Remova ou ajuste o link manualmente.'
    );
  }
  if (!ownership.owned) {
    throw makeError('ENOTOWNED', `O destino existente nao pertence a ${SKILL_NAME}.`);
  }
  if (
    ownership.managed
    && !ownership.modified
    && ownership.currentHash === installedHash
    && ownership.marker?.sourceHash === sourceHash
    && ownership.activation === activation
  ) return 'already-current';
  if (ownership.managed && !ownership.modified) return 'update';
  if (!force) {
    if (ownership.managed && ownership.modified) {
      throw makeError(
        'EMODIFIED',
        'A instalacao possui alteracoes locais. Preserve-as ou use --force para substitui-las.'
      );
    }
    throw makeError(
      'EUNMANAGED',
      'A skill parece ter sido instalada manualmente. Use --force para adota-la e substituir seu conteudo.'
    );
  }
  return 'update';
}

export function installSkill({
  agent = 'both',
  scope = 'workspace',
  workspaceDir,
  projectDir,
  homeDir = os.homedir(),
  activation = 'selective',
  force = false,
  dryRun = false,
  sourceDirectory = SKILL_SOURCE
} = {}) {
  validateBundledSkill(sourceDirectory);
  const normalizedActivation = normalizeActivation(activation);
  const targets = resolveTargets({ agent, scope, workspaceDir, projectDir, homeDir });
  const version = getPackageVersion();
  const sourceHash = computeDirectoryHash(sourceDirectory);
  const variants = [];
  try {
    const preflight = targets.map((target) => {
      const variant = prepareVariant(sourceDirectory, target.agent, normalizedActivation);
      variants.push(variant);
      const ownership = inspectOwnership(target.destination);
      return {
        target,
        ownership,
        variant,
        action: planInstallAction(
          ownership,
          sourceHash,
          variant.installedHash,
          normalizedActivation,
          force
        )
      };
    });

    if (!dryRun) {
      for (const item of preflight) {
        if (item.action === 'already-current') continue;
        installOne({
          preparedSourceDirectory: item.variant.directory,
          destination: item.target.destination,
          version,
          sourceHash,
          installedHash: item.variant.installedHash,
          activation: normalizedActivation,
          agent: item.target.agent,
          replacing: item.ownership.exists
        });
      }
    }

    return preflight.map(({ target, action, variant }) => ({
      ...target,
      action: dryRun && action !== 'already-current'
        ? `would-${action}`
        : (action === 'install' ? 'installed' : action === 'update' ? 'updated' : action),
      version,
      sourceHash,
      installedHash: variant.installedHash,
      activation: normalizedActivation
    }));
  } finally {
    for (const variant of variants) variant.cleanup();
  }
}

export function uninstallSkill({
  agent = 'both',
  scope = 'workspace',
  workspaceDir,
  projectDir,
  homeDir = os.homedir(),
  force = false,
  dryRun = false
} = {}) {
  const targets = resolveTargets({ agent, scope, workspaceDir, projectDir, homeDir });
  const preflight = targets.map((target) => ({
    target,
    ownership: inspectOwnership(target.destination)
  }));
  for (const { target, ownership } of preflight) {
    if (!ownership.exists) continue;
    if (ownership.isSymlink) {
      throw makeError(
        'ESYMLINK',
        `Recusando remover o link simbolico em ${target.destination}. Remova-o manualmente.`
      );
    }
    if (!ownership.owned) {
      throw makeError(
        'ENOTOWNED',
        `Recusando remover ${target.destination}: o diretorio nao pertence a ${SKILL_NAME}.`
      );
    }
    if (!force && !ownership.managed) {
      throw makeError(
        'EUNMANAGED',
        `A instalacao em ${target.destination} nao foi criada por este pacote. Use --force para remove-la.`
      );
    }
    if (!force && ownership.modified) {
      throw makeError(
        'EMODIFIED',
        `A instalacao em ${target.destination} possui alteracoes locais. Use --force para remove-la.`
      );
    }
  }
  const results = [];
  for (const { target, ownership } of preflight) {
    if (!ownership.exists) {
      results.push({ ...target, action: 'not-installed' });
      continue;
    }
    if (!dryRun) fs.rmSync(target.destination, { recursive: true, force: true });
    results.push({ ...target, action: dryRun ? 'would-uninstall' : 'uninstalled' });
  }
  return results;
}

export function getStatus(options = {}) {
  return resolveTargets(options).map(inspectTarget);
}

function probeCommand(command, args = ['--version']) {
  const result = spawnSync(command, args, {
    encoding: 'utf8',
    timeout: 5000,
    windowsHide: true
  });
  if (result.error?.code === 'ENOENT') return null;
  const output = `${result.stdout ?? ''}\n${result.stderr ?? ''}`.trim();
  return {
    command,
    available: result.status === 0,
    version: output.split(/\r?\n/).find(Boolean) ?? null,
    exitCode: result.status
  };
}

export function runDoctor() {
  const pythonCandidates = process.platform === 'win32'
    ? [['py', ['-3', '--version']], ['python', ['--version']], ['python3', ['--version']]]
    : [['python3', ['--version']], ['python', ['--version']]];
  let python = null;
  for (const [command, args] of pythonCandidates) {
    python = probeCommand(command, args);
    if (python) break;
  }
  return {
    package: PACKAGE_NAME,
    packageVersion: getPackageVersion(),
    node: process.version,
    bundledSkillValid: validateBundledSkill(),
    bundledSkillHash: computeDirectoryHash(SKILL_SOURCE),
    activationModes: [...ACTIVATION_MODES],
    defaultActivation: 'selective',
    python,
    claude: probeCommand('claude'),
    codex: probeCommand('codex')
  };
}
