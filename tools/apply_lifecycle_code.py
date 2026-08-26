#!/usr/bin/env python3
"""One-time source transformation for the resumable lifecycle release."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, content: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(relative: str, old: str, new: str, *, optional: bool = False) -> None:
    text = read(relative)
    if old not in text:
        if optional or new in text:
            return
        raise SystemExit(f"Anchor not found in {relative}: {old[:100]!r}")
    write(relative, text.replace(old, new, 1))


def append_once(relative: str, marker: str, content: str) -> None:
    text = read(relative)
    if marker not in text:
        if not text.endswith("\n"):
            text += "\n"
        write(relative, text + content)


# Package metadata.
package_path = ROOT / "package.json"
package = json.loads(package_path.read_text(encoding="utf-8"))
package["version"] = "0.5.0"
package["description"] = (
    "Install the plan-and-execute skill for guided request capture, adaptive evidence-backed study, "
    "traceable recursive planning, resumable execution, guarded cancellation, and isolated Claude Code or Codex workers."
)
keywords = list(package.get("keywords", []))
for keyword in ("resume", "lifecycle"):
    if keyword not in keywords:
        keywords.append(keyword)
package["keywords"] = keywords
package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lock_path = ROOT / "package-lock.json"
lock = json.loads(lock_path.read_text(encoding="utf-8"))
lock["version"] = "0.5.0"
if "" in lock.get("packages", {}):
    lock["packages"][""]["version"] = "0.5.0"
lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Installer validation includes lifecycle resources.
installer_path = ROOT / "lib/installer.js"
installer = installer_path.read_text(encoding="utf-8")
start = installer.index("  const required = [")
end = installer.index("  ];", start)
block = installer[start:end]
lines = block.splitlines()
seen: set[str] = set()
normalized: list[str] = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith("path.join("):
        key = stripped.rstrip(",")
        if key in seen:
            continue
        seen.add(key)
        line = line.rstrip()
        if not line.endswith(","):
            line += ","
    normalized.append(line)
for key in (
    "path.join('scripts', 'lifecyclectl.py')",
    "path.join('scripts', 'lifecycle_self_test.py')",
    "path.join('references', 'LIFECYCLE.md')",
):
    if key not in seen:
        normalized.append("    " + key + ",")
new_block = "\n".join(normalized) + "\n"
installer_path.write_text(installer[:start] + new_block + installer[end:], encoding="utf-8")

# The strict runner activates, leases, and recovers before its existing loop.
runner_path = ROOT / "skill/plan-and-execute/scripts/run_isolated.py"
runner = runner_path.read_text(encoding="utf-8")
if "import lifecyclectl  # noqa: E402" not in runner:
    runner = runner.replace("import shlex\nimport shutil\n", "import shlex\nimport shutil\nimport signal\n", 1)
    runner = runner.replace(
        "import planctl  # noqa: E402\n",
        "import planctl  # noqa: E402\nimport lifecyclectl  # noqa: E402\n",
        1,
    )
    runner = runner.replace(
        "def run_plan(args: argparse.Namespace) -> int:\n",
        "def _run_plan(args: argparse.Namespace) -> int:\n",
        1,
    )
    cleanup_old = '''        if should_cleanup:\n            planctl.cleanup_plan(plan_dir, manifest)\n            print("\\n[cleanup] Planning artifacts deleted; implementation files were preserved.")\n        else:\n            print(f"\\n[plan] Planning artifacts retained at {plan_dir}")\n        return 0\n'''
    cleanup_new = '''        # Terminal work must never block the next default invocation, even when\n        # the completed plan is intentionally retained for inspection.\n        lifecyclectl.clear_active(plan_dir)\n        if should_cleanup:\n            planctl.cleanup_plan(plan_dir, manifest)\n            print("\\n[cleanup] Planning artifacts deleted; implementation files were preserved.")\n        else:\n            print(f"\\n[plan] Planning artifacts retained at {plan_dir}")\n        return 0\n'''
    if cleanup_old not in runner:
        raise SystemExit("run_isolated cleanup anchor not found")
    runner = runner.replace(cleanup_old, cleanup_new, 1)
    parser_anchor = "\ndef build_parser() -> argparse.ArgumentParser:\n"
    wrapper = r'''

def run_plan(args: argparse.Namespace) -> int:
    """Run or resume a plan under an atomic lease."""
    plan_dir, _ = planctl.load_plan(args.plan)
    lifecyclectl.activate_plan(plan_dir)
    with lifecyclectl.runner_lease(plan_dir):
        recovered = lifecyclectl.recover_interrupted_tasks(
            plan_dir,
            allow_live_lease=True,
        )
        if recovered:
            print(
                f"[resume] Recovered {recovered} interrupted task(s); "
                "partial repository changes were preserved.",
                flush=True,
            )
        return _run_plan(args)


def _interrupt_on_signal(signum: int, frame: object) -> None:
    del signum, frame
    raise KeyboardInterrupt


def install_signal_handlers() -> None:
    if hasattr(signal, "SIGTERM"):
        try:
            signal.signal(signal.SIGTERM, _interrupt_on_signal)
        except (OSError, ValueError):
            pass
'''
    if parser_anchor not in runner:
        raise SystemExit("run_isolated parser anchor not found")
    runner = runner.replace(parser_anchor, wrapper + parser_anchor, 1)
    runner = runner.replace(
        "def main() -> int:\n    args = build_parser().parse_args()\n",
        "def main() -> int:\n    install_signal_handlers()\n    args = build_parser().parse_args()\n",
        1,
    )
runner_path.write_text(runner, encoding="utf-8")

# Direct planctl cleanup also clears a matching active pointer.
planctl_path = ROOT / "skill/plan-and-execute/scripts/planctl.py"
planctl = planctl_path.read_text(encoding="utf-8")
cleanup_start = planctl.find("def cleanup_plan(")
cleanup_end = planctl.find("\ndef ", cleanup_start + 5)
segment = planctl[cleanup_start:cleanup_end]
if ".active-plan.json" not in segment:
    anchor = "    shutil.rmtree(plan_dir)\n"
    addition = '''    # Direct guarded cleanup must not leave a pointer to a deleted plan.\n    active_pointer = Path(manifest["repo_root"]) / manifest["work_root"] / ".active-plan.json"\n    if active_pointer.is_file() and not active_pointer.is_symlink():\n        try:\n            active_record = read_json(active_pointer)\n        except PlanError:\n            active_record = None\n        if isinstance(active_record, dict) and active_record.get("plan_id") == manifest.get("plan_id"):\n            try:\n                active_pointer.unlink()\n            except FileNotFoundError:\n                pass\n    shutil.rmtree(plan_dir)\n'''
    if anchor not in segment:
        raise SystemExit("planctl cleanup anchor not found")
    segment = segment.replace(anchor, addition, 1)
    planctl = planctl[:cleanup_start] + segment + planctl[cleanup_end:]
planctl_path.write_text(planctl, encoding="utf-8")

# CLI lifecycle commands. This file is replaced intentionally to keep argument handling coherent.
write("bin/plan-and-execute.js", r'''#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import {
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

const HELP = `plan-and-execute (alias: pae) - instala e controla a skill no Claude Code e/ou Codex

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
  --provider <claude|codex>          Sobrescrever provedor na retomada
  --once                            Executar no maximo um TODO
  --no-wait                         Nao aguardar automaticamente limites de uso
  --no-cleanup                      Manter o plano concluido para inspecao
  --all                             Com cancel, remover todos os planos reconhecidos

Opcoes de instalacao:
  --agent <claude|codex|both>        Destino. Padrao: both
  --scope <workspace|user>           Projeto atual ou perfil do usuario. Padrao: workspace
  --local                            Alias de --scope workspace
  --global                           Alias de --scope user
  --dry-run                          Mostrar operacoes sem alterar arquivos

Exemplos:
  pae current
  pae resume
  pae resume --provider codex --once
  pae cancel
  pae reset --force
  npx @luizcgvrj/plan-and-execute install both --global
  pae install codex --cwd /caminho/do/projeto
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
  if (args.length > 0 && !args[0].startsWith('-')) command = args.shift();
  const options = {
    agent: 'both', scope: 'workspace', workspaceDir: process.cwd(), force: false,
    dryRun: false, json: false, provider: null, once: false, noWait: false,
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
      case '--global': case '-g': options.scope = 'user'; break;
      case '--local': options.scope = 'workspace'; break;
      case '--claude': options.agent = 'claude'; break;
      case '--codex': options.agent = 'codex'; break;
      case '--both': options.agent = 'both'; break;
      case '--provider': options.provider = requireValue(args, index, arg); index += 1; break;
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
  if (options.provider && !['claude', 'codex'].includes(options.provider)) {
    throw new Error(`Provedor invalido: ${options.provider}. Use claude ou codex.`);
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
      console.log(`${result.agent}/${result.scope}: ${status} - ${result.destination}`);
    } else console.log(`${result.agent}/${result.scope}: ${result.action} - ${result.destination}`);
  }
}

function printDoctor(report, json) {
  if (json) { console.log(JSON.stringify(report, null, 2)); return; }
  console.log(`Pacote: ${report.package} v${report.packageVersion}`);
  console.log(`Node: ${report.node}`);
  console.log(`Skill embutida: ${report.bundledSkillValid ? 'valida' : 'invalida'}`);
  console.log(`Python: ${report.python?.version ?? 'nao encontrado (necessario para executar a skill)'}`);
  console.log(`Claude CLI: ${report.claude?.version ?? 'nao encontrado'}`);
  console.log(`Codex CLI: ${report.codex?.version ?? 'nao encontrado'}`);
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
      case 'doctor': printDoctor(runDoctor(), options.json); break;
      case 'current': process.exitCode = runLifecycle(lifecycleArguments('current', options), options); break;
      case 'resume': process.exitCode = runLifecycle(lifecycleArguments('resume', options), options, { stream: true }); break;
      case 'cancel': process.exitCode = runLifecycle(lifecycleArguments('cancel', options), options); break;
      case 'reset': process.exitCode = runLifecycle(lifecycleArguments('reset', options), options); break;
      default: fail(`Comando desconhecido: ${command}\n\n${HELP}`, 2);
    }
  } catch (error) { fail(error.message, exitCodeForError(error)); }
}

await main();
''')

# Run all three Python self-test suites.
write("tools/run-skill-self-test.js", r'''#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const scriptDirectory = path.join(root, 'skill', 'plan-and-execute', 'scripts');
const testScripts = [
  path.join(scriptDirectory, 'self_test.py'),
  path.join(scriptDirectory, 'study_self_test.py'),
  path.join(scriptDirectory, 'lifecycle_self_test.py')
];
const candidates = process.platform === 'win32'
  ? [['py', ['-3']], ['python', []], ['python3', []]]
  : [['python3', []], ['python', []]];
let python = null;
for (const [command, prefix] of candidates) {
  const probe = spawnSync(command, [...prefix, '--version'], { cwd: root, encoding: 'utf8', windowsHide: true });
  if (probe.error?.code === 'ENOENT') continue;
  if (probe.status === 0) { python = [command, prefix]; break; }
}
if (!python) {
  console.error('Python 3 nao foi encontrado. Instale Python 3.10+ para executar os self-tests da skill.');
  process.exit(1);
}
for (const testScript of testScripts) {
  const [command, prefix] = python;
  const result = spawnSync(command, [...prefix, testScript], {
    cwd: root, stdio: 'inherit', windowsHide: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' }
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
''')

# Validator release and lifecycle assertions.
validator_path = ROOT / "tools/validate-skill.js"
validator = validator_path.read_text(encoding="utf-8")
validator = validator.replace("packageMetadata.version !== '0.4.0'", "packageMetadata.version !== '0.5.0'")
validator = validator.replace("Expected package version 0.4.0", "Expected package version 0.5.0")
validator = validator.replace(
    "'No arguments: create an editable request draft'",
    "'No arguments: resume an implementation or create a request'",
)
needle = "  'references/INTAKE.md'"
if "'lifecyclectl.py current'" not in validator:
    validator = validator.replace(
        needle,
        needle + ",\n  'lifecyclectl.py current',\n  'references/LIFECYCLE.md',\n  'cancel --repo-root'",
        1,
    )
if "agents/openai.yaml must mention resumable lifecycle" not in validator:
    marker = "const skill = fs.readFileSync(path.join(SKILL_SOURCE, 'SKILL.md'), 'utf8');"
    addition = """if (!metadata.toLowerCase().includes('resume')) {\n  console.error('agents/openai.yaml must mention resumable lifecycle and resume behavior.');\n  process.exit(1);\n}\n\n"""
    validator = validator.replace(marker, addition + marker, 1)
validator_path.write_text(validator, encoding="utf-8")

# Node tests cover idle lifecycle CLI and installed lifecycle resources.
cli_test = ROOT / "test/cli.test.js"
cli_text = cli_test.read_text(encoding="utf-8")
if "CLI lifecycle commands are workspace-aware" not in cli_text:
    cli_text += r'''

test('CLI lifecycle commands are workspace-aware and automation friendly', () => {
  const workspace = temporaryDirectory();
  try {
    const current = run(['current', '--cwd', workspace, '--json']);
    assert.equal(current.status, 0, current.stderr);
    const currentPayload = JSON.parse(current.stdout);
    assert.equal(currentPayload.status, 'idle');
    assert.equal(currentPayload.action, 'create_request');
    const cancel = run(['cancel', '--cwd', workspace, '--json']);
    assert.equal(cancel.status, 0, cancel.stderr);
    const cancelPayload = JSON.parse(cancel.stdout);
    assert.equal(cancelPayload.status, 'idle');
    assert.equal(cancelPayload.implementation_changes_preserved, true);
    const reset = run(['reset', '--cwd', workspace, '--json']);
    assert.equal(reset.status, 0, reset.stderr);
    assert.equal(JSON.parse(reset.stdout).status, 'idle');
  } finally {
    fs.rmSync(workspace, { recursive: true, force: true });
  }
});
'''
cli_test.write_text(cli_text, encoding="utf-8")

installer_test = ROOT / "test/installer.test.js"
installer_test_text = installer_test.read_text(encoding="utf-8")
anchor = "      assert.ok(fs.existsSync(path.join(result.destination, 'scripts', 'requestctl.py')));\n"
if "'lifecyclectl.py'" not in installer_test_text:
    installer_test_text = installer_test_text.replace(
        anchor,
        anchor
        + "      assert.ok(fs.existsSync(path.join(result.destination, 'scripts', 'lifecyclectl.py')));\n"
        + "      assert.ok(fs.existsSync(path.join(result.destination, 'references', 'LIFECYCLE.md')));\n",
        1,
    )
installer_test.write_text(installer_test_text, encoding="utf-8")

print("Lifecycle code transformation applied.")
