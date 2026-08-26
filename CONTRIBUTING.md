# Contributing

1. Create a focused branch from `main`.
2. Keep skill instructions concise and move detailed procedures into `references/`.
3. Add deterministic tests for every script or installer behavior change.
4. Keep `TODO.md` one line per task; execution metadata belongs in task definitions.
5. Run:

```bash
npm ci
npm run check
npm pack --dry-run
```

6. Update `CHANGELOG.md` and both README languages when user-facing behavior changes.
7. Open a pull request describing behavior, validation evidence, compatibility impact, and any migration notes.
