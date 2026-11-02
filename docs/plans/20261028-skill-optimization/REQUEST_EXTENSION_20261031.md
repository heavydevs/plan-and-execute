# Additional requirements — 2026-10-31

Branch: `checkpoint/plano1-estudo-provider-switch-20261028`. Existing plan: `.ai-work/20261028-skill-study-provider-switch`.
This is an amendment of a single existing plan, not a second plan or evidence of implemented behavior.

## Coverage

- **P046/R046 → TODO 087 + independent review 088:** For cohesive multi-file DIRECT work, inspect relevant files cheaply, delegate difficult architecture to a stronger model only when justified, then choose a qualified economical executor and monitored tests.
- **P047/R047 → TODO 089 + independent review 090:** Reduce implicit plan-and-execute activation for simple commands and trivial edits through concise discovery metadata and host-level negative invocation tests.
- **P048/R048 → TODO 091 + independent review 092:** When an active task is blocked by complex product bugs or flawed architecture, safely add focused design, repair and monitored validation TODOs without losing checkpoints.
- **P049/R049 → TODO 093 + independent review 094:** For authorized trusted-project implementation delegation, ensure effective localhost, network and workspace access without a hidden sandbox; pause when host policy blocks it.
- **P050/R050 → TODO 095 + independent review 096:** Only at new ORCHESTRATED plan creation, discover alternate provider agents and separately ask permission for missing configuration or login; never prompt during DIRECT work or task execution.
- **P051/R051 → TODO 097 + independent review 098:** Reduce redundant user-facing AI outputs, status messages and manuals while retaining correctness, exact technical detail, clear actions and user-selectable depth.

Existing TODOs 006–029 and 048–063 partially address these areas. They do not cover the six requested end-to-end behaviors or their complete acceptance cases. Preserve the prior 86 task IDs and provider-switch cases A01–A12.

**New execution-guidance research (2026-10-31):** `docs/research/20261028-skill-optimization/prepared-research/ADDITIONAL_12_TASKS_20261031.md`. Every TODO 087-098 must read its own numbered section **and** the cross-feature contract/test notes before implementing or reviewing. The report is a prepared research input, not proof of implementation, independent review, provider access, or test success.

## Implementation contracts

### 087/088: DIRECT architecture delegation with economical implementation

1. Inventory and read all materially relevant files with the current affordable model; forward only decision-relevant evidence to stronger context.
2. Classify architecture complexity independently of plan need; delegate high-risk architecture to a qualified stronger tier with durable design.
3. Return bounded implementation to the current or intermediate tier when testability and capability floors justify it; reroute expensive silent-failure work upward.
4. Run meaningful DIRECT tests through shared resource/log/progress watchers, optionally using a cheap, read-only event-triggered observer.

**Acceptance criteria**
- A cohesive seven-file task stays DIRECT even when one difficult design decision needs a stronger architect.
- The inexpensive stage reads all relevant files; the architecture worker receives a precise evidence packet, not a duplicated source dump.
- The architect outputs a durable design; implementation can return to a lower qualified tier with acceptance checks.
- Stateful DIRECT validations use project resource mapping and log monitoring without creating a TODO plan.
- Compare complete validated cost (read, design, implementation, retries, reviews) to a single qualified model; preserve security floors.

### 089/090: Avoid skill loading for routine commands and trivial changes

1. Narrow host-visible skill description/trigger language without requiring the full instruction body for a negative decision.
2. Test negative activation for git status, one-file read, short shell commands and trivial edits, plus positive explicit plan invocations.
3. Measure false activation, missed activation and prompt bytes on real host traces; do not add a paid classifier.

**Acceptance criteria**
- Simple shell commands, one-file reads and trivial edits do not implicitly load the full skill.
- Explicit plan/lifecycle commands and genuine multi-workstream jobs still activate.
- Tiny discoverable metadata cost is acknowledged; there is no claim of zero skill-related tokens.
- Held-out host evaluations measure false positives/negatives and token impact, not keyword assertions alone.

### 091/092: Create bounded repair tasks for complex active-plan blockers

1. Distinguish a reproducible complex architectural/product defect from resource outages, quotas, flakiness or a cheap local fix.
2. Insert one or more independent design, repair and validation TODOs using lease-safe replayable graph mutation.
3. Deduplicate blocker fingerprints, keep DAG and bounded expansion budgets, and preserve original task status.
4. Validate fixes with mapped health, resource and log monitoring before resuming blocked work.

**Acceptance criteria**
- A complex reproducible blocker creates scoped repair/design TODOs and suspends the original task.
- A temporary outage, quota limit or simple patch does not add tasks or escalate architecture reasoning.
- Idempotency prevents recursive task explosion; leases, cycles and interrupted writes are handled.
- Original validated subtasks survive, and newly created tests must pass before unblocking.

### 093/094: Verify authorized unsandboxed access for implementing agents

1. Specify explicit trusted-workspace/user authorization for unsandboxed source-writing delegates.
2. Map verified native provider version/CLI permission flags, then actively test localhost and required workspace access.
3. Report unsupported or prohibited full access instead of silently falling back to a sandbox or modifying global settings.
4. Keep non-implementing observers restricted and test host denial, wrong flags, resume and unsafe inputs.

**Acceptance criteria**
- An authorized delegated implementer can access permitted loopback services and required paths.
- Provider flags are version-qualified, and effective permission is actually verified.
- Host-enforced restrictions cause an actionable pause, not an unsafe bypass or false success.
- Observers remain genuinely read-only or tool-less, rather than gaining source writes.
- Threats from unrestricted commands are documented, with consent and no credential leakage.

### 095/096: Offer other-provider setup and login before creating a plan

1. Discover alternate provider agents, installed versions, config and auth readiness with bounded non-generative probes.
2. Classify ready, needs_config, needs_login, unsupported and unknown without exposing secrets.
3. Ask separately for each discovered agent needing setup/login before new-plan tasks are created; persist choices.
4. Exclude unavailable providers without capability downgrade; do not ask again on resume, task runs or simple requests.

**Acceptance criteria**
- Each discovered agent needing setup/login gets a separate named consent question only during new-plan preparation.
- Without consent no login, config mutation, token exposure or paid model call occurs.
- Ready agents are not re-prompted; declined and unsupported agents have explicit reasons.
- Existing-plan resume, running TODOs, DIRECT changes and shell commands never run this questionnaire.
- Unknown availability cannot silently widen a forbidden provider chain or lower capability.

### 097/098: Make console, progress and end-user docs concise and precise

1. Define answer-first, literal, specific adult-professional language; do not confuse autism with reduced intelligence or uniform preferences.
2. Cut greetings, repeated recaps, filler, generic praise, unasked tangents and redundant progress without omitting important decisions.
3. Separate concise human output from full machine-readable JSON, diagnostics and logs; expose details/verbose on request.
4. Measure output tokens and repeated-text rate together with accuracy, necessary caveats, actionability, accessibility and actual human comprehension.

**Acceptance criteria**
- A one-step command returns the result and necessary next action, not a verbose status essay.
- Technical answers lead with a precise answer and retain commands, constraints, risk and error explanation when material.
- Do not restate earlier concepts unless necessary for the present decision, apparent confusion or explicit user request.
- User-facing bytes/tokens fall without losing correct steps, safety warnings, machine output or diagnostic evidence.
- The tone respects adult autistic users, avoids overgeneralization and supports individual preference and detail expansion.
- Independent test and human feedback verify non-inferior comprehension, accuracy and completeness, not word count alone.


## Policies and tradeoffs

- Simple commands and trivial changes avoid implicitly loading skill-body instructions; the small host-visible name/description remains unavoidable.
- DIRECT architecture uses economical complete input inspection, transmits only relevant evidence for stronger reasoning and independently routes implementation back to the lowest qualified tier. Root-model switching is not simulated.
- Monitored tests reuse the resource map and event-triggered log observers without a TODO plan. Complex blockers get bounded recoverable repair tasks; environment and quota failures do not automatically trigger larger models.
- Full access for implementation delegates requires a trusted workspace, user and host authorization, version-qualified flags and effective localhost/filesystem probes. Host restrictions are never bypassed. Observers remain truly read-only/tool-less.
- Alternate-vendor setup/login questions are individually addressed to each discovered agent only when creating a new ORCHESTRATED plan. No prompt during DIRECT, resume or task execution. Never capture secrets or perform paid model probes for availability.
- Human-facing answers should be **answer first → material reason/condition → necessary action**. Progress should report a genuine transition, not restate previous updates. Avoid filler, unrequested tutorials and repeated concepts.
- Keep technical vocabulary, exact commands, caveats and errors where necessary. Do not infantilize autistic adults, generalize communication preferences or remove meaningful content in the name of word counts; allow optional detail.
- Measure output token savings against completeness, accuracy, actionability and comprehension, with human reviewers where feasible. Raw diagnostics and machine-readable outputs remain complete.

## Sources inspected (2026-10-31)

- Agent Skills specification: https://agentskills.io/specification. Host skill discovery metadata and progressive disclosure.
- OpenAI skill evaluation: https://developers.openai.com/blog/eval-skills. Evaluate real positive and negative skill selection traces and tokens.
- OpenAI Codex approvals and security: https://learn.chatgpt.com/docs/agent-approvals-security. Full access removes sandbox/approval protections; permission constraints remain material.
- Anthropic Claude Code auto mode: https://www.anthropic.com/research/claude-code-auto-mode. Skipping permissions can expose host resources.
- W3C WAI, Keep Text Succinct: https://www.w3.org/WAI/WCAG2/supplemental/patterns/o3p05-succinct-text/. Main point first, short focused blocks.
- W3C Writing for Web Accessibility: https://www.w3.org/WAI/tips/writing/. Specific error messages, concise unambiguous instructions.
- GOV.UK writing for user interfaces: https://www.gov.uk/service-manual/design/writing-for-user-interfaces. Reduce cognitive load and unnecessary interface text.
- National Autistic Society: autism and communication: https://www.autism.org.uk/advice-and-guidance/about-autism/autism-and-communication. Direct and precise preferences are possible but individual.
- National Autistic Society: accessible information: https://www.autism.org.uk/learn/knowledge-hub/guides-and-resources/accessible-information. Ask about preferred communication and format.
- Autistic Self Advocacy Network: plain language: https://autisticadvocacy.org/2025/07/asan-says-no-generative-ai-in-plain-language/. Do not infantilize or erase meaning; disabled people should review accessibility claims.
- OpenAI reasoning best practices: https://developers.openai.com/api/docs/guides/reasoning-best-practices. Clear goal, direct instructions; verbose chain of thought is unnecessary.
- OpenAI prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching. Cached input does not change output-token generation.

Prepared repository reports (revision 2): 006-activation-intake, 028-delegation, 060-advisory-observer, 062-validate-or-fix.

## Integration and evidence status

Add TODOs 087–098 before integration 082; reviews 088/090/092/094/096/098 are mandatory dependencies of 082. Final whole-skill task 086 remains last. All added tasks start pending. No actual implementation, authenticated provider run, login, host selection experiment or independent reviewer is claimed by this amendment.

## Subsequent focused extension — 2026-11-02 (P052/R052)

The existing tasks 052–063 already cover sliding idle windows, progress event syntax, supervised jobs, resource health and some escalation. They do not provide one verified end-to-end guarantee for productive-work counters and truthful percent, confirmed 300-second semantic stall diagnosis, authorized stronger-code repair and fresh validation. New TODO 099 implements only that missing seam; TODO 100 independently reviews it. The mandatory integration gate 082 depends on 100. See `docs/research/20261028-skill-optimization/prepared-research/099-semantic-progress-recovery.md`. Unknown/environmental stalls do not blindly escalate. All new work remains pending.
