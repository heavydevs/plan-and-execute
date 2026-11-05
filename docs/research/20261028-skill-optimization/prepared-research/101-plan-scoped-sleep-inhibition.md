# P053 — Whole-plan host OS sleep inhibition for overnight autonomous execution

**Research date:** 2026-11-05. **Branch:** `checkpoint/plano1-estudo-provider-switch-20261028`. **Single active plan:** `.ai-work/20261028-skill-study-provider-switch`.

**Status:** prepared design **only**, not implemented or independently reviewed. New TODO 101 will implement the feature, and TODO 102 will perform an actual independent maximum-qualified code review/correction; both remain pending until real tests, hashes and review evidence exist.

## Objective, gaps and guarantees

The user wants to start a plan involving many agents/tasks and go to sleep, without **automatic OS idle sleep/hibernation** interrupting computation. The plan already covers durable checkpoints/resume (018/019), supervised long jobs (054/055), watchdog (056/057), cross-platform installation/CI (066/067), authorization (093/094), and semantic long-validation progress (099/100). However, none ensures one **host-owned power inhibitor** stays alive *between* all worker sessions, models, validations and TODOs. Add only this missing lifecycle seam; no new planner, watchdog or LLM polling loop.

**Do not claim universal overnight reliability.** Native idle blockers generally do not stop explicit lid close/manual sleep, shutdown/reboot, battery/thermal safety events, enterprise policy, loss of electricity, WSL host isolation, or provider quota/auth/network/approval issues. Screen sleep should remain enabled. Durable checkpoint-based resume remains essential.

## Alternatives studied

| Solution | Assessment |
|---|---|
| Permanently change Windows powercfg, macOS pmset or Linux logind.conf | Reject: modifies user/global configuration, privilege and crash recovery problems |
| Fake mouse/keyboard events, CPU busy loop or fake progress | Reject: intrusive, costly and not a reliable power-management contract |
| Agent-specific hooks/sleep controls for each Claude/Codex/Gemini/Qwen/... execution | Insufficient: protection gaps between agents, test commands, TODO transitions and approval waits |
| Third-party tray monitor and shell hooks | Optional comparison, not required: vendor compatibility and risky lid handling |
| **Native OS inhibitor owned by the whole plan coordinator** | **Choose:** one deterministic lease for every task/provider; releases with host-owned handle/FD/process, no persistent policy edit |

## Host-specific research

### Windows

- `SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)` blocks idle sleep while the **same owner thread remains alive**. Clean up with `SetThreadExecutionState(ES_CONTINUOUS)` on that thread. Do not launch a short-lived helper and assume its setting persists. Check return codes. Do not use `ES_DISPLAY_REQUIRED` or `ES_AWAYMODE_REQUIRED`; let the monitor sleep.
- Alternative `PowerCreateRequest`/`PowerSetRequest(PowerRequestSystemRequired)` with `PowerClearRequest` and handle close. Microsoft explicitly warns **Modern Standby on battery/DC** terminates system/execution-required requests five minutes after the system sleep timeout. Continuous blockers may drain battery; Windows power management and corporate policy can still take precedence. The system can still sleep when a user closes lid or explicitly requests it.
- `powercfg /requests` is read-only status, not a proof of sustained permission/policy. Never mutate `powercfg /change`, `/requestsoverride`, registry, AC/DC timeout or request admin privileges silently. Test lifetime, AC/DC, Modern Standby and denied policy.

### macOS

- Supervised `caffeinate -i -w <coordinator_pid>` or `caffeinate -i <runner>`, or direct IOKit `IOPMAssertionCreateWithName(kIOPMAssertionTypePreventUserIdleSystemSleep)` + checked release. Built-in utility is simple; IOKit avoids subprocess overhead but is more complex.
- Apple's `PreventUserIdleSystemSleep` protects only **idle** system sleep, not lid-close, Apple menu, low battery or other sleep reasons. Display can dim/sleep. Do not change global `pmset`.

### Linux

- Use a host logind sleep/idle inhibitor retained across **the entire runner process**, e.g. `systemd-inhibit --what=idle:sleep --mode=block --who=plan-and-execute --why='Active plan' <runner>`, or a logind D-Bus `Inhibit` whose FD stays open. Acquire before first worker, release after completion. Read-only `systemd-inhibit --list` may aid inspection.
- `LidSwitchIgnoreInhibited=yes` defaults to ignoring high-level sleep inhibitors when logind handles lid switch. A `handle-lid-switch` low-level override is a different, user-sensitive action; never silently enable it. Missing systemd/DBus, permissions or policies must return unavailable/denied.

### WSL2, Docker, containers, VMs, remote hosts

A Linux inhibitor in WSL does **not** imply the Windows physical host stays awake; use an authorized Windows-host helper that remains alive or explicitly report unsupported. A container/VM inhibitor does not necessarily cover its host. A managed/cloud/CI host may be terminated by the infrastructure independently. Detect **which machine owns power**; never report a guest-only inhibitor as physical laptop protection or bypass agent sandbox to acquire one.

## AI agent/vendor documentation review

| Plan-supported agent/provider | Documented unattended interface | Sleep implication |
|---|---|---|
| **Claude Code / Agent SDK (Anthropic)** | `claude -p` noninteractive, permissions and sessions | Coordinator owns host lease across distinct Claude invocations |
| **Codex CLI / SDK (OpenAI)** | `codex exec`, approval/sandbox and resume | Host coordinator guard outside sandbox; no permission weakening |
| **Antigravity/Gemini (Google)** | `agy -p` and headless approvals; some soft-denials can return exit 0 | Host guard cannot solve approvals; check actual output/evidence |
| **Qwen Code** | `general.preventSystemSleep=true`; macOS caffeinate, Linux systemd-inhibit, Windows SetThreadExecutionState during model streaming/tool calls | Relevant native implementation precedent, **not whole-plan gapless coverage** |
| **Kimi Code (Moonshot)** | Noninteractive prompts and version-specific permissions | Preflight approvals separately |
| **Trae Agent (ByteDance)** | Persistent shell, background process and bounded tool execution | Session lifetime alone does not block host sleep |
| **Muse Code (Meta)** | Headless `muse exec` and approval/sandbox modes | Host guard independent of provider |
| **GLM (Z.ai)** | Client/model profiles vary | A hosted model endpoint cannot hold a host power request |
| **DeepSeek** | Codex CLI provider integration | Protect local client/host, not remote model endpoint |

The community `agents-dont-sleep` tool is an optional comparison only; do not add a required third-party tray app or provider hook dependency to guarantee all phases.

## Chosen lifecycle and unattended-readiness policy

1. **Auto-on locally:** Scoped `prevent_idle_sleep=auto` by default for productive **ORCHESTRATED RUNNING** plans, not tiny DIRECT jobs; explicit opt-out. `require_awake` strict overnight mode must abort **before paid workers** if host protection is unavailable or denied. Ordinary auto mode should warn, not lie.
2. **Acquire before dispatch:** Host supervisor, outside restricted worker sandboxes, takes exactly one verified lease with owner plan/process, backend, host OS (including WSL), reason, and clear `active/degraded/unsupported/denied/released` state. Never record secrets.
3. **Gapless:** Keep the inhibitor through task transitions, fresh agent conversations, provider switches, test jobs, reviews, repairs and legitimate 310+ second quiet validations. Worker exit must not release the supervisor guard.
4. **Release safely:** In idempotent finalization/signal handling for completion, failure, cancellation, reset, SIGINT/SIGTERM and explicit pause waiting on human approval. Concurrent plans must not release each other's active requests. A force-killed supervisor must not leak permanent host power changes; use native handle/FD/process lifetime.
5. **Recover:** On interruption/restart, existing checkpoints decide remaining work. Check stale PID/ownership, reacquire fresh inhibitor and verify **before the next worker**. Do not trust a prior status file as a living host lock.
6. **Preflight distinct dependencies:** Power, mains/battery, session/terminal survival, auth, noninteractive approvals, quota, network and resumability have separate statuses. Never auto-approve risky operations, bypass sandbox/admin policy or loop through costly retries to chase an overnight goal.
7. **Efficient evidence:** Acquire/release/error events, not per-second LLM calls. Reuse current monitoring and service map; add backend mocks, cross-platform CI and safe native OS smoke checks where available.

## Acceptance / adversarial tests

- Protection held *without release/acquire gap* across **two different providers**, at least two TODOs, reviews/handoffs and a 310+ second legitimate quiet validation.
- Display may turn off; never issue permanent power setting changes, synthetic input or hidden lid/thermal/battery overrides.
- Verified cleanup on success, failure, explicit pause, cancel/reset, SIGINT/SIGTERM, forced death, duplicate acquire/release and concurrent plans; no cross-release.
- Crash/restart/resume rechecks host/owner, reacquires before paid worker, rejects stale PIDs/orphans and leaves durable task results intact.
- Windows native API return/lifetime/Modern Standby DC/policy denial; macOS caffeinate/IOKit and lid/battery; Linux logind/DBus/lid high-level default; WSL guest-only cannot falsely protect host.
- Strict unattended preflight fails before model calls if host guard is denied; normal mode visibly warns. Auth/quota/network/approval remain independent blocking conditions.
- Deterministic mocks + non-invasive OS CI/smoke checks and affected runner/lifecycle regressions; actual source hashes and logs required. No intentional hibernate testing on user's machine.
- Genuine fresh independent reviewer with source hashes/effort/provider identity in task 102; critical/high findings corrected or gate remains pending. Integration 082 depends on 102; final 086 remains last.

## Primary official sources and engineering literature (consulted 2026-11-05)

1. Microsoft SetThreadExecutionState: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate
2. Microsoft PowerSetRequest and Modern Standby DC: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-powersetrequest
3. Microsoft PowerClearRequest: https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-powerclearrequest
4. Microsoft System Sleep Criteria: https://learn.microsoft.com/en-us/windows/win32/power/system-sleep-criteria
5. Microsoft powercfg diagnostics: https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options
6. Apple IOPMAssertionCreateWithName: https://developer.apple.com/documentation/iokit/1557134-iopmassertioncreatewithname
7. Apple PreventUserIdleSystemSleep: https://developer.apple.com/documentation/iokit/kiopmassertiontypepreventuseridlesystemsleep
8. Historical macOS caffeinate man page mirror: https://man.freebsd.org/cgi/man.cgi?apropos=0&manpath=macOS+10.13.6&query=caffeinate&sektion=8
9. freedesktop systemd-inhibit: https://www.freedesktop.org/software/systemd/man/latest/systemd-inhibit.html
10. freedesktop logind.conf lid switch: https://www.freedesktop.org/software/systemd/man/latest/logind.conf.html
11. Anthropic Claude Code CLI: https://docs.anthropic.com/en/docs/claude-code/cli-usage
12. OpenAI Codex noninteractive: https://learn.chatgpt.com/docs/non-interactive-mode
13. Google Antigravity headless: https://antigravity.google/docs/cli/headless/
14. Qwen official sleep inhibition announcement: https://qwenlm.github.io/qwen-code-docs/en/blog/updates/weekly-update-2026-06-11/
15. Qwen headless: https://qwenlm.github.io/qwen-code-docs/en/users/features/headless/
16. Moonshot Kimi CLI: https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command
17. ByteDance Trae tools: https://github.com/bytedance/trae-agent/blob/main/docs/tools.md
18. Meta Muse Code: https://dev.meta.ai/docs/muse-code
19. Z.ai GLM/ZCode: https://zcode.z.ai/en/docs/welcome
20. DeepSeek Codex integration: https://api-docs.deepseek.com/quick_start/agent_integrations/codex/
21. Google SRE book Handling Overload: https://sre.google/sre-book/handling-overload/
22. Google SRE book Effective Troubleshooting: https://sre.google/sre-book/effective-troubleshooting/
23. Optional community comparison only: https://github.com/itsmbaqer/agents-dont-sleep

**Documentation versus inference:** The API limits are documented; plan-owned guard semantics and configuration defaults are the **proposed architecture**, not tests of the user's real machine or installed CLI version. Physical host, lid/policy and long-run reliability require implementation-time evidence.
