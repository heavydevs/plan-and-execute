# P053 / R053 — Prevent automatic computer sleep during a running plan (2026-11-05)

Target branch: `checkpoint/plano1-estudo-provider-switch-20261028`; existing one-plan work: `.ai-work/20261028-skill-study-provider-switch`.

User request: after studying vendors, OS documentation and reliability literature, add an implementation task that prevents local computer inactivity sleep/hibernation across an overnight multi-TODO AI workflow.

**Decision:** TODO 101 implements one host OS-native, coordinator-owned, verified power lease over all RUNNING ORCHESTRATED tasks; TODO 102 independently reviews and corrects it. Both pending and precede integration 082. The whole-skill task 086 stays last. Default local auto-on, opt-out, strict overnight require-awake preflight; release on completion/cancel/explicit pause, preserve durable resume.

Do not change global Windows powercfg/macOS pmset/Linux logind policy or secretly override lid, thermal and battery safeguards. Sleep prevention cannot guarantee against manual shutdown, lid, Modern Standby battery behavior, policy, network, quotas, auth or interactive approvals. Research/alternatives/sources/tests: `docs/research/20261028-skill-optimization/prepared-research/101-plan-scoped-sleep-inhibition.md`. No product implementation, live OS tests or external review is claimed here.
