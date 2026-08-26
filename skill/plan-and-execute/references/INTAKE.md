# Request intake and editor workflow

Use this workflow before repository study whenever the skill is invoked without inline instructions or with a request-file path.

## Contents

- [No-argument invocation](#no-argument-invocation)
- [Confirmation and continuation](#confirmation-and-continuation)
- [Invocation with a file path](#invocation-with-a-file-path)
- [Editor selection](#editor-selection)
- [Language selection](#language-selection)
- [Safety and recovery](#safety-and-recovery)
- [Command reference](#command-reference)

## No-argument invocation

From the target repository root, create a draft:

```bash
python <skill-dir>/scripts/requestctl.py create --repo-root . --json
```

The command creates:

```text
.ai-work/intake/request-YYYYMMDD-HHMMSS.md
```

The file begins with short instructions and contains sections for:

- goal;
- requirements and activities;
- constraints and non-goals;
- relevant context and links;
- tests, validation, and definition of done;
- additional notes.

The instruction text is delimited from the user-authored request. Keep these markers:

```text
<!-- plan-and-execute:request:start -->
<!-- plan-and-execute:request:end -->
```

The helper returns JSON containing the absolute path, selected language, editor information, and a localized `confirmation_label`.

After creating the draft, stop. Do not start planning while the user is still editing.

## Confirmation and continuation

Present a prominent confirmation action. Prefer native choice buttons when the host exposes them. Otherwise show exactly two short choices:

```text
Continue — I finished writing the request
Reopen the request file
```

For a Portuguese locale, use the localized label returned by the helper.

When the user confirms, validate the exact path captured at creation time:

```bash
python <skill-dir>/scripts/requestctl.py validate \
  --file ".ai-work/intake/request-YYYYMMDD-HHMMSS.md" \
  --json
```

A template containing only headings and comments is not ready. Validation requires meaningful user-authored text.

Extract the request body for analysis:

```bash
python <skill-dir>/scripts/requestctl.py extract \
  --file ".ai-work/intake/request-YYYYMMDD-HHMMSS.md"
```

After deep analysis, review, and plan-spec generation, create the plan with move semantics:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json \
  --request-file ".ai-work/intake/request-YYYYMMDD-HHMMSS.md" \
  --move-request
```

The plan receives `REQUEST.md`. Only after that copy validates successfully is the intake source removed. An empty intake directory is also removed.

## Invocation with a file path

When the invocation argument resolves to an existing regular file, validate and extract it directly:

```bash
python <skill-dir>/scripts/requestctl.py validate --file "docs/change-request.md" --json
python <skill-dir>/scripts/requestctl.py extract --file "docs/change-request.md"
```

Create the plan without `--move-request`:

```bash
python <skill-dir>/scripts/planctl.py create \
  --repo-root . \
  --spec /tmp/plan-spec.json \
  --request-file "docs/change-request.md"
```

This copies the request into the plan as `REQUEST.md` while preserving the caller-owned file.

Paths with spaces must be quoted. Reject missing paths, directories, and symbolic links. If a path-like argument does not exist, tell the user instead of silently treating it as prose.

## Editor selection

`requestctl.py create` chooses an editor in this order:

1. explicit `--editor` command;
2. VS Code when its environment is detected, using `code --reuse-window` or `code-insiders --reuse-window`;
3. `$VISUAL`;
4. `$EDITOR`;
5. the platform default: Notepad on Windows, `open -t` on macOS, or `xdg-open` on Linux.

Failure to launch an editor does not delete the draft. Return the path so the user can open it manually.

Override the editor when necessary:

```bash
python <skill-dir>/scripts/requestctl.py create \
  --repo-root . \
  --editor "vim" \
  --json
```

Create without opening anything:

```bash
python <skill-dir>/scripts/requestctl.py create --repo-root . --no-open --json
```

Reopen an existing draft:

```bash
python <skill-dir>/scripts/requestctl.py reopen --file "<request-path>" --json
```

## Language selection

The draft language defaults from `LC_ALL`, `LC_MESSAGES`, or `LANG`:

- Portuguese locale -> `pt-BR`;
- any other locale -> English.

Override it explicitly:

```bash
python <skill-dir>/scripts/requestctl.py create --language en --json
python <skill-dir>/scripts/requestctl.py create --language pt-BR --json
```

The request may be written in any language. Preserve the user's language for the final summary unless the user asks otherwise.

## Safety and recovery

- Generated drafts stay under the repository-relative `.ai-work/intake/` directory.
- The helper rejects absolute or parent-traversing `work_root` values.
- The helper rejects a symlinked work root or intake directory.
- Request-file validation rejects symbolic links and non-regular files.
- `.ai-work` is added to the repository-local Git exclude file when possible.
- Plan creation stores the request SHA-256 in `manifest.json` and verifies it during every plan validation.
- `--move-request` deletes the source only after `REQUEST.md` exists and the complete plan passes validation.

After a resumed chat, recover the newest generated draft only when the original path is unavailable:

```bash
python <skill-dir>/scripts/requestctl.py latest --repo-root . --json
```

If several drafts exist, show the selected path and let the user correct it before continuing.

## Command reference

```text
requestctl.py create   Create a localized draft and optionally open it
requestctl.py validate Verify that a file contains meaningful request text
requestctl.py extract  Print only the request body
requestctl.py latest   Find the newest generated draft
requestctl.py reopen   Open an existing request file
```

All commands use only the Python standard library.
