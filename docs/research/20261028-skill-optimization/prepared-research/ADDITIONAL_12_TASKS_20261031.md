# Research-backed execution guidance for TODOs 087-098

Date: 2026-10-31. Target: branch checkpoint/plano1-estudo-provider-switch-20261028.
Purpose: carry the research findings into the existing single plan, before any implementation or independent review.
Status: **design recommendations only**. Nothing below is evidence that a task was executed, a provider was invoked, a test passed, a user approved wider access, or a model was benchmarked.

## Decision rules applying to all twelve tasks

1. Keep the **existing plan and task IDs**, with its manifest as authority and task-specific bounded context. Do not open another orchestration plan for this research.
2. Reuse the existing project routing, execution, validation, resource-watch, availability, and event infrastructure. Add shared interfaces only when required; avoid shadow routers and duplicated state machines.
3. Optimize **cost per correctly validated outcome**, not raw prompt tokens. Record input/output/cache/reasoning usage when observable, monetary model rates for a pinned snapshot when known, extra model calls, tool execution, review, retries, elapsed time, and end-to-end pass rate. Unknown subscription quota/cost must remain unknown, not estimated as API billing.
4. Separate **discovery, reasoning, implementation, review, and deterministic validation**. Avoid paying for a model to carry out deterministic file discovery or CLI capability checks.
5. Preserve hard security, user approval, host-enforced policy, reviewer independence, and actual test evidence even when this increases cost. Do not claim a worker has a certain model, effort, permission, or auth state without verifying effective execution.
6. Keep four compatible contracts across the features: (a) routing decision + cost/evidence; (b) provider readiness + permission/capability; (c) durable task/repair event + graph generation; and (d) machine event + derived concise human presentation.
7. Every review TODO must be executed by a genuinely separate qualified agent/context against the **actual implementation**, with reviewed hashes, recorded findings, fixes, and rerun regressions. This research report does not satisfy a review TODO.
8. Treat source documentation as version-sensitive; before coding CLI/provider details, compare official docs to the installed CLI version and policy. The references are research inputs, not a promise of runtime support.

## 087 — Implement economical DIRECT architecture delegation

**Recommendation.** DIRECT versus ORCHESTRATED is a work-structure decision, **independent** of architecture/model difficulty. A cohesive seven-file change may remain DIRECT while escalating only one design decision. Design an optional stage sequence: economical repository reconnaissance -> qualified high-capability architect only if architecture risk warrants it -> lowest qualified implementation executor -> mapped deterministic validation.

**Algorithm.** Discover complete *materially relevant* code/test/config surface with git listing, rg, call graph/import references and changed-file impact; distinguish coverage from dumping a repository. Produce an evidence packet containing relevant paths, location-specific facts, public interfaces, invariants, failing/passing tests, uncertainty, and source hashes. Send only the decision-relevant subset to the architect; architect produces a short durable decision record with alternatives, selected contract, hazards and acceptance cases. Reuse the same handoff as implementation context. The implementing tier can be cheaper only if capability floors, security risk and detectability allow it. Do not silently switch the parent session's model; use a real delegated worker or report inability to delegate.

**Reuse.** routingctl.py, workload_routing.py, run_isolated.py, validatectl.py, service_map.py, resource_watch.py and routing_telemetry.py. Do not create a parallel cost engine or monitoring map. An optional observer must be bounded/event-triggered and genuinely read-only; no polling LLM for log lines.

**Tests.** One-file trivial edit never delegates; seven-file coherent task stays DIRECT with one hard architecture handoff; cross-cutting risky change goes straight to a sufficiently strong model; packet omits irrelevant file dumps without hiding required facts; design and implementation models are independently routed; monitored DIRECT stateful tests work without creating plan-control files; error/quota/env classes do not blindly escalate tier.

**Measurement.** Compare full validated runs against a one-qualified-model baseline, including extra calls and retries. See [S1], [S2], [S3], [S4].

## 088 — Independently review and correct 087

Require a genuine fresh qualified reviewer, not the implementation worker's summary. Inspect effective model routing, captured input/code hashes, evidence packet, architect decision, changed code, actual monitored test logs, and security floors. Use held-out tasks with easy, medium and high-risk changes; compare single-model versus staged handoff on functional acceptance, regressions, total billed/estimated usage with correct labeling, time, and retry costs. Deliberately test absence of the architect and stale decision packets. Require rerunning the mapped validations after any review fix. No invented savings threshold or reviewer proof. See [S2], [S3], [S5].

## 089 — Prevent unnecessary implicit skill activation

**Recommendation.** Address pre-invocation routing through narrow host-visible name/description metadata and negative examples; use direct exit when legitimately loaded for a small task. The Agent Skills specification exposes the description for matching before the full instructions. Trim the SKILL body, defer references, and avoid adding a paid classifier or shadow coordinator to decide whether the skill deserves loading.

**Provider nuance.** Claude Code has disable-model-invocation and a user-invocable-only override. These are useful for a deliberately manual-only installation, **not as the default**, because they also suppress legitimate automatic activation; in some configurations they remove discovery text too. Host behavior differs: document host-specific overrides rather than silently assuming equivalent controls in Codex. Keep explicit plan creation/resume/cancel invocations reachable, and retain implicit selection for genuine independent workstreams/long recoverable work.

**Tests.** Live or instrumented host traces: negative git status, branch checkout/push, single read, one-line edit, routine bug fix; positive explicit plan, multi-workstream migration, interrupted resume, broad research/security change. Measure metadata tokens and full-body tokens separately; metadata cost cannot always be reduced to zero. See [S1], [S3], [S6].

## 090 — Independently review and correct 089

Use held-out, realistic positive/negative prompts (including ambiguous wording and competition from another matching skill) across supported hosts. Build a confusion matrix: unnecessary activation, missed critical activation, direct exit after accidental load, explicit invocation success, prompt bytes/tokens, and regressions in normal small-task latency. Check Claude-specific settings experimentally; do not treat a frontmatter toggle as a cross-provider fix. No string-match-only test may count as host-activation evidence. Re-run routing/activation self-tests. See [S1], [S3], [S6].

## 091 — Add repair tasks only for complex active-plan blockers

**Recommendation.** Add an explicit *blocker-to-graph-mutation* transaction to the existing planctl/runner/lifecycle contract. Not every failure becomes a TODO. Classify reproducible architectural/product blocker versus local patchable defect, environmental outage, rate/quota limit, transient test failure or unavailable service. Only complex product/architecture blockers produce scoped design/repair/validation TODOs.

**Durable algorithm.**
1. Collect a bounded failure packet: failing task/subtask, reproducible evidence, relevant file/test hashes, failure class, root-cause hypothesis.
2. Compute stable blocker fingerprint from normalized failing contract + cause + affected owner (not timestamps/transcript); record current plan generation and lease.
3. Under a narrow exclusive mutation guard, reload state, check fingerprint/idempotency and expansion budgets, create dependent repair nodes in a topologically valid DAG, make original task blocked on successful repair validation, and atomically persist a new generation. Never write an incomplete pending edge.
4. Reconcile materialized TODO/task markdown only after manifest transaction; on crash, rerender deterministically from authoritative manifest. Keep original verified subtasks unchanged; reopen only stale affected contracts.
5. Run mapped resource/log-aware repair tests before unblocking. Failed repair resumes its own task rather than recursively duplicating siblings.

**Budget.** Define explicit maximum repair depth/children and require user or reviewer intervention on budget exhaustion; tune via tests, not arbitrary endless recursion. Enforce symlink/path and lease guards. Favor applying replay/idempotency principles to the existing JSON manifest rather than adding Temporal/LangGraph dependencies. See [S7], [S8].

## 092 — Independently review and correct 091

Inject faults after claim, after graph validation, just before/after atomic rename, after TODO projection, and before resuming original task; rerun each to prove crash recovery. Race two workers on the same fingerprint; prove only one repair subgraph is created. Test stale lease, duplicate event, cycle, max expansion, simple bug, quota error, unavailable localhost and recurring complex blocker. Confirm all completed unaffected subtasks survive and repair validations are real fresh mapped checks. Inspect generation/lineage, idempotency and review independence. See [S7], [S8].

## 093 — Authorize and verify effective delegated implementer access

**Recommendation.** Treat access as explicit **capabilities**, not a Boolean 'full_access'. Distinguish desired filesystem roots, write actions, loopback endpoints, outbound internet, process execution, credentials, shell, and whether the agent is a writer or observer. Effective permissions are the intersection of user approval, host policy, provider CLI, process isolation and actual endpoint/path reachability. A request for no sandbox is not permission to bypass a host-enforced policy.

**Implementation.** Detect provider and pinned CLI version; use provider-specific documented flags and approval settings, never guessed generic flags. Require informed user authorization and a trusted/disposable workspace before an unsandboxed writer is enabled. Prefer narrow workspace permission plus explicit network exceptions when sufficient. Probe allowed temporary-file create/read/delete and required 127.0.0.1 service from the **delegate process/network namespace**; avoid a destructive or credential-bearing probe. Record approved scope, effective probe results, denials, versions and redacted evidence. Fail closed/actionably if the host cannot supply requested legitimate capabilities. Never modify global CLI settings silently.

**Critical Claude nuance.** Depending on parent permission mode, Claude subagent permissionMode may be ignored; disallowed Write/Edit tools alone do not guarantee read-only if Bash/MCP can write. Place observers in separately enforced restricted subprocess/tool boundaries (or entirely tool-less). Do not grant full access to read-only reviewers or observers by inheritance.

**Tests.** Host denial, stale flags/version, wrong working dir, path escape/symlink, blocked or unavailable localhost, differing network namespaces, disabled shell, unauthorized write, resume and log secret redaction. See [S9], [S10], [S11].

## 094 — Independently review and correct 093

Threat-model a malicious repository instruction, untrusted stdout, prompt-injected tests, unsafe command expansion, and secrets in logs; confirm no elevation beyond explicit scope. Test with a true full-access writer and an isolated read-only observer under a privileged parent. Verify permissions by behavioral probes, not by the presence of argument strings. Cover provider/OS/CLI-version matrix (Windows, WSL2, Linux as available); unavailable platforms are 'not verified', not passed. Reject insecure fallback and re-run security checks after fixes. See [S9], [S10], [S11].

## 095 — Prepare alternate provider configuration only for new plans

**Recommendation.** Put a short, no-inference readiness gate at **new ORCHESTRATED plan creation**, before writing plan tasks. Skip on DIRECT, exact lifecycle/status commands, resume and task execution. Use bounded process timeouts and non-generative probes: executable presence and version, supported provider profile and config parse, provider-specific auth status. For example, codex --version, codex login status; claude --version, claude auth status. Do not run a paid generation to 'prove' availability. Auth success does **not** prove tier quota, availability of every model, organization policy, or actual task capability.

**Five outcomes.** ready, needs_config, needs_login, unsupported, unknown. Persist per-provider state, observed version, source/probe timestamp, user choice and reason without secrets; treat unknown conservatively. Ask separately for each named agent needing setup or login, only at that new-plan gate. Do not login, edit user-global config, reveal tokens or spend on models unless the user explicitly authorizes each relevant action. If a provider is declined/unavailable, select only an allowed provider meeting the minimum capability floor; otherwise stop with a precise explanation.

**Reuse.** configure.py, availability.py, model_catalogctl.py, routing_config.py, preplanctl.py. Account for automation/non-interactive hosts where asking is impossible: pause with resumable preplan state rather than prompting during a task. See [S12], [S13].

## 096 — Independently review and correct 095

Mock multiple provider CLI binaries and status responses with finite timeouts; include no executable, invalid config, current auth, logged-out auth, expired auth, stale status, version mismatch, noninteractive host, unsupported model, duplicate choices, explicit decline and interrupted setup. Assert zero paid calls, login attempts and config mutations when consent is missing; no secret-bearing output in logs. Check that ready providers are not re-prompted and declined providers cannot be reintroduced through fallback. Validate resuming an existing plan bypasses the questionnaire. See [S12], [S13].

## 097 — Make user-facing communication concise but precise

**Recommendation.** Derive human messages from structured event records instead of asking the LLM to repeatedly narrate every step. Store full machine events (task id, transition, status, severity, evidence pointer, next actionable step) separately from human rendering. Default renderer: **result first -> relevant condition or risk -> next action**. Provide explicit expanded/verbose modes and full machine JSON for integration; do not truncate machine evidence.

**Output policy.** State changes worth showing: task started when meaningful, blocker/required consent, reproducible failure with action, completion with test count and next step. Suppress duplicate progress, greetings, praise, re-summaries, filler and unrequested tutorials. Use event IDs/fingerprints for deduplication; do not mistake absent progress logs for success. Preserve commands, paths, limitations, safety caveats, reasons for failure and unresolved checks when useful. Avoid global hard word caps: complex instructions need sufficient words.

**Accessibility.** Use literal, explicit, precise adult-professional writing, headings and one concept per block. Do not presume all autistic readers prefer the same style, need simpler vocabulary, or have lower intelligence. Allow a user-chosen level of detail and incorporate actual feedback. Apply W3C cognitive accessibility guidance and user-involved review rather than claiming clinical validation.

**Tests.** Short git command with succinct result; failed test with exact diagnosis; consent required; permission denied; long installation guide with every necessary step; explicit 'explain deeply'; Portuguese/English consistency; unchanged JSON diagnostics and unredacted evidence *only within secure logs* (never expose secrets). See [S14], [S15], [S16].

## 098 — Independently review and correct 097

Run blinded paired comparisons on the same scenarios with the old/new renderer; measure visible output tokens, repeated-span rate, factual accuracy, omitted mandatory steps, actionability, confusion, need for follow-up clarification, and human task-completion/comprehension. Where feasible, include consenting adult users, including neurodivergent users with differing preferences; never claim to have tested real humans without evidence. Preserve complete machine logs and safety details. Approve concision only where accuracy and comprehension are non-inferior; classify any omission of a necessary warning or command as a failure regardless of token savings. See [S14], [S15], [S16].

## Cross-feature integration and test order

- Before 082, finish implementation and real independent review of each pair: 087/088, 089/090, 091/092, 093/094, 095/096, 097/098. Do not mark tasks complete on prepared research.
- Tests must prove the *composed behavior*: a small command does not activate planning (089), a hard-but-cohesive coding change uses DIRECT and may seek strong architecture (087), a new orchestrated plan alone offers provider setup (095), its writer obtains only authorized effective capabilities (093), a genuine complex blocker safely inserts durable repair work (091), and user-facing progress remains concise while machine evidence stays complete (097).
- Independent reviews must check actual source/code hashes and rerun mapped P1_TESTS_XXX/P1_XXX validations. Re-run integration and packaging checks in 082-086.
- Create explicit counterexamples for feature interference: an already-running DIRECT task never launches the setup questionnaire; quota errors do not create repair tasks; an observer never inherits writer access; user-facing brevity never suppresses an unsafe-permissions warning.
- Report all unverified external provider/OS tests and costs honestly.

## Shared evidence contracts (proposed interfaces, not implemented)

1. RoutingDecision: task_or_direct_id, phase, selected_provider/model/effort, capability_floor, rationale, evidence_hash, measured_usage_or_unknown, baseline_comparison.
2. EffectiveCapability: provider_cli_version, requested_scopes, user_consent_reference, host_policy_result, verified_probes, limitations, role(writer/observer).
3. RepairMutation: manifest_generation, blocker_fingerprint, original_task/subtask, failure_class, new_task_ids, dependency_delta, lease_epoch, recorded_validation.
4. ProgressEvent: stable_id, task_id, phase, transition, severity, evidence_ref, user_action_required, human_render_policy.

No part of this report requires adding all four JSON schemas blindly: implement the smallest compatible extension to the contracts already used in the repository.

## Sources and relevance

Official/documentation:
- [S1] Agent Skills specification (discovery metadata and progressive loading): https://agentskills.io/specification
- [S2] Claude Code subagents (isolated context, model/permission inheritance, tools): https://code.claude.com/docs/en/sub-agents
- [S3] Claude Code skills (activation, disable-model-invocation, body context cost): https://code.claude.com/docs/en/skills
- [S4] OpenAI prompt/agent routing and implementation guidance: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- [S5] OpenAI evals for Agent Skills (positive/negative real traces): https://developers.openai.com/blog/eval-skills
- [S6] Agent Skills spec and Claude documentation cited above; host-only negative invocation is **not** achievable via a repo script that runs after a skill is loaded.
- [S7] Temporal durable workflow and replay contract (principles, not dependency recommendation): https://docs.temporal.io/workflows
- [S8] LangGraph persistence / interrupt / resume (conceptual comparison): https://docs.langchain.com/oss/javascript/langgraph/thinking-in-langgraph
- [S9] OpenAI/Codex sandbox and approvals (separate controls): https://developers.openai.com/pt-BR/docs/sandboxing
- [S10] OpenAI guardrails and human review, including fail-closed boundaries: https://developers.openai.com/api/docs/guides/agents/guardrails-approvals
- [S11] Claude Code subagents and CLI flags: https://code.claude.com/docs/en/sub-agents and https://code.claude.com/docs/en/cli-reference
- [S12] Claude CLI reference for auth status: https://code.claude.com/docs/en/cli-reference
- [S13] Codex developer commands for auth status: https://learn.chatgpt.com/docs/developer-commands?surface=cli
- [S14] W3C cognitive accessibility, succinct and literal text: https://www.w3.org/TR/coga-usable/
- [S15] GOV.UK writing for user interfaces: https://www.gov.uk/service-manual/design/writing-for-user-interfaces
- [S16] National Autistic Society, communication differences/preferences: https://www.autism.org.uk/advice-and-guidance/about-autism/autism-and-communication

Books / research for architectural trade-offs (design inputs, not runtime evidence):
- Kleppmann & Riccomini, Designing Data-Intensive Applications, second edition: transactional changes, consistency and recoverability; https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/
- Google, Building Secure and Reliable Systems: least privilege, isolation, incident reasoning; https://google.github.io/building-secure-and-reliable-systems/raw/ch05.html
- Google SRE Book: service-level validation, monitoring, failure diagnosis; https://sre.google/sre-book/table-of-contents/
- RouteLLM, ICLR 2025: quality/cost-based model routing motivation, not an automatic guarantee for coding workloads; https://proceedings.iclr.cc/paper_files/paper/2025/hash/5503a7c69d48a2f86fc00b3dc09de686-Abstract-Conference.html

## Evidence limits

This document records desk research and engineering recommendations, not a measured improvement. No provider was authenticated, no independent reviewer was dispatched, no live CLI access was verified, no benchmark was executed, and no new implementation/test was run as part of its preparation. Tasks 087-098 remain pending until real task evidence is recorded.
