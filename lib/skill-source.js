/** Deterministic, self-contained companion payload built from the canonical runtime.
 * Runtime source stays in plan-and-execute; no second implementation is maintained.
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const SKILLS = Object.freeze(['plan-and-execute', 'validate-or-fix']);

export function normalizeSkill(value = SKILLS[0], allowAll = false) {
  if (!SKILLS.includes(value) && !(allowAll && value === 'all')) {
    throw new Error(`Skill invalida: ${value}. Use ${SKILLS.join(', ')}${allowAll ? ' ou all' : ''}.`);
  }
  return value;
}

export function skillSource(name) {
  return path.join(root, 'skill', normalizeSkill(name));
}

export function stageSkillSource(name, sourceDirectory = skillSource(name)) {
  normalizeSkill(name);
  const stat = fs.lstatSync(sourceDirectory);
  if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error('Fonte da skill deve ser um diretorio regular.');
  if (name === 'plan-and-execute') return { directory: sourceDirectory, cleanup() {} };
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'pae-companion-'));
  const destination = path.join(temporary, name);
  const cleanup = () => fs.rmSync(temporary, { recursive: true, force: true });
  try {
    fs.cpSync(sourceDirectory, destination, { recursive: true, errorOnExist: true });
    // A complete, already-built package can be reinstalled without a sibling.
    if (fs.existsSync(path.join(destination, '_runtime'))) {
      return { directory: destination, cleanup };
    }
    const canonical = skillSource('plan-and-execute');
    const files = fs.readdirSync(path.join(canonical, 'scripts'))
      .filter((name) => name.endsWith('.py') && name !== 'self_test.py' && !name.endsWith('_self_test.py'))
      .map((name) => path.join('scripts', name));
    files.push(path.join('assets', 'service-map-template.md'));
    files.push(...fs.readdirSync(path.join(canonical, 'references'))
      .filter((name) => name.endsWith('.json')).map((name) => path.join('references', name)));
    const hashes = {};
    for (const relative of files.sort()) {
      const source = path.join(canonical, relative);
      if (!fs.lstatSync(source).isFile() || fs.lstatSync(source).isSymbolicLink()) {
        throw new Error(`Runtime nao regular: ${relative}`);
      }
      const target = path.join(destination, '_runtime', relative);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.copyFileSync(source, target);
      hashes[relative.split(path.sep).join('/')] = crypto.createHash('sha256').update(fs.readFileSync(source)).digest('hex');
    }
    fs.writeFileSync(path.join(destination, '_runtime', 'PROVENANCE.json'),
      `${JSON.stringify({ schema_version: 1, source: 'skill/plan-and-execute', files: hashes }, null, 2)}\n`);
    return { directory: destination, cleanup };
  } catch (error) {
    cleanup();
    throw error;
  }
}
