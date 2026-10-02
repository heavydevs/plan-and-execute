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
  isMissingCommand,
  probeCommand,
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
  'lifecyclectl_concise.py'
);

const EXECUTION_PROVIDERS = Object.freeze([
  'claude', 'codex', 'antigravity', 'gemini', 'qwen', 'kimi', 'trae'
]);
const PROFILE_PROVIDERS = Object.freeze(['muse', 'glm', 'deepseek']);
const RESUME_PROVIDERS = Object.freeze([...EXECUTION_PROVIDERS, ...PROFILE_PROVIDERS]);
const MODELS_ACTIONS = Object.freeze(['status', 'show', 'refresh', 'diff']);
const OPTIONAL_PROVIDER_COMMANDS =Object.freeze({
  antigravity: 'agy',
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
  claude, codex, antigravity, gemini, qwen, kimi, trae

A instalacao padrao da skill e o tutorial rapido continuam restritos a Claude Code e Codex.
Antigravity (agy), Qwen, Kimi e Trae sao backends opcionais de execucao; gemini e legado
(Gemini CLI descontinuada em 2026-06-18).

Uso da implementacao:
  pae current [opcoes]              Mostrar a implementacao ativa
  pae resume [opcoes]               Continuar de onde parou
  pae cancel [opcoes]               Cancelar e apagar o plano ativo
  pae reset [opcoes]                Apagar todos os planos reconhecidos no workspace

Configuracao de roteamento (sem chamadas de geracao):
  pae configure                     Perguntas separadas; salva no perfil do usuario
  pae configure --plan <diretorio>   Substituicoes para um plano existente
  pae configure --config <arquivo>   Destino explicito
  pae configure --show [--json]      Mostrar configuracao sem gravar
  pae configure --profile <glm|deepseek> [--harness <claude|codex>]
                                    Salvar perfil de provedor (somente nomes de variaveis de ambiente)

Catalogo de modelos (sem chamadas de geracao):
  pae models status [--provider <nome>] [--plan <diretorio>]
  pae models show [--provider <nome>]
  pae models refresh --provider <nome> | --plan <diretorio>
  pae models diff --plan <diretorio>

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
  --provider <nome>                 claude|codex|antigravity|gemini|qwen|kimi|trae|muse|glm|deepseek
  --harness <nome>                  Com configure --profile: claude|codex
  --cache-dir <caminho>             Com models: cache do catalogo
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
  pae resume --provider antigravity --once
  pae resume --provider muse --once
  pae models refresh --plan .ai-work/<plano>
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
    noCleanup: false, allPlans: false, configPath: null, planPath: null, showConfig: false,
    profile: null, harness: null, cacheDir: null, action: null
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
      if (command === 'models' && !options.action && MODELS_ACTIONS.includes(arg)) {
        options.action = arg; continue;
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
      case '--config': options.configPath = requireValue(args, index, arg); index += 1; break;
      case '--plan': options.planPath = requireValue(args, index, arg); index += 1; break;
      case '--show': options.showConfig = true; break;
      case '--profile': options.profile = requireValue(args, index, arg).toLowerCase(); index += 1; break;
      case '--harness': options.harness = requireValue(args, index, arg).toLowerCase(); index += 1; break;
      case '--cache-dir': options.cacheDir = requireValue(args, index, arg); index += 1; break;
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
  if (options.provider && !RESUME_PROVIDERS.includes(options.provider)) {
    throw new Error(`Provedor invalido: ${options.provider}. Use ${RESUME_PROVIDERS.join(', ')}.`);
  }
  if (command === 'models' && !options.action) options.action = 'status';
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

function executionDoctorReport(options) {
  const report = runDoctor();
  for (const [provider, command] of Object.entries(OPTIONAL_PROVIDER_COMMANDS)) {
    report[provider] = probeCommand(command);
  }
  report.executionProviders = [...EXECUTION_PROVIDERS];
  report.defaultProviderOrder = ['claude', 'codex'];
  report.standardInstallTargets = ['claude', 'codex'];
  report.routingProfiles = routingProfilesReport(options);
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
  console.log(`Antigravity CLI agy (opcional): ${report.antigravity?.version ?? 'nao encontrado'}`);
  console.log(`Gemini CLI (legado): ${report.gemini?.version ?? 'nao encontrado'}`);
  console.log(`Qwen Code (opcional): ${report.qwen?.version ?? 'nao encontrado'}`);
  console.log(`Kimi Code CLI (opcional): ${report.kimi?.version ?? 'nao encontrado'}`);
  console.log(`Trae Agent (opcional): ${report.trae?.version ?? 'nao encontrado'}`);
  console.log(`Ordem padrao: ${report.defaultProviderOrder.join(' -> ')}`);
  for (const [name, entry] of Object.entries(report.routingProfiles.providers)) {
    const env = [entry.base_url_env && `${entry.base_url_env}=${entry.base_url_set ? 'definida' : 'ausente'}`,
      entry.token_env && `${entry.token_env}=${entry.token_set ? 'definida' : 'ausente'}`].filter(Boolean).join(', ');
    console.log(`Perfil ${name} (${entry.harness}): CLI ${entry.command_found ? 'encontrada' : 'nao encontrada'}${env ? `; ${env}` : ''}`);
  }
}

function pythonCandidates(scriptArgs, script = lifecycleScript) {
  if (process.platform === 'win32') return [
    ['py', ['-3', script, ...scriptArgs]],
    ['python', [script, ...scriptArgs]],
    ['python3', [script, ...scriptArgs]]
  ];
  return [['python3', [script, ...scriptArgs]], ['python', [script, ...scriptArgs]]];
}

function runLifecycle(scriptArgs, options, { stream = false, script = lifecycleScript } = {}) {
  for (const [command, args] of pythonCandidates(scriptArgs, script)) {
    const result = spawnSync(command, args, {
      cwd: path.resolve(options.workspaceDir),
      encoding: stream ? undefined : 'utf8',
      stdio: stream ? 'inherit' : 'pipe',
      windowsHide: true,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
    });
    if (isMissingCommand(result)) continue;
    if (!stream) {
      if (result.stdout) process.stdout.write(result.stdout);
      if (result.stderr) process.stderr.write(result.stderr);
    }
    return result.status ?? 1;
  }
  throw new Error('Python 3 nao foi encontrado. Instale Python 3.10+ para controlar a implementacao.');
}

const scriptsDir = path.join(packageRoot, 'skill', 'plan-and-execute', 'scripts');
const configureScript = path.join(scriptsDir, 'configure.py');
const catalogScript = path.join(scriptsDir, 'model_catalogctl.py');

function capturePython(scriptArgs, options, script) {
  for (const [command, args] of pythonCandidates(scriptArgs, script)) {
    const result = spawnSync(command, args, {
      cwd: path.resolve(options.workspaceDir),
      encoding: 'utf8',
      windowsHide: true,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1', PYTHONIOENCODING: 'utf-8' }
    });
    if (isMissingCommand(result)) continue;
    if (result.stderr) process.stderr.write(result.stderr);
    return { status: result.status ?? 1, stdout: result.stdout ?? '' };
  }
  throw new Error('Python 3 nao foi encontrado. Instale Python 3.10+ para controlar a implementacao.');
}

function routingProfilesReport(options) {
  const args = ['--doctor', '--json'];
  if (options.configPath) args.push('--config', path.resolve(options.workspaceDir, options.configPath));
  try {
    const result = capturePython(args, options, configureScript);
    if (result.status === 0) return JSON.parse(result.stdout);
  } catch { /* the doctor stays usable without Python or with an unreadable config */ }
  return { version: 1, config_path: null, configured: [], providers: {}, error: 'unavailable' };
}

function modelsCommand(options) {
  const { action } = options;
  const plan = options.planPath ? path.resolve(options.workspaceDir, options.planPath) : null;
  const cache = options.cacheDir ? ['--cache-dir', path.resolve(options.workspaceDir, options.cacheDir)] : [];
  const call = (args) => capturePython([...args, ...cache], options, catalogScript);
  if (action === 'refresh') {
    if (!plan && !options.provider) throw new Error('models refresh exige --provider ou --plan.');
    const results = {};
    if (options.provider) {
      results.provider = call(['refresh', '--provider', options.provider, '--json']);
      if (results.provider.status !== 0) return results.provider.status;
    }
    if (plan) {
      results.plan = call(['refresh', '--plan', plan, '--json']);
      if (results.plan.status !== 0) return results.plan.status;
    }
    const parsed = Object.fromEntries(Object.entries(results).map(([key, value]) => [key, JSON.parse(value.stdout)]));
    if (options.json) {
      console.log(JSON.stringify(results.provider && results.plan ? parsed : (parsed.plan ?? parsed.provider), null, 2));
      return 0;
    }
    if (parsed.provider) {
      console.log(`Catalogo ${parsed.provider.provider}: ${parsed.provider.origin}${parsed.provider.catalog_version ? ` ${parsed.provider.catalog_version}` : ''}`);
    }
    if (parsed.plan) {
      const state = parsed.plan.old_digest === parsed.plan.new_digest ? 'inalterado' : 'alterado';
      console.log(`Digest: ${parsed.plan.old_digest ?? 'nenhum'} -> ${parsed.plan.new_digest} (${state})`);
      console.log(`Tarefas reavaliadas: ${(parsed.plan.rebased ?? []).join(', ') || 'nenhuma'}`);
    }
    return 0;
  }
  const args = [action];
  if (options.provider && action !== 'diff') args.push('--provider', options.provider);
  if (plan && action !== 'show') args.push('--plan', plan);
  if (options.json) args.push('--json');
  const result = call(args);
  if (result.stdout) process.stdout.write(result.stdout);
  return result.status;
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
      case 'doctor': printDoctor(executionDoctorReport(options), options.json); break;
      case 'configure': {
        const args = [];
        if (options.configPath) args.push('--config', path.resolve(options.workspaceDir, options.configPath));
        if (options.planPath) args.push('--plan', path.resolve(options.workspaceDir, options.planPath));
        if (options.showConfig) args.push('--show');
        if (options.profile) args.push('--profile', options.profile);
        if (options.harness) args.push('--harness', options.harness);
        if (options.json) args.push('--json');
        if (options.dryRun) args.push('--dry-run');
        process.exitCode = runLifecycle(args, options, {
          stream: !options.showConfig && !options.profile,
          script: configureScript
        });
        break;
      }
      case 'models': process.exitCode = modelsCommand(options); break;
      case 'current': process.exitCode = runLifecycle(lifecycleArguments('current', options), options); break;
      case 'resume': process.exitCode = runLifecycle(lifecycleArguments('resume', options), options, { stream: true }); break;
      case 'cancel': process.exitCode = runLifecycle(lifecycleArguments('cancel', options), options); break;
      case 'reset': process.exitCode = runLifecycle(lifecycleArguments('reset', options), options); break;
      default: fail(`Comando desconhecido: ${command}\n\n${HELP}`, 2);
    }
  } catch (error) { fail(error.message, exitCodeForError(error)); }
}

await main();
