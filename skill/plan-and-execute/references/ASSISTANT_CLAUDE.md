# Claude advisory profile

Load only when `assistant.enabled` is true and `assistant.provider` is `claude`, or when diagnosing that profile.

Claude advisory execution requires a native `claude`/`claude.exe` and an explicitly supplied `ANTHROPIC_API_KEY`. It uses API billing, not subscription OAuth, and does not copy credentials from files, keychains, wrappers, hooks, plugins, or worker settings.

The adapter verifies the required bare/tool-less CLI flags and then uses `--bare`, `--tools ""`, strict empty MCP configuration, disabled slash commands, no session persistence, one turn, and a strict JSON schema. It runs in a fresh private directory with a minimal environment. Coding-worker arguments and unrelated secrets are not inherited.

Antigravity, Codex, Gemini, Qwen, Kimi and Trae remain valid coding executors but are not supported advisory profiles here. Their current native interfaces do not provide the same verified per-run read-only/tool-less boundary; never fall back to a coding adapter just to obtain advice.

Missing key, unsupported command wrapper, missing CLI/capability, refusal, timeout, invalid output, or process failure returns to normal validation/failure handling without another adviser.

Primary references reviewed 2026-09-28:
- https://code.claude.com/docs/en/headless
- https://code.claude.com/docs/en/cli-reference
