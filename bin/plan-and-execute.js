#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import {
  ACTIVATION_MODES,
  getPackageVersion,
  getStatus,
  installSkill,
  resolveTargets,
  runDoctor,
  uninstallSkill
} from '../lib/installer.js';

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const lifecycleScript = path.join(
  packageRoot,
  'skill',
  'plan-and-execute',
  'scripts',
  'lifecyclectl.py'
);

const EXECUTION_PROVIDERS = Object.freeze([
  'claude', 'codex', 'gemini', 'qwen', 'kimi', 'trae'
]);
const OPTIONAL_PROVIDER_COMMANDS = Object.freeze({
  gemini: 'gemini',
  qwen: 'qwen',
  kimi: 'kimi',
  trae: 'trae-cli'
});

const HELP = `plan-and-execute (alias: pae) - instala a skill no Claude Code/Codex e controla execucoes isoladas

A ativacao padrao e selective: tarefas pequenas/medias coesas ficam no agente atual;
a skill orquestra somente trabalho long-horizon que justifica plano persistente.
Use --activation explicit para impedir invocacao automatica da skill.

Provedores de execucao suportados:
  claude, codex, gemini, qwen, kimi, trae

A instalacao padrao da skill e o tutorial rapido continuam restritos a Claude Code e Codex.
Gemini, Qwen, Kimi e Trae sao backends opcionais de execucao.

Uso da implementacao:
  pae current [opcoes]              Mostrar a implementacao ativa
  pae resume [opcoes]               Continuar de onde parou
  pae cancel [opcoes]               Cancelar e apagar o plano ativo
  pae reset [opcoes]                Apagar todos os planos reconhecidos no workspace

Uso da instalacao:
  pae install [claude|codex|both] [opcoes]
  pae status [claude|codex|both] [opcoes]
  pae paths [claude|codex|both] [opcoes]
  pae uninstall [claude|codex|both] [opcoes]
  pae doctor [--json]

Opcoes gerais:
  --cwd <caminho>                   Raiz do workspace. Padrao: diretorio atual
  --workspace <caminho>             Alias de --cwd
  --json                            Gerar saida JSON quando suportado
  --force                           Forcar operacao protegida
  -h, --help                        Mostrar ajuda
  -v, --version                     Mostrar versao

Opcoes de execucao:
  --provider <nome>                 claude|codex|gemini|qwen|kimi|trae
  --once                            Executar no maximo um TODO pai
  --no-wait                         Nao aguardar automaticamente limites de uso
  --no-cleanup                      Manter o plano concluido para inspecao
  --all                             Com cancel, remover todos os planos reconhecidos

Opcoes de instalacao:
  --agent <claude|codex|both>       Destino. Padrao: both
  --scope <workspace|user>          Projeto atual ou perfil do usuario. Padrao: workspace
  --activation <selective|explicit> Auto seletivo (padrao) ou somente invocacao explicita
  --selective                       Alias de --activation selective
  --explicit                        Alias de --activation explicit
  --local                           Alias de --scope workspace
  --global                          Alias de --scope user
  --dry-run                         Mostrar operacoes sem alterar arquivos

Exemplos:
  pae current
  pae resume
  pae resume --provider codex --once
  pae resume --provider gemini --once
  pae cancel
  pae reset --force
  npx @luizcgvrj/plan-and-execute install both --global
  pae install both --activation explicit --global
  pae install codex --cwd /caminho/do/projeto
`;

function fail(message, code = 1) {
  console.error(`Erro: ${message}`);
  process.exitCode = code;
}

function requireValue(args, index, option) {
  const value = args[index + 1];
  if (!value || value.startsWith('-')) throw new Error(`A opcao ${option} exige um valor.`);
  return value;
}

export function parseArguments(argv) {
  const args = [...argv];
  let command = 'help';
  if (args.length > 0 && !args[0].startsWith('-')) command = args.shift();
  const options = {
    agent: 'both', scope: 'workspace', workspaceDir: process.cwd(), activation: 'selective',
    force: false, dryRun: false, json: false, provider: null, once: false, noWait: false,
    noCleanup: false, allPlans: false
  };
  let showHelp = false;
  let showVersion = false;
  let positionalAgentUsed = false;
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (!arg.startsWith('-')) {
      if (!positionalAgentUsed && ['claude', 'codex', 'both'].includes(arg)) {
        options.agent = arg; positionalAgentUsed = true; continue;
      }
      throw new Error(`Argumento desconhecido: ${arg}`);
    }
    switch (arg) {
      case '--agent': case '--target': case '-a':
        options.agent = requireValue(args, index, arg); index += 1; break;
      case '--scope': case '-s':
        options.scope = requireValue(args, index, arg); index += 1; break;
      case '--workspace': case '--project-dir': case '--cwd': case '-C':
        options.workspaceDir = requireValue(args, index, arg); index += 1; break;
      case '--activation':
        options.activation = requireValue(args, index, arg).toLowerCase(); index += 1; break;
      case '--selective': options.activation = 'selective'; break;
      case '--explicit': options.activation = 'explicit'; break;
      case '--global': case '-g': options.scope = 'user'; break;
      case '--local': options.scope = 'workspace'; break;
      case '--claude': options.agent = 'claude'; break;
      case '--codex': options.agent = 'codex'; break;
      case '--both': options.agent = 'both'; break;
      case '--provider': options.provider = requireValue(args, index, arg).toLowerCase(); index += 1; break;
      case '--once': options.once = true; break;
      case '--no-wait': options.noWait = true; break;
      case '--no-cleanup': options.noCleanup = true; break;
      case '--all': options.allPlans = true; break;
      case '--force': case '-f': options.force = true; break;
      case '--dry-run': options.dryRun = true; break;
      case '--json': options.json = true; break;
      case '-h': case '--help': showHelp = true; break;
      case '-v': case '--version': showVersion = true; break;
      default: throw new Error(`Opcao desconhecida: ${arg}`);
    }
  }
  if (options.provider && !EXECUTION_PROVIDERS.includes(options.provider)) {
    throw new Error(`Provedor invalido: ${options.provider}. Use ${EXECUTION_PROVIDERS.join(', ')}.`);
  }
  if (!ACTIVATION_MODES.includes(options.activation)) {
    throw new Error(`Modo de ativacao invalido: ${options.activation}. Use ${ACTIVATION_MODES.join(' ou ')}.`);
  }
  return { command, options, showHelp, showVersion };
}

function printResults(results, json) {
  if (json) { console.log(JSON.stringify(results, null, 2)); return; }
  for (const result of results) {
    if ('installed' in result) {
      let status = 'nao instalada';
      if (result.installed) {
        if (result.symlink) status = 'link simbolico nao gerenciado';
        else if (!result.valid) status = 'diretorio presente, mas SKILL.md invalido';
        else if (result.modified) status = `instalada e modificada${result.version ? ` (v${result.version})` : ''}`;
        else if (result.managed) status = `instalada${result.version ? ` (v${result.version})` : ''}`;
        else status = 'instalada manualmente';
      }
      const activation = result.activation ? `, ativacao=${result.activation}` : '';
      console.log(`${result.agent}/${result.scope}: ${status}${activation} - ${result.destination}`);
    } else {
      const activation = result.activation ? ` (${result.activation})` : '';
      console.log(`${result.agent}/${result.scope}: ${result.action}${activation} - ${result.destination}`);
    }
  }
}

function probeCommand(command, args = ['--version']) {
  const result = spawnSync(command, args, { encoding: 'utf8', timeout: 5000, windowsHide: true });
  if (result.error?.code === 'ENOENT') return null;
  const output = `${result.stdout ?? ''}\n${result.stderr ?? ''}`.trim();
  return {
    command,
    available: result.status === 0,
    version: output.split(/\r?\n/).find(Boolean) ?? null,
    exitCode: result.status
  };
}

function executionDoctorReport() {
  const report = runDoctor();
  for (const [provider, command] of Object.entries(OPTIONAL_PROVIDER_COMMANDS)) {
    report[provider] = probeCommand(command);
  }
  report.executionProviders = [...EXECUTION_PROVIDERS];
  report.defaultProviderOrder = ['claude', 'codex'];
  report.standardInstallTargets = ['claude', 'codex'];
  return report;
}

function printDoctor(report, json) {
  if (json) { console.log(JSON.stringify(report, null, 2)); return; }
  console.log(`Pacote: ${report.package} v${report.packageVersion}`);
  console.log(`Node: ${report.node}`);
  console.log(`Skill embutida: ${report.bundledSkillValid ? 'valida' : 'invalida'}`);
  console.log(`Ativacao padrao: ${report.defaultActivation}`);
  console.log(`Python: ${report.python?.version ?? 'nao encontrado (necessario para executar a skill)'}`);
  console.log(`Claude CLI: ${report.claude?.version ?? 'nao encontrado'}`);
  console.log(`Codex CLI: ${report.codex?.version ?? 'nao encontrado'}`);
  console.log(`Gemini CLI (opcional): ${report.gemini?.version ?? 'nao encontrado'}`);
  console.log(`Qwen Code (opcional): ${report.qwen?.version ?? 'nao encontrado'}`);
  console.log(`Kimi Code CLI (opcional): ${report.kimi?.version ?? 'nao encontrado'}`);
  console.log(`Trae Agent (opcional): ${report.trae?.version ?? 'nao encontrado'}`);
  console.log(`Ordem padrao: ${report.defaultProviderOrder.join(' -> ')}`);
}

function pythonCandidates(scriptArgs) {
  if (process.platform === 'win32') return [
    ['py', ['-3', lifecycleScript, ...scriptArgs]],
    ['python', [lifecycleScript, ...scriptArgs]],
    ['python3', [lifecycleScript, ...scriptArgs]]
  ];
  return [['python3', [lifecycleScript, ...scriptArgs]], ['python', [lifecycleScript, ...scriptArgs]]];
}

function runLifecycle(scriptArgs, options, { stream = false } = {}) {
  for (const [command, args] of pythonCandidates(scriptArgs)) {
    const result = spawnSync(command, args, {
      cwd: path.resolve(options.workspaceDir),
      encoding: stream ? undefined : 'utf8',
      stdio: stream ? 'inherit' : 'pipe',
      windowsHide: true,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
    });
    if (result.error?.code === 'ENOENT') continue;
    if (!stream) {
      if (result.stdout) process.stdout.write(result.stdout);
      if (result.stderr) process.stderr.write(result.stderr);
    }
    return result.status ?? 1;
  }
  throw new Error('Python 3 nao foi encontrado. Instale Python 3.10+ para controlar a implementacao.');
}

function lifecycleArguments(command, options) {
  const args = [command, '--repo-root', path.resolve(options.workspaceDir)];
  if (options.json) args.push('--json');
  if (options.force && ['cancel', 'reset'].includes(command)) args.push('--force');
  if (command === 'cancel' && options.allPlans) args.push('--all');
  if (command === 'resume') {
    if (options.provider) args.push('--provider', options.provider);
    if (options.once) args.push('--once');
    if (options.noWait) args.push('--no-wait');
    if (options.noCleanup) args.push('--no-cleanup');
  }
  return args;
}

function exitCodeForError(error) {
  if (['EEXIST', 'EMODIFIED', 'EUNMANAGED', 'ENOTOWNED', 'ESYMLINK'].includes(error?.code)) return 3;
  return 1;
}

async function main() {
  let parsed;
  try { parsed = parseArguments(process.argv.slice(2)); }
  catch (error) { fail(error.message, 2); return; }
  const { command, options, showHelp, showVersion } = parsed;
  if (showVersion) { console.log(getPackageVersion()); return; }
  if (showHelp || command === 'help') { console.log(HELP); return; }
  try {
    switch (command) {
      case 'install': printResults(installSkill(options), options.json); break;
      case 'status': printResults(getStatus(options), options.json); break;
      case 'paths': printResults(resolveTargets(options).map((target) => ({ ...target, action: 'target' })), options.json); break;
      case 'uninstall': printResults(uninstallSkill(options), options.json); break;
      case 'doctor': printDoctor(executionDoctorReport(), options.json); break;
      case 'current': process.exitCode = runLifecycle(lifecycleArguments('current', options), options); break;
      case 'resume': process.exitCode = runLifecycle(lifecycleArguments('resume', options), options, { stream: true }); break;
      case 'cancel': process.exitCode = runLifecycle(lifecycleArguments('cancel', options), options); break;
      case 'reset': process.exitCode = runLifecycle(lifecycleArguments('reset', options), options); break;
      default: fail(`Comando desconhecido: ${command}\n\n${HELP}`, 2);
    }
  } catch (error) { fail(error.message, exitCodeForError(error)); }
}

await main();
