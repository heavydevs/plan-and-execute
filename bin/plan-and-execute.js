#!/usr/bin/env node

import {
  getPackageVersion,
  getStatus,
  installSkill,
  resolveTargets,
  runDoctor,
  uninstallSkill
} from '../lib/installer.js';

const HELP = `plan-and-execute (alias: pae) - instala a skill no Claude Code e/ou Codex

Uso:
  plan-and-execute install [claude|codex|both] [opcoes]
  plan-and-execute status [claude|codex|both] [opcoes]
  plan-and-execute paths [claude|codex|both] [opcoes]
  plan-and-execute uninstall [claude|codex|both] [opcoes]
  plan-and-execute doctor [--json]

Opcoes:
  --agent <claude|codex|both>  Destino. Padrao: both
  --scope <workspace|user>     Projeto atual ou perfil do usuario. Padrao: workspace
  --cwd <caminho>              Raiz do workspace. Padrao: diretorio atual
  --workspace <caminho>        Alias de --cwd
  --local                      Alias de --scope workspace
  --global                     Alias de --scope user
  --force                      Substituir/remover uma copia gerenciada que foi modificada
  --dry-run                    Mostrar operacoes sem alterar arquivos
  --json                       Gerar saida JSON
  -h, --help                   Mostrar ajuda
  -v, --version                Mostrar versao

Exemplos:
  npx @luizcgvrj/plan-and-execute install both --global
  npx @luizcgvrj/plan-and-execute install claude --local
  pae install codex --cwd /caminho/do/projeto
  pae status both --global
  pae uninstall claude --local
`;

function fail(message, code = 1) {
  console.error(`Erro: ${message}`);
  process.exitCode = code;
}

function requireValue(args, index, option) {
  const value = args[index + 1];
  if (!value || value.startsWith('-')) {
    throw new Error(`A opcao ${option} exige um valor.`);
  }
  return value;
}

export function parseArguments(argv) {
  const args = [...argv];
  let command = 'help';

  if (args.length > 0 && !args[0].startsWith('-')) {
    command = args.shift();
  }

  const options = {
    agent: 'both',
    scope: 'workspace',
    workspaceDir: process.cwd(),
    force: false,
    dryRun: false,
    json: false
  };

  let showHelp = false;
  let showVersion = false;
  let positionalAgentUsed = false;

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];

    if (!arg.startsWith('-')) {
      if (!positionalAgentUsed && ['claude', 'codex', 'both'].includes(arg)) {
        options.agent = arg;
        positionalAgentUsed = true;
        continue;
      }
      throw new Error(`Argumento desconhecido: ${arg}`);
    }

    switch (arg) {
      case '--agent':
      case '--target':
      case '-a':
        options.agent = requireValue(args, index, arg);
        index += 1;
        break;
      case '--scope':
      case '-s':
        options.scope = requireValue(args, index, arg);
        index += 1;
        break;
      case '--workspace':
      case '--project-dir':
      case '--cwd':
      case '-C':
        options.workspaceDir = requireValue(args, index, arg);
        index += 1;
        break;
      case '--global':
      case '-g':
        options.scope = 'user';
        break;
      case '--local':
        options.scope = 'workspace';
        break;
      case '--claude':
        options.agent = 'claude';
        break;
      case '--codex':
        options.agent = 'codex';
        break;
      case '--both':
        options.agent = 'both';
        break;
      case '--force':
      case '-f':
        options.force = true;
        break;
      case '--dry-run':
        options.dryRun = true;
        break;
      case '--json':
        options.json = true;
        break;
      case '-h':
      case '--help':
        showHelp = true;
        break;
      case '-v':
      case '--version':
        showVersion = true;
        break;
      default:
        throw new Error(`Opcao desconhecida: ${arg}`);
    }
  }

  return { command, options, showHelp, showVersion };
}

function printResults(results, json) {
  if (json) {
    console.log(JSON.stringify(results, null, 2));
    return;
  }

  for (const result of results) {
    if ('installed' in result) {
      let status = 'nao instalada';
      if (result.installed) {
        if (result.symlink) {
          status = 'link simbolico nao gerenciado';
        } else if (!result.valid) {
          status = 'diretorio presente, mas SKILL.md invalido';
        } else if (result.modified) {
          status = `instalada e modificada${result.version ? ` (v${result.version})` : ''}`;
        } else if (result.managed) {
          status = `instalada${result.version ? ` (v${result.version})` : ''}`;
        } else {
          status = 'instalada manualmente';
        }
      }
      console.log(`${result.agent}/${result.scope}: ${status} - ${result.destination}`);
    } else {
      console.log(`${result.agent}/${result.scope}: ${result.action} - ${result.destination}`);
    }
  }
}

function printDoctor(report, json) {
  if (json) {
    console.log(JSON.stringify(report, null, 2));
    return;
  }
  console.log(`Pacote: ${report.package} v${report.packageVersion}`);
  console.log(`Node: ${report.node}`);
  console.log(`Skill embutida: ${report.bundledSkillValid ? 'valida' : 'invalida'}`);
  console.log(`Python: ${report.python?.version ?? 'nao encontrado (necessario para executar a skill)'}`);
  console.log(`Claude CLI: ${report.claude?.version ?? 'nao encontrado'}`);
  console.log(`Codex CLI: ${report.codex?.version ?? 'nao encontrado'}`);
}

function exitCodeForError(error) {
  if (['EEXIST', 'EMODIFIED', 'EUNMANAGED', 'ENOTOWNED', 'ESYMLINK'].includes(error?.code)) {
    return 3;
  }
  return 1;
}

async function main() {
  let parsed;
  try {
    parsed = parseArguments(process.argv.slice(2));
  } catch (error) {
    fail(error.message, 2);
    return;
  }

  const { command, options, showHelp, showVersion } = parsed;

  if (showVersion) {
    console.log(getPackageVersion());
    return;
  }
  if (showHelp || command === 'help') {
    console.log(HELP);
    return;
  }

  try {
    switch (command) {
      case 'install':
        printResults(installSkill(options), options.json);
        break;
      case 'status':
        printResults(getStatus(options), options.json);
        break;
      case 'paths':
        printResults(resolveTargets(options).map((target) => ({ ...target, action: 'target' })), options.json);
        break;
      case 'uninstall':
        printResults(uninstallSkill(options), options.json);
        break;
      case 'doctor':
        printDoctor(runDoctor(), options.json);
        break;
      default:
        fail(`Comando desconhecido: ${command}\n\n${HELP}`, 2);
    }
  } catch (error) {
    fail(error.message, exitCodeForError(error));
  }
}

await main();
