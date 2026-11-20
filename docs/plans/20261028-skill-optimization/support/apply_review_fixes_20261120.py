#!/usr/bin/env python3
"""Apply PLAN_ARCHITECTURE_REVIEW_20261120.md sections A/B to the pending task content.

Declarative and idempotent: every operation states a target state, so a second run
leaves every file byte-identical. The authoritative manifest is edited first; then
PLAN1_SPEC.json is re-projected from it (same fields the structural gate compares),
TASK_INPUTS.json gets checks/scope/acceptance_ids, and every task definition plus
TODO.md is re-rendered with the plan's own renderer (planctl_concise). No task id,
requirement id or status changes; autostart stays false.

Not handled here (owned elsewhere): support/check_delivery.py, run_task_checks.py,
delivery_gate_self_test.py, orchestrator.config.json, MODEL_MATRIX.*, SERVICE_MAP.md
and the routingctl.py ESCALATION_LADDERS comment.

Usage: python docs/plans/20261028-skill-optimization/support/apply_review_fixes_20261120.py [--check]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / "docs/plans/20261028-skill-optimization"
PLAN = ROOT / ".ai-work/20261028-skill-study-provider-switch"
REVIEW_REF = "docs/research/20261028-skill-optimization/PLAN_ARCHITECTURE_REVIEW_20261120.md"
APPLIED_AT = "2026-11-20T12:00:00Z"

sys.path.insert(0, str(ROOT / "skill/plan-and-execute/scripts"))
import artifact_contract  # noqa: E402  (task text budgets of the plan contract)
import planctl_concise  # noqa: E402  (renderer used by the native controller)

PC = planctl_concise.planctl

SK = "skill/plan-and-execute/scripts/"
REF = "skill/plan-and-execute/references/"


def sk(name: str) -> list[str]:
    return ["python", SK + name]


def py(path: str, *args: str) -> list[str]:
    return ["python", path, *args]


VALIDATE_SKILL = ["node", "tools/validate-skill.js"]
STRUCTURE = py("docs/plans/20261028-skill-optimization/support/check_delivery.py", "--structure")
RELIABILITY = sk("reliability_self_test.py")
ROUTING = sk("routing_self_test.py")

META_LINES = {
    "The prepared report is input evidence, not proof that this implementation or its independent review has passed.",
    "Prepared research is not proof of implementation or independent-review completion.",
}
FRONTIER_REVIEW = ("A frontier (Fable 5.2 / Astra 6.2) reviewer is accepted only with recorded repeated "
                   "max-review failure; a reused review session or dispatch is rejected.")
A9 = ("Effective top tier is max; frontier is never a ladder or switch rung and is never reached for "
      "implementation, quota, auth or environment outcomes.")
A10 = ("The v8 map is preserved: Opus 5.5 / Sol 6.2 xhigh at max, Fable 5.2 / Astra 6.2 absent from the "
       "tier map, Antigravity Claude capped at advanced, Gemini 4 Hydrogen/Neon preset ordered first, Carbon not routed.")


def review_pair_line(impl: str) -> str:
    return f"Every 2026-11-20 acceptance addition of task {impl} has actual test evidence on the final reviewed hashes."


def rng(a: int, b: int) -> list[str]:
    return [f"{i:03}" for i in range(a, b + 1)]


# --------------------------------------------------------------------------------------
# Declarative table: (task ids, operations). Applied in order; each op is idempotent.
# --------------------------------------------------------------------------------------
OPS: list[tuple[list[str], dict]] = []


def op(ids, **ops):
    OPS.append(([ids] if isinstance(ids, str) else list(ids), ops))


# ---- 001-005 ------------------------------------------------------------------------
op("001",
   sub={"S002": (None, "Implement only the deterministic preflight contract from ARCHITECTURE_AND_SCOPE.md using the pinned inventory and current task catalog; coverage checks belong to 002."),
        "S003": (None, "Add negative fixtures for stale hashes of pinned TASK_INPUTS prepared_reports/input_contract files, missing resources, unsupported CLI versions and broad context loading; report historical BASELINE_INVENTORY.json drift as drift, never a failure.")},
   acc_add=["Preflight passes against the current tree with 131/188 inventory hashes changed and lists that drift instead of failing."])
op("002",
   sub={"S002": (None, "Import check_delivery.structural and check_delivery.verified_files for source/contract coverage; do not reimplement them."),
        "S003": (None, "Add only the negative fixtures delivery_gate_self_test.py lacks: unknown SOURCES id, report hash drift, requirement without consumer, task without prepared_report, missing 082 review gate.")},
   acc_add=["A report record citing an unknown SOURCES id is rejected.",
            "A prepared report whose hash drifted from its pinned INDEX/TASK_INPUTS hash is rejected.",
            "A requirement with no consuming task is rejected.",
            "A task entry without a prepared_report is rejected.",
            "A plan missing a required 082 review-gate dependency is rejected."])
op(["002", "003"], checks_add=[py("docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py")])
for _rid in ("003", "005"):
    op(_rid,
       sub={"S002": (None, "Use a real fresh maximum-qualified code reviewer with the changed diff, report and acceptance evidence; do not send unrelated task histories."),
            "S003": (None, "Correct every blocking finding or leave the gate incomplete with a recorded reason."),
            "S004": (None, "Re-run declared checks after corrections and pin the final reviewed source state.")},
       acc_set=["Actual fresh reviewer provider/model/effort and reviewed input hashes are recorded.",
                "No unresolved critical/high finding remains; the assigned acceptance cases have actual test evidence.",
                "A reused or fabricated review receipt is rejected.",
                "The prepared report is input evidence, not proof that this implementation or its independent review has passed."])
op("004",
   sub={"S002": (None, "Build one shared fake-provider fixture (claude/codex/antigravity argv; success, quota, auth and functional outcomes) that starts no subprocess and makes no network call."),
        "S003": (None, "Implement a report-aware loader that returns only the entry's prepared_reports/input_contract paths and rejects unlisted reports and the task's own not-yet-created files."),
        "S004": (None, "Add a credit-exhaustion fixture classified distinctly from auth and functional failures.")},
   acc_set=["One shared fake-provider fixture covers claude/codex/antigravity argv with success, quota, auth and functional outcomes and starts no subprocess or network call.",
            "The report-aware loader returns only the entry's prepared_reports/input_contract paths and rejects unlisted reports and the task's own not-yet-created files.",
            "A credit-exhaustion fixture is classified as availability, distinct from auth and functional failures.",
            "Offline contract tests pass with no model call or user-global configuration write.",
            "Actual code changes and acceptance evidence are recorded.",
            "The prepared report is input evidence, not proof that this implementation or its independent review has passed."])

# ---- 006-018 ------------------------------------------------------------------------
op("006",
   sub={"S003": (None, "Measure entrypoint bytes and offline false-positive/false-negative rates on held-out routing-evals.json against baseline; live host loading/latency only with owner-confirmed authenticated runs, otherwise a recorded limitation.")},
   acc_replace=[("Measure entrypoint bytes, referenced files actually loaded and routing false-positive/false-negative cases against baseline.",
                 "Entrypoint bytes and offline false-positive/false-negative rates on held-out routing-evals.json are measured against baseline; live host loading/latency needs owner-confirmed authenticated runs, else a recorded limitation.")])
op(["006", "007"], checks_add=[sk("self_test.py")])
op("008", sub={"S004": (None, "Measure obligation recall and contradiction coverage against a deterministic one-shot extraction comparator offline; a model-based comparison needs owner confirmation (G002), otherwise it is a recorded limitation.")})
op(["010", "011"], checks_add=[sk("artifact_concision_self_test.py")])
op(["012", "013"], checks_add=[sk("self_test.py"), sk("lifecycle_self_test.py"), sk("context_self_test.py"), sk("task_memory_self_test.py")])
op("012", guide_add=["012 owns the single receipt-validity function; 018 extends it and never adds a second one."])
op(["014", "015"], checks_add=[sk("artifact_concision_self_test.py"), sk("progress_runner_self_test.py"), sk("pattern_runner_self_test.py"), sk("self_test.py")])
op("014",
   sub={"S004": (None, "Measure stale-learning errors and context bytes offline; live task-success measurement without owner authorization is a recorded limitation; cache reuse is an observed metric, not a structural assertion.")},
   acc_replace=[("Byte-stable prefixes and bounded task suffixes survive different task IDs and prior failure lengths.",
                 "Prefix stability is owned by 028; 014 changes do not regress the existing byte-stable prefix fixtures.")])
op("016",
   deps_add=["019"],
   acc_replace=[("Two writers using the same starting revision cannot both silently succeed.",
                 "Two writers using the same starting revision or digest cannot both silently succeed or overwrite the registry.")],
   acc_remove=["Two writers with the same starting digest cannot both overwrite the registry."])
op(["018", "019"], checks_add=[sk("watchdogctl_self_test.py"), sk("keepalivectl_self_test.py"), sk("preplan_self_test.py"), sk("task_memory_self_test.py"), sk("self_test.py")])
op("018", sub={"S004": (None, "Extend 012's receipt-validity function with scoped contract/input fingerprints (no second fingerprint); reserve whole-repository fingerprints for integration checks.")})

# ---- 020-035 ------------------------------------------------------------------------
op(["020", "021"], checks_add=[sk("route_selector_self_test.py"), sk("routing_config_self_test.py"), sk("workload_routing_self_test.py"), sk("rollout_gate_self_test.py"), sk("delegation_self_test.py"), sk("progress_runner_self_test.py")])
op("020", acc_add=[A9])
op(["022", "023"], checks_add=[sk("workload_routing_self_test.py"), sk("observer_self_test.py"), sk("watchdogctl_self_test.py")])
op("022",
   sub={"S004": (None, "Include allowed-provider, privacy, workload, snapshot and effective-routing settings, the per-tier chain (tier_routes) and the provider permission/sandbox mode in the availability fingerprint.")},
   acc_add=["Credit exhaustion is a long-lived quota-scope observation with reset/expiry, not a 300-second retry loop, and never a functional or capability failure.",
            "With one provider's credits exhausted the chain continues Antigravity > Codex > Claude for implementation and Codex > Claude for review."])
op(["024", "025"], checks_add=[sk("configure_self_test.py"), sk("availability_self_test.py"), sk("observer_self_test.py"), sk("routing_config_self_test.py"), sk("model_routing_self_test.py"), sk("route_selector_self_test.py")])
op("024",
   acc_replace=[("Frontend evaluation detects broken keyboard navigation even when screenshots match.",
                 "Routing evidence marks a frontend task whose keyboard check fails as failed even when screenshots match; the browser harness belongs to 125.")],
   acc_add=["Ties resolve Antigravity > Codex > Claude for implementation/repair and Codex > Claude for architecture/review.",
            "Fable 5.2, Astra 6.2 and gemini-4-carbon-* never appear in implementation, repair or monitoring routes.",
            A10])
op("025", ti={"research_sha256": "e2747d6c96173285b1d6d2ee50d71aa87756c7188934722d5e46843134022ddc"})
op(["026", "027"], checks_add=[sk("model_catalog_self_test.py"), sk("model_routing_self_test.py"), sk("route_selector_self_test.py")])
op("026",
   acc_replace=[("Legacy config snapshots do not inherit a newly enabled global switch policy.",
                 "An existing plan's catalog snapshot binding is unchanged when a newer catalog snapshot or policy version is published; config-snapshot inheritance is owned by 070.")],
   acc_add=[A10])
op("027", ti={"research_sha256": "bfd027f508680eb995590ab784296a652fad0a69ab3fb97fa80f7fa305f7dcb2"})
op(["028", "029"], checks_add=[sk("self_test.py"), sk("delegation_self_test.py"), sk("progress_runner_self_test.py")])
op("028",
   sub={"S002": (None, "Define the delegate-vs-single-qualified-model comparison as a fixture-backed decision record (cost fields, unknowns null) handed to 064; no live run (G002).")},
   acc_add=["With an uncommitted tracked change in the parent checkout and no commit authorization, in-place execution preserves it; isolated-worktree mode carries the declared uncommitted inputs or refuses with a reason, never starting from HEAD."])
CLAUDE_CODEX_CHECKS = [sk("self_test.py"), sk("failure_evidence_self_test.py"), sk("snapshot_runner_self_test.py"), sk("model_routing_self_test.py"), sk("route_selector_self_test.py")]
op(["030", "031", "032", "033"], checks_add=CLAUDE_CODEX_CHECKS)
op("030",
   acc_add=["A model whose minimum Claude Code version is unmet (fixture claude-fable-5-2 on 2.1.283 -> HTTP 400) is a version/environment block skipped before dispatch, never a semantic failure or effort escalation.",
            "An alias whose resolved backend differs from the requested id (fable -> 5.1, haiku -> Haiku 4.5 without effort) is recorded with requested and resolved ids.",
            A10])
op("032",
   deps_add=["009"],
   sub={"S004": (None, "Remove universal no-cache-write-cost assumptions from planned economics, including the PRIMARY_PLANNING.md claim, and use model-versioned reported usage.")},
   acc_replace=[("An unsupported sandbox/effort flag fails preflight instead of falling back to unrestricted execution.",
                 "Read-only roles (review, summary, observer) fail preflight rather than widen authority; authorized implementers get the configured mode (including full access, owned by 093) verbatim, never downgraded or upgraded.")],
   acc_add=["Routing never emits ultra effort; credits-exhausted/quota is availability with cooldown and consumes no semantic attempt.",
            A10])
op(["032", "033"], write_add=[REF + "PRIMARY_PLANNING.md"])
op("033", guide_add=["Dispatch the max reviewer on Codex (Sol 6.2 xhigh), then Claude (Opus 5.5 xhigh); record Codex as skipped for availability when its credits are exhausted."])
op(["034", "035"], checks_add=[sk("routing_config_self_test.py"), sk("self_test.py"), sk("failure_evidence_self_test.py"), sk("snapshot_runner_self_test.py"), sk("model_routing_self_test.py"), sk("route_selector_self_test.py")])
op("034", acc_add=["Antigravity Claude 4.6 ids (removed 2026-11-18) and unlisted Carbon variants are skipped as unavailable with a reason.",
                   "agy-flash-monitor stays advisory-only and is disabled in favor of deterministic monitoring when no read-only boundary is proven.",
                   A10])

# ---- 036-067 ------------------------------------------------------------------------
op(rng(36, 43), checks_add=[sk("self_test.py"), sk("failure_evidence_self_test.py"), sk("snapshot_runner_self_test.py")])
op(rng(44, 47), write_add=[SK + "workload_routing.py"],
   checks_add=[sk("routing_config_self_test.py"), sk("self_test.py"), sk("failure_evidence_self_test.py"), sk("snapshot_runner_self_test.py")])
COOLDOWN = ("cooldown_key/cooldown_keys include the provider profile/backend, so quota exhaustion of that backend never "
            "cools down native Claude/Codex routes; legacy no-profile keys stay valid.")
op(["044", "046"], acc_add=[COOLDOWN])
op(["048", "049"], checks_add=[sk("artifact_concision_self_test.py"), sk("progress_runner_self_test.py"), sk("self_test.py")])
op("048", deps_add=["047"])
op(["050", "051"], checks_add=[sk("progress_watch_self_test.py"), sk("validatectl_self_test.py"), sk("jobctl_self_test.py"), sk("failure_evidence_self_test.py")])
op("050",
   sub={"S005": (None, "Run the declared regression commands and every assigned acceptance counterexample, plus run_task_checks.py --task 050 directly because resource_watch.py is under change. Preserve logs, hashes, failures and limits.")},
   acc_add=["Existing schema_version 1 maps (.ai-work/SERVICE_MAP.md, sha256-path-content-v2-streamed) stay valid; new readiness/health fields are optional."])
op(["052", "053"], checks_add=[sk("progress_runner_self_test.py"), sk("snapshot_runner_self_test.py")])
op(["054", "055"], checks_add=[sk("progress_runner_self_test.py"), sk("failure_evidence_self_test.py")],
   guide_add=["Stale-success rejection and validation-only resume call 048's receipt/generation binding in runner_contract.py/artifact_contract.py; no second digest in jobctl.py."])
op("054", acc_add=["A receipt that 048's binding invalidates is rejected by jobctl with the same reason."])
op(["058", "059"], checks_add=[sk("progress_watch_self_test.py"), sk("validatectl_self_test.py"), sk("jobctl_self_test.py")])
op("062", deps_set=["001", "051", "055", "061"])
op(["062", "063"], checks_add=[sk("validatectl_self_test.py"), sk("companion_self_test.py"), ["node", "--test", "test/companion.test.js"]],
   write_remove=[SK + "companion_validation_self_test.py"], new_remove=[SK + "companion_validation_self_test.py"],
   inputs_remove=[SK + "companion_validation_self_test.py"])
op(["064", "065"], checks_add=[py("tools/routing_eval_self_test.py"), py("tools/routing_eval_predeclaration_self_test.py"), py("tools/skill_benchmark_self_test.py"), py("tools/routing_eval.py", "validate-predeclaration")])
op("064", acc_add=["If docs/research/routing-eval/measurements.jsonl exists, thresholds.json stays byte-identical; otherwise any edit updates predeclared_on and the regenerated SHADOW_REPORT digest."])
op("066", acc_add=["Temporary installs use an isolated npm prefix and HOME/USERPROFILE/APPDATA; hashes of the real installed skill dirs and %APPDATA%/plan-and-execute/orchestrator.config.json are identical before and after."])
op(["066", "067"], guide_add=["Edit package-lock.json only with npm install --package-lock-only --ignore-scripts after owner confirmation; no npm publish, no -g install; npm pack only with --dry-run or --pack-destination <tmp>."])

# ---- 068-081 provider switching ------------------------------------------------------
op(["068", "069"], write_add=["test/optimization/provider_switch_cases.json"])
op("068", new_add=["test/optimization/provider_switch_cases.json"],
   acc_add=["Each case in test/optimization/provider_switch_cases.json names its owner task (070-080).",
            "New fixtures cover the antigravity/codex/claude implementation chain and the codex/claude review chain.",
            "Codex out of credits is availability: no functional failure and no escalation.",
            "claude-fable-5-2, gpt-6.2-astra and gemini-4-carbon-* are never useful rungs.",
            "A03: in map v8 Claude strong and max are both claude-opus-5-5; a no-op is counted only when model and effort are equal."])
op("069", guide_add=["Also review 068's policy fixtures (provider chains, credit exhaustion, frontier and Carbon exclusions, A03 no-op rule)."])
op(["070", "071", "072", "073", "074", "075", "076", "077", "078", "079", "080", "081"],
   checks_add=[py("test/optimization/provider_switch_handoff_self_test.py")])
op("070",
   acc_remove=["Strictly validate provider_switch.mode and handoff subkeys; default legacy mode keeps previous behavior.",
               "Fingerprint every route-affecting option; full version1 config snapshots do not inherit new global settings."],
   acc_add=["A05: the third provider of a strong chain is reachable at max_attempts=8, or a documented budget rule rejects the case.",
            "A06: ladder and dispatch use one chain derived from tier_routes when present, else provider_order."])
op(["070", "071"], checks_add=[sk("configure_self_test.py")])
op("071", acc_add=["A reused or fabricated review receipt is rejected."])
op("072", acc_add=["A01: legacy-mode argv goldens are unchanged.",
                   "A02: a useful top on provider 1 moves the next attempt to provider 2.",
                   "A07: a missing tier lifts upward or skips the provider with a reason, never lowering the floor.",
                   "Schema 1-4 manifests without provider/phase state load and resume with legacy counters.",
                   A9])
op(["072", "073"], checks_add=[sk("self_test.py"), sk("lifecycle_self_test.py"), sk("snapshot_runner_self_test.py")])
op(["074", "075"], checks_add=[sk("workload_routing_self_test.py"), sk("provider_self_test.py")], acc_add=[A9])
op("074", acc_add=["After max fails on every eligible provider, frontier is offered only for review/architecture through task 105's approval and never after quota/auth/environment outcomes; the legacy-mode ladder is unchanged."])
op(["076", "077"], checks_add=[sk("assistant_triage_self_test.py"), sk("provider_self_test.py")])
op(["078", "079"], checks_add=[sk("pattern_runner_self_test.py"), sk("telemetry_self_test.py")])
op("079", title="Review and correct attempt-bound handoff in both worker prompts")
op(["080", "081"], checks_add=[sk("model_routing_self_test.py"), sk("routing_config_self_test.py")],
   guide_add=["Preserve the 2026-11-20 owner-preference section of MODEL_ROUTING.md; keep model facts consistent with MODEL_REFRESH_20261120.md (Fable/Astra above the tier map; bare haiku is Haiku 4.5 without effort; Codex ultra never routed)."])

# ---- 082 integration ----------------------------------------------------------------
op("082",
   deps_add=["112"],
   guide_set=[
       "Read docs/research/20261028-skill-optimization/prepared-research/ARCHITECTURE_AND_SCOPE.md and docs/plans/20261028-skill-optimization/IMPLEMENTATION_INTEGRATION.md.",
       "Use only task 082 inputs, declared checks and write scope in TASK_INPUTS.json; write evidence to docs/research/20261028-skill-optimization/implementation/082-receipt.json.",
       "Implement the assigned recommendations, preserving already-satisfied invariants with regression tests rather than duplicate code.",
       "If integration exposes a defect outside this write scope, reopen its owning TODO and correction review with native controllers; do not silently expand scope.",
       # Both sentences are study.json validation implications that studyctl requires verbatim in some task.
       "Keep historical receipt integrity separate from current source/command/map validation. Every changed implementation and correction gate needs actual acceptance evidence; prepared research never counts as a pass.",
       "Integrate all six feature pairs from docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261031.md; require actual independent review receipts.",
       "Integrate verified P053 101/102 host sleep guard and tests across providers, OS backends, WSL, long validation and strict preflight.",
       "Integrate P054 timer cleanup and P055 L6 model routing after genuine independent reviews 104/106.",
       "Require genuine 112 impact-selection and 114 audit/refactor reviews; mapped source-specific suites gate tasks and the full global suite runs at the final plan revision, again after later fixes.",
       "Integrate independently reviewed 115-120 quota restoration/resume, oracle-strength tests and every-task lazy routing without losing global final suite.",
       "Integrate actual independently reviewed P065 tasks 121-126, source-of-truth design memory, optional prototype lab and accessible UX validation without lost final-suite gate.",
       "P066: integrate reviewed 128/130 standards and 121's shared first-use UX state; validate ORM/JDBC drift and justified exceptions; document CLI in README.md, README.pt-BR.md and --help only after implementation.",
   ],
   acc_add=["tools/run-repo-checks.js runs every test/optimization/*_self_test.py from tasks 068-130, and integration_082_self_test.py proves it."])

# ---- 087-100 ------------------------------------------------------------------------
op("087", deps_add=["081"],
   sub={"S003": (None, "Extend PRIMARY_SIGNALS/minimum_route in routingctl.py with a DIRECT staged handoff (no parallel router); delegate high-risk architecture to a qualified stronger tier with durable design.")},
   guide_add=["Architecture stage Codex > Claude (Sol 6.2 / Opus 5.5 high/xhigh); implementation stage Antigravity > Codex > Claude; unavailable providers are skipped without lowering the floor; frontier never serves DIRECT implementation."])
op(["087", "088"], write_remove=[SK + "direct_route.py"], new_remove=[SK + "direct_route.py"], write_add=[SK + "routingctl.py"],
   checks_add=[sk("workload_routing_self_test.py"), sk("validatectl_self_test.py")])
op("089", deps_add=["088"],
   sub={"S004": (None, "Measure false activation, missed activation and prompt bytes on deterministic eval fixtures; live host traces only with explicit owner confirmation (G002); do not add a paid classifier.")},
   acc_replace=[("Held-out host evaluations measure false positives/negatives and token impact, not keyword assertions alone.",
                 "Deterministic positive/negative eval fixtures pass; live host traces run only with explicit owner confirmation (G002), and unavailable/no-quota hosts are recorded not_verified, not passed.")])
op(["089", "090"], checks_add=[VALIDATE_SKILL, sk("token_efficiency_self_test.py")])
op("091", deps_add=["090", "073"],
   acc_add=["Failures that availability classifies as quota/auth/environment never create repair tasks."])
op(["091", "092"], checks_remove=[ROUTING], checks_add=[sk("lifecycle_self_test.py"), sk("self_test.py"), sk("failure_evidence_self_test.py")])
op("093", deps_add=["092", "073"],
   sub={"S002": (None, "Treat the owner's user-global config as the authorization record: when it grants full access, Codex and Antigravity implementation workers run full-access without sandbox; the skill never writes that config; the built-in default stays conservative."),
        "S003": (None, "Replace the Codex worker default --sandbox workspace-write (build_worker_command codex branch) with the configured mode and a version-verified flag; keep Antigravity skip_permissions; reviewers/observers inherit no write access.")},
   acc_add=["A provider that cannot be probed (Codex credits exhausted) records effective_access: not_verified(quota)."])
op(["093", "094"], checks_add=[sk("provider_self_test.py"), sk("configure_self_test.py")])
op("095", deps_add=["094", "073"],
   sub={"S003": (None, "Classify ready, needs_config, needs_login, unsupported and unknown without exposing secrets; add a read-only availability field from the availability.py ledger.")},
   acc_add=["A logged-in provider with exhausted quota/credits is not prompted to log in, not marked unsupported, and is skipped by routing until its cooldown ends."])
op(["095", "096"], checks_add=[sk("preplan_self_test.py"), sk("configure_self_test.py"), sk("model_catalogctl_self_test.py")])
op("097", deps_add=["096", "073"],
   sub={"S005": (None, "Measure output tokens and repeated-text rate with accuracy, necessary caveats, actionability and accessibility on paired old/new scenarios; human comprehension is not_verified without consented user evidence.")},
   acc_replace=[("Independent test and human feedback verify non-inferior comprehension, accuracy and completeness, not word count alone.",
                 "Automated paired old/new scenarios show accuracy and completeness no worse; human comprehension is not_verified unless consented user evidence exists.")],
   new_add=[REF + "USER_COMMUNICATION.md", SK + "process_io.py"])
op(["097", "098"], dedupe_write=True, checks_remove=[ROUTING],
   checks_add=[sk("artifact_concision_self_test.py"), sk("token_efficiency_self_test.py")])
op("099", deps_add=["094", "096", "098"],
   acc_add=["A confirmed stall raises effort first on the same eligible route, then the next tier up to max; frontier is never chosen for implementation repair.",
            A9])
op("100", acc_add=["Verify: A confirmed stall raises effort first on the same eligible route, then the next tier up to max; frontier is never chosen for implementation repair."])
op(["099", "100"], checks_add=[sk("progress_watch_self_test.py"), sk("jobctl_self_test.py")])

# ---- 101-106 ------------------------------------------------------------------------
op("101", acc_add=[
    "A detached jobctl supervisor holds its own job-scoped OS request until the job exits; runner death during supervised validation leaves no sleep gap.",
    "Each sleep request is released only by its owner.",
    "On Windows the request is held on a dedicated thread in the long-lived runner (run_concise), not in a helper that exits.",
    "A keepalive relaunch acquires a fresh request before dispatching."])
op("102", ti={"kind": "review"})
KEEPALIVE_CHECKS = [sk("keepalivectl_self_test.py"), sk("watchdogctl_self_test.py"), sk("lifecycle_self_test.py")]
op("103",
   why="Scheduler adapters, the keepalive CLI and lifecycle cleanup share one plan-scoped ownership invariant and one test boundary.",
   subs_set=[
       ("S001", "Extend keepalivectl and isolate OS adapters", "Extend keepalivectl.py (check/pause/resume/schedule, --yes, RESTART states, lock, --max-restarts); move OS adapters (schtasks XML, systemd-user, launchd, cron) into keepalive_schedule.py imported only by keepalivectl; one CLI, one XML source."),
       ("S002", "Offer scheduling once at the threshold", "Offer scheduling exactly once for >=6 pending executable TODOs; consent stored plan-scoped, non-interactive default no, never prompt DIRECT."),
       ("S003", "Register exact per-plan scheduler entries", "Register an exact per-plan host-scheduler entry (Windows Task Scheduler, Linux user systemd timer with safe cron fallback, macOS launchd where permitted) with unique ownership, no privilege escalation."),
       ("S004", "Resume only dead runnable work per tick", "At each twenty-minute tick check runner lease and actual runnable state; only resume dead/awaiting/cooldown-due, never restart live, silent, blocked, permission-pending or validation-active work."),
       ("S005", "Unregister and self-clean without power changes", "Unregister on success, cancel, reset or opt-out, plus safe self-clean on next tick if a plan vanished; release nothing power-related (101's finalizer still runs; power_inhibit.py is out of scope)."),
       ("S006", "Validate boundaries, concurrency and cleanup", "Validate all threshold boundaries, multi-plan concurrency, restart budget, OS mocks, crash and termination cleanup; real CI evidence only."),
   ],
   acc_set=[
       "Plans with 0–5 pending executable tasks are not offered timer, 6+ are offered once; opt-in only; count review tasks where actually executable.",
       "Twenty-minute scheduled checks are deterministic and use no model tokens when healthy; no automatic session chat wake claims.",
       "Dead runnable runner is restarted at most once per tick with lock/lease and restart-loop budget; no restart of live/silent/blocked/quota-not-due runner.",
       "Native Windows Task Scheduler, Linux systemd-user timer (safe cron fallback), and macOS launchd conditional adapters install/remove only their plan-scoped jobs without modifying unrelated jobs.",
       "Terminal success/cancel/reset removes OS timer and owned metadata before plan control cleanup; missing plan next tick triggers safe self-removal; multiple plans isolated.",
       "When WSL, sandbox, guest VM or host limitations prevent reliable host scheduling, report unsupported instead of claiming wake capability.",
       "Sleep inhibition remains separate, continuous lease owned by task 101; no timer-powered wake guarantee, no global power settings or synthetic input.",
       "Mocked OS tests and real available platform smoke checks; independently reviewed task 104 required before integration 082.",
       "check --plan <missing> from the scheduled task deletes only PlanAndExecuteKeepalive-<plan_key> after confirming the plan directory is gone (not merely unreadable or unmounted) and exits 0.",
       "The Windows task stays InteractiveToken/LeastPrivilege without WakeToRun, and docs state that it runs only while the user is logged on.",
       "A runner launched by a tick survives the end of the scheduled action.",
   ])
op(["103", "104"], checks_remove=[ROUTING], checks_add=KEEPALIVE_CHECKS)
op("104",
   why="One reviewer context holds the final 103 diff, scheduler tests and ownership invariants needed to judge and correct them together.",
   write_add=[SK + "run_concise.py", REF + "INSTALLATION.md", REF + "INSTALLATION.pt-BR.md"],
   subs_set=[
       ("S001", "Read final 103 evidence", "Read fresh implementation receipt, task 103 source, exact hashes, OS test outputs and design P054."),
       ("S002", "Dispatch qualified independent review", "Dispatch qualified independent review, record actual model/effort/inputs; verify thresholds, concurrent plans, Windows/Linux/macOS and unsupported environments."),
       ("S003", "Correct critical/high problems and rerun", "Correct all critical/high problems and rerun lifecycle/recovery regressions; preserve strict no-duplicate-runner and no-credit-when-healthy invariants."),
       ("S004", "Record real review receipt and limits", "Record real review receipt and unresolved native physical-host limitations; never invent execution."),
   ],
   acc_set=[
       "Actual independent fresh reviewer evidence and hashes, with all high/critical defects corrected.",
       "OS timer lifecycle and missing-plan self-removal tested under concurrent plans and hostile path/symlink conditions.",
       "No active worker/validation terminated or relaunched; power inhibitor remains separately lifetime-scoped.",
       "Threshold 5/6 boundary, 20-minute trigger and no healthy model calls verified.",
       "Windows/Linux/macOS mocks and available native checks pass, or task remains pending.",
   ])
FRONTIER_CHECKS = [sk("model_routing_self_test.py"), sk("route_selector_self_test.py"), sk("model_catalog_self_test.py"), sk("model_catalogctl_self_test.py"),
                   sk("workload_routing_self_test.py"), sk("routing_config_self_test.py"), sk("availability_self_test.py"), sk("model_matrix_self_test.py"), sk("self_test.py")]
op("105",
   title="Add the opt-in frontier tier L6/F6 on top of map 2026-11-20-v8",
   objective="Add an opt-in frontier tier (aliases L6/F6) above max for architecture and code review only, outside TIER_ORDER, without changing the v8 map, routes or argv while it is disabled.",
   scope_in=["Add the opt-in frontier tier L6/F6 on top of map 2026-11-20-v8"],
   why="Frontier constants, the ladder_exhausted gate and every rejection path share one routing invariant that must be implemented and tested together.",
   deps_add=["100"],
   subs_set=[
       ("S001", "Read the 2026-11-20 refresh and pin its baseline", "Read docs/research/MODEL_REFRESH_20261120.md (it overrides prepared report 105 on conflict; report 105 stays hash-pinned and unedited); record a baseline hash of the uncommitted refresh files so 106 can separate the 105 diff."),
       ("S002", "Keep the v8 refresh byte-identical", "Do not redo the refresh: CURRENT_MODELS, ESCALATION_LADDERS, MODEL_MAP_VERSION=2026-11-20-v8, bootstrap catalog and Gemini 4 preset stay byte-identical while L6 is off. Verify only observed ids: claude-fable-5-2, gpt-6.2-astra; Carbon is not listed."),
       ("S003", "Add FRONTIER_TIER outside TIER_ORDER", "Add FRONTIER_TIER='frontier' (aliases l6/f6) outside TIER_ORDER plus an opt-in FRONTIER_MODELS with its own version, so apply_current_models, lift_tier, provider_ladder, selector min(eligible), the stagnation floor and planctl.VALID_TIERS never reach it."),
       ("S004", "Define frontier candidates, roles and order", "Candidates: claude-fable-5-2 (high; xhigh only where measured), gpt-6.2-astra (high/xhigh, never ultra), gemini-4-carbon-* only if agy models lists it. Roles: architecture, code_review. Order Codex > Claude > Antigravity; Codex credit exhaustion skips to Fable."),
       ("S005", "Gate entry at ladder_exhausted with approval", "Offer frontier only at the ladder_exhausted event (run_isolated.py) with a recorded task-scoped approval after >=2 semantic/plan_defect failures at the max/xhigh rung; environmental, budget, timeout_ceiling, quota and unknown never count."),
       ("S006", "Benchmark only after owner confirmation", "Run benchmarks only after owner confirmation; Astra stays unmeasured; cite the secondary replay in MODEL_REFRESH_20261120.md and record cost/quality unknowns honestly."),
   ],
   guide_set=[
       "Read docs/research/MODEL_REFRESH_20261120.md first; docs/research/20261028-skill-optimization/prepared-research/105-frontier-model-routing-20261112.md is background and loses on conflict.",
       "Version floors: claude-fable-5-2 needs Claude Code >= 2.1.290; gpt-6.2-astra needs Codex >= 0.171.0; gemini-4-carbon-* is Ultra/Enterprise only and is not listed on this account.",
       "No PRIMARY_SIGNALS entry maps to frontier; frontier_long_horizon stays ('max','high'); Codex credit exhaustion is availability (skip to Fable, record no escalation).",
       "Touch run_isolated.py only in its ladder_exhausted/route-resolution branch; keep the ESCALATION_LADDERS comment saying frontier needs this task's explicit approval.",
       "Use only task 105 inputs, checks and write scope in TASK_INPUTS.json; record actual receipts/outcomes and leave the task pending until verified.",
   ],
   acc_set=[
       "The 2026-11-20 sources and the observed CLI ids (claude-fable-5-2, gpt-6.2-astra; no gemini-4-carbon-*) are recorded in the receipt.",
       "When every max candidate is unavailable the selector returns no_candidate, never frontier.",
       "A config escalation_ladder containing frontier or l6 is rejected.",
       "A plan spec with model_tier: frontier is rejected.",
       "A frontier route for workload implementation is rejected.",
       "With L6 disabled, routes, argv and the v8 map hash are identical to the recorded baseline.",
       A9,
   ])
op(["105", "106"], write_add=[REF + "MODEL_ROUTING_CLAUDE.md", REF + "MODEL_ROUTING_CODEX.md", SK + "run_isolated.py"],
   inputs_add=["docs/research/MODEL_REFRESH_20261120.md"], checks_add=FRONTIER_CHECKS)
op("106",
   why="One reviewer context holds the 105 diff, the pinned v8 baseline and every negative case needed to approve or correct it.",
   subs_set=[
       ("S001", "Read the 105 diff and evidence", "Read task 105 actual diff, receipts, source hashes and official vendor evidence; do not trust proposed model IDs without an installed CLI check."),
       ("S002", "Run an independent max-qualified review", "Use a genuinely independent max-qualified reviewer; audit providers, catalog freshness, tier monotonicity, the frontier gate, subscription budgets and previous compatibility."),
       ("S003", "Correct findings and rerun", "Correct invalid IDs, unsupported effort flags, default frontier promotions, cost-accounting errors and any critical/high findings; rerun tests and record genuine independent review."),
   ],
   acc_set=[
       "Real independent review and source hashes captured; unresolved critical/high issues block integration.",
       "The 105 diff is verified against the pinned refresh baseline hash; files outside the 105 scope are unchanged.",
       "Every S003/S005 negative case is re-run: lift, ladder, selector, stagnation floor, planctl tiers, quota, implementation role, and Codex credit exhaustion -> Fable with no escalation.",
       "Legacy L1–L5 routes and old persisted configuration stable; L6 enabled paths select only exact observed compatible models.",
       "No unapproved paid API fallback or model tier escalation on environment, timeout, quota or weak evidence.",
   ])

# ---- 107-120 ------------------------------------------------------------------------
op("107",
   acc_add=["The design reviewer is read-only through the adapter-pinned read-only argv (fail-closed table in run_isolated.py) plus a before/after worktree fingerprint; provider sandbox/skip_permissions settings never reach it.",
            "The reviewer route follows Codex > Claude at strong/max; frontier only through task 105's approval."],
   guide_add=["If direct_route.py is absent, use the DIRECT entry point named in the 087 receipt."])
op(["107", "108"], checks_remove=[sk("planctl.py") + ["--help"]], checks_add=[sk("self_test.py")])
G109_OLD = "Read `docs/research/20261028-skill-optimization/prepared-research/109-batched-test-failure-triage.md` and `docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261114_TEST_FAILURE_BATCH.md` before code; inspect source exactly, don't infer newer features are already implemented."
G109_NEW = ["Read docs/research/20261028-skill-optimization/prepared-research/109-batched-test-failure-triage.md and docs/plans/20261028-skill-optimization/REQUEST_EXTENSION_20261114_TEST_FAILURE_BATCH.md before code.",
            "Inspect source exactly; do not infer that newer features are already implemented."]
RTC = "Edits to support/run_task_checks.py stay fail-closed (nonzero if any declared check fails or did not run); record its hash in changed_artifacts and in 110's reviewed_inputs (code_fingerprint does not cover docs/)."
op("109", guide_replace=[(G109_OLD, G109_NEW)],
   guide_add=["Use reviewed 111 impact-selected task tests; after focused fixes rerun all required mapped task suites; the global all-project suite runs at plan closure 082/084 or earlier when risk, unknown graph or CI requires.", RTC])
op("110", guide_replace=[(G109_OLD, G109_NEW)],
   guide_add=["Review the distinction between complete task-mapped reruns and final global full-suite regression; unknown/zero impact selection and focused-only green never satisfy acceptance.", RTC])
op(["109", "110"], checks_add=[sk("self_test.py"), sk("progress_runner_self_test.py"), sk("failure_evidence_self_test.py")])
op(["111", "112"], checks_remove=[RELIABILITY], checks_add=[sk("self_test.py"), sk("progress_runner_self_test.py"), sk("validatectl_self_test.py")])
op("111",
   guide_add=["Expose a selection contract (exact argv, reasons, source/map fingerprint) for 109 to consume later; do not import or assume test_failure_cycle.py."],
   acc_replace=[("Resource watcher, P057 failure collection, cancellation, bounded worker context and true nonzero exits remain intact.",
                 "Resource watcher, cancellation, bounded worker context and true nonzero exits remain intact.")])
op("112", sub={"S002": ("Dispatch a fresh max-qualified review", "Dispatch a fresh max-qualified reviewer pinning the final 111 source, test and receipt hashes; record provider, model, effort and dispatch evidence."),
               "S003": ("Audit routing, validation wiring and context", "Audit routing, validation wiring and context boundaries of the final 111 code against the selection contract."),
               "S004": ("Correct critical/high defects and rerun checks", "Correct only critical/high defects, rerun functional, adversarial and negative checks and obtain approval on the final hashes.")})
op("113", acc_add=[
    "node tools/validate-skill.js passes.",
    "SKILL.md stays <= 7167 normalized characters (baseline 6826 x 1.05) with at most one lazy pointer line.",
    "TOKEN_EFFICIENCY.md stays <= 10000 characters (currently 9975); 113 detail lives in TEST_REVIEW_REFACTOR.md.",
    "The orchestrator enforces audit-only and ownership limits: test files are hashed before/after and any change outside the authorized case set is rolled back and rejected.",
    "A fixture where a full-access unsandboxed worker writes outside the authorized case set anyway is rolled back and rejected."])
op(["113", "114"], checks_add=[VALIDATE_SKILL])
op("115", deps_set=["023", "055", "075", "100", "104", "106"],
   guide_add=["Provider preference is per phase: implementation Antigravity > Codex > Claude; architecture and review Codex > Claude; re-rank only before a new safe dispatch."],
   acc_add=["credits exhausted/depleted (matched by the availability.py quota regex) is class credits_exhausted: reset unknown, never paid-probed, restored only on an observed non-paid signal or operator action, never escalated to frontier.",
            "Fixture: with Codex exhausted, implementation goes to Antigravity and review to Claude Opus 5.5.",
            "Fixture: when Codex returns, only the next eligible dispatch goes back to Codex."])
op("116", guide_add=["Probe credits_exhausted classification, Codex-exhausted rerouting (implementation -> Antigravity, review -> Claude Opus 5.5) and return to Codex on the next eligible dispatch only."],
   acc_add=["Verified: credits_exhausted classification and the Codex exhausted/returned rerouting fixtures pass on the final 115 code."])
op(["115", "116"], checks_remove=[RELIABILITY], checks_add=[sk("availability_self_test.py"), sk("keepalivectl_self_test.py")])
op("117", deps_set=["110", "112", "108", "114"])
op(["117", "118"], checks_remove=[RELIABILITY], checks_add=[sk("context_self_test.py")])
op("119", deps_add=["114"],
   guide_replace=[("Gate all 120 active TODOs plus future ones; stale evidence, unsafe scope, secrets and unknown dependency broaden with justification.",
                   ["Gate every manifest task (currently 130) plus future ones, never hard-coding a count; stale evidence, unsafe scope, secrets and unknown dependency broaden with justification."])],
   acc_add=["Negative case: the context packet never selects the frontier tier or overrides the phase provider chain; routingctl stays the only route source."])
op("120",
   guide_replace=[("Probe all 120 current tasks and future task, cache unknown, changed source, stale contracts and prompt leaks.",
                   ["Probe every manifest task (currently 130) plus a future task, never hard-coding a count; cache unknown, changed source, stale contracts and prompt leaks."])],
   acc_replace=[("Verified: Probe all 120 current tasks and future task, cache unknown, changed source, stale contracts and prompt leaks.",
                 "Verified: Probe every manifest task (currently 130) plus a future task without a hard-coded count; cache unknown, changed source, stale contracts and prompt leaks.")])
op(["119", "120"], checks_remove=[RELIABILITY], checks_add=[sk("token_efficiency_self_test.py"), sk("routing_self_test.py")])

# ---- 121-126 UX ---------------------------------------------------------------------
R121_OLD = "Read assigned P065 architectural report and current affected symbols; verify accepted 025/120 prior receipts only."
R121_NEW = "Read assigned P065 architectural report and current affected symbols; verify accepted 025/120/128 receipts only (shared consent comes from 127)."
UX_NEG = "Cross-check applicable negative cases A–P and provenance in P065 research; screenshot matching never overrides keyboard/functional failures; an unsupported tool is not a green run."
op("121",
   sub={"S001": (None, R121_NEW)},
   guide_replace=[(R121_OLD, [R121_NEW])],
   guide_add=["Shared first-use decision/state is implemented by 127 and reviewed by 128; do not build a second UX consent controller."],
   acc_add=["UX init/refresh, first-use consent and no repeated research are verified by spies in tests; no backend-only overhead or silent paid calls.",
            "node tools/validate-skill.js passes and SKILL.md stays <= 7167 normalized characters with at most one lazy pointer line."])
op(rng(121, 126), guide_add=[UX_NEG])
op(["121", "123"], checks_remove=[STRUCTURE], checks_add=[VALIDATE_SKILL])
S123_OLD = "Build versioned local scaffold template with pinned dependency lockfile, localhost-only dev and sanitized mock data, generated tokens, no production credentials or remote assets."
S123_NEW = "Build a versioned scaffold template with exact-version pins in package.json and no shipped lockfile (created only in the target project by npm install after explicit confirmation, G002); localhost-only dev, sanitized mocks, no remote assets."
S123_GUIDE = "Template package.json uses exact-version pins and ships no lockfile; the lockfile is created only in the target project by npm install after explicit user confirmation (G002); localhost-only dev, sanitized mocks."
op("123", sub={"S003": (None, S123_NEW)}, guide_replace=[(S123_OLD, [S123_GUIDE])],
   acc_add=["No install runs in the skill repo or its tests; lab setup without install confirmation reports an honest skip."])
op("124", acc_add=["Probes confirm no npm install or network access without confirmation and no lockfile or node_modules in the template."])

# ---- 127-130 coding standards ---------------------------------------------------------
STD_VALID = lambda tid: [f"python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_TESTS_{tid}",
                         f"python skill/plan-and-execute/scripts/resource_watch.py run --repo-root . --map .ai-work/SERVICE_MAP.md --validation P1_{tid}"]
for _tid in ("127", "128", "129", "130"):
    op(_tid, validation_set=STD_VALID(_tid))
op("127",
   why="Consent state, discovery, generated standards docs and the CLI share one onboarding contract and one test boundary.",
   subs_set=[
       ("S001", "Inspect P066 and live source", "Inspect only P066 and the relevant live source, 025/120 evidence and test baselines."),
       ("S002", "Implement persisted first-use consent", "Implement persisted per-project, per-topic standards/UX first-use consent with noninteractive fallback, secure scope, worktrees and atomic state."),
       ("S003", "Run approved init/refresh discovery only", "Perform approved init/refresh only: deterministic module/libraries/usage/representative patterns/ORM/helpers discovery; optional contemporary source study; no recurring full research."),
       ("S004", "Generate compact source-hashed standards docs", "Generate compact source-hashed docs/ai-standards/ AGENT_INDEX.md, manifests, TECH_STACK.md, ARCHITECTURE.md, CODING_RULES.md, REUSE_CATALOG.json, module rules and ADRs; retain inferred vs approved distinction."),
       ("S005", "Implement pae standards and onboarding CLI", "Implement pae standards status/init/refresh/explain/check/export-instructions and pae onboarding status, --json/dry-run, CLI help and EN/PT-BR usage examples; exporting third-party instructions requires approval."),
       ("S006", "Test recognition, consent and security cases", "Test JPA and monorepo recognition, declared-but-unused dependencies, consent persistence, CI/headless zero prompting, stale hash, malicious files, security and no fallback to unwanted study."),
   ],
   acc_set=["P066 cases D, F, G, H-M, O, P, S and T pass with real tests: one-time consent, no repeated UX, discovery, safe exports that never overwrite manual agent files.",
            "No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.",
            "First-use consent, reusable source-backed agent docs, framework-consistent ORM/JDBC/exception detection and UX lazy activation are validated where applicable.",
            "Test/reviewer evidence exists for current code SHA; otherwise task remains pending."])
op("128",
   why="One reviewer context holds the final 127 code, tests and consent invariants needed to judge and correct them together.",
   subs_set=[
       ("S001", "Read final 127 evidence", "Read P066 and only actual final 127 code/tests/receipts and review their SHA hashes."),
       ("S002", "Dispatch a fresh max-qualified review", "Run a genuine separate fresh maximum-qualified reviewer for UX/standards consent safety, source evidence, code quality, performance, privacy and token economy."),
       ("S003", "Run adversarial safety probes", "Adversarial tests for worktree identity, repeat consent, no-TTY CI, secrets, prompt injection, symlinks, stale code, hidden remote calls and overwritten agent files."),
       ("S004", "Fix blockers and record the review", "Fix or reopen owner for blocking defects, rerun focused tests; record genuine reviewer route, source hash and decisions."),
   ],
   acc_set=["A real fresh max-qualified reviewer approves the final 127 source/test/receipt hashes with dispatch provenance.",
            "The S003 adversarial probes pass: worktree identity, repeat consent, no-TTY CI, secrets, prompt injection, symlinks, stale code, hidden remote calls and overwritten agent files.",
            "High/critical findings are fixed and re-reviewed on the final hashes."])
op("129",
   why="Scoped retrieval, drift checks and exception handling share one standards-guard contract verified by one test suite.",
   deps_add=["114"],
   subs_set=[
       ("S001", "Use P066 and accepted evidence", "Use P066 and real accepted 128/108/112/114/120 evidence, without repeating broad research."),
       ("S002", "Implement scoped source-hashed retrieval", "Implement module/intent scoped source-hashed retrieval of approved rules, installed AND used libraries, nearby examples and reusable helpers."),
       ("S003", "Apply architecture preflight and diff review", "Apply architecture preflight and diff reviewer to package/naming, imports, persistence ORM vs JDBC, duplicate helpers and exception handling; inferred rules warn and approved rules gate."),
       ("S004", "Handle approved exceptions and migrations", "Handle approved native SQL/JDBC exceptions, module-specific styles and planned migrations through scoped ADR/waiver and acceptance tests; stale hash triggers targeted invalidation only."),
       ("S005", "Integrate guard evidence with routing and review", "Integrate compact guard evidence with DIRECT/ORCHESTRATED task_context_router and security/performance review; no new paid agent or web calls in ordinary tasks."),
       ("S006", "Test drift, isolation and disabled mode", "Test JPA→JDBC architectural drift, legitimate query, monorepo isolation, malicious input, unreadable tools and disabled-mode/no-index behavior."),
   ],
   acc_set=["P066 cases A-F, N, Q, R and T pass with real tests, including JPA->JDBC drift flagged, an approved JDBC exception passing, and monorepo isolation.",
            "No source, target project or approval boundary overwritten implicitly; malformed input and unavailable tools fail safely.",
            "First-use consent, reusable source-backed agent docs, framework-consistent ORM/JDBC/exception detection and UX lazy activation are validated where applicable.",
            "Test/reviewer evidence exists for current code SHA; otherwise task remains pending."],
   guide_add=["Run after 113/114 on the shared runner files (run_isolated.py, runner_contract.py); rebase on their accepted versions."])
op("130",
   why="One reviewer context holds the final 129 guard code, tests and exception rules needed to judge and correct them together.",
   subs_set=[
       ("S001", "Review final 129 with a fresh max reviewer", "Review P066 and true final 129 source/tests/receipt with fresh maximum-qualified independent model."),
       ("S002", "Probe standards, exceptions and isolation", "Probe approved versus inferred standards, ORM/JDBC exceptions, stale files, monorepo cross-talk, prompt injection, security/performance and context bounds."),
       ("S003", "Correct defects and require final sign-off", "Correct implementation owner defects and rerun tests, require true final SHA independent sign-off."),
       ("S004", "Record honest provider and cost evidence", "Record honest provider/model/effort/real cost or unknown and integration evidence; do not simulate completion."),
   ],
   acc_set=["A real fresh max-qualified reviewer approves the final 129 source/test/receipt hashes with dispatch provenance.",
            "The S002 adversarial probes pass: approved vs inferred standards, ORM/JDBC exceptions, stale files, monorepo cross-talk, prompt injection, security/performance and context bounds.",
            "High/critical findings are fixed and re-reviewed on the final hashes."])

# ---- A2 dependency gates (already in the manifest; projected into the spec) ------------
op("082", deps_add=["128", "130"])
op("121", deps_set=["025", "120", "128"])

# Tasks moved before 082 in the manifest so the whole-skill review stays last.
MOVE_BEFORE_082 = ["127", "128", "129", "130"]


# --------------------------------------------------------------------------------------
class Drift(RuntimeError):
    pass


def norm_argv(a):
    return [str(x) for x in a]


def replace_in_list(items: list[str], old: str, new: list[str], where: str) -> list[str]:
    if old in items:
        i = items.index(old)
        return items[:i] + [n for n in new if n not in items or n == old] + items[i + 1:]
    if all(n in items for n in new):
        return items
    raise Drift(f"{where}: neither old nor new text present: {old[:80]!r}")


def insert_before_receipts(files: list[str], path: str) -> list[str]:
    if path in files:
        return files
    idx = next((i for i, f in enumerate(files) if f.startswith("docs/research/20261028-skill-optimization/implementation/")), len(files))
    return files[:idx] + [path] + files[idx:]


def dedupe(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


def apply_ops(manifest: dict, ti: dict) -> set[str]:
    tasks = {t["id"]: t for t in manifest["tasks"]}
    entries = {e["id"]: e for e in ti["tasks"]}
    acc_touched: set[str] = set()
    for ids, ops in OPS:
        for tid in ids:
            t, e = tasks[tid], entries[tid]
            if "title" in ops:
                t["title"] = ops["title"]
            if "objective" in ops:
                t["objective"] = ops["objective"]
            if "scope_in" in ops:
                t["scope"]["in"] = list(ops["scope_in"])
            if "why" in ops:
                t["context_boundary"]["why_one_todo"] = ops["why"]
            if "validation_set" in ops:
                t["validation_commands"] = list(ops["validation_set"])
            if "deps_set" in ops:
                t["dependencies"] = list(ops["deps_set"])
            for d in ops.get("deps_add", []):
                if d not in t["dependencies"]:
                    t["dependencies"].append(d)
            if "subs_set" in ops:
                old = {s["id"]: s for s in t["subtasks"]}
                new = []
                for sid, title, objective in ops["subs_set"]:
                    base = old.get(sid) or {"id": sid, "title": "", "objective": "", "required": True,
                                            "status": "pending", "started_at": None, "completed_at": None, "history": []}
                    base["title"], base["objective"] = title, objective
                    new.append(base)
                t["subtasks"] = new
            for sid, (title, objective) in ops.get("sub", {}).items():
                s = next(x for x in t["subtasks"] if x["id"] == sid)
                if title is not None:
                    s["title"] = title
                s["objective"] = objective
            if "guide_set" in ops:
                t["implementation_guidance"] = list(ops["guide_set"])
            for old, new in ops.get("guide_replace", []):
                t["implementation_guidance"] = replace_in_list(t["implementation_guidance"], old, new, f"{tid} guidance")
            for g in ops.get("guide_add", []):
                if g not in t["implementation_guidance"]:
                    t["implementation_guidance"].append(g)
            if any(k in ops for k in ("acc_set", "acc_replace", "acc_add", "acc_remove")):
                acc_touched.add(tid)
            if "acc_set" in ops:
                t["acceptance_criteria"] = list(ops["acc_set"])
            for old, new in ops.get("acc_replace", []):
                t["acceptance_criteria"] = replace_in_list(t["acceptance_criteria"], old, [new], f"{tid} acceptance")
            for a in ops.get("acc_remove", []):
                if a in t["acceptance_criteria"]:
                    t["acceptance_criteria"].remove(a)
            for a in ops.get("acc_add", []):
                if a not in t["acceptance_criteria"]:
                    t["acceptance_criteria"].append(a)
            # write scope (TASK_INPUTS write_scope + manifest/spec expected_files)
            for p in ops.get("write_add", []):
                if p not in e["write_scope"]:
                    e["write_scope"].append(p)
                t["scope"]["expected_files"] = insert_before_receipts(t["scope"]["expected_files"], p)
            for p in ops.get("write_remove", []):
                e["write_scope"] = [x for x in e["write_scope"] if x != p]
                t["scope"]["expected_files"] = [x for x in t["scope"]["expected_files"] if x != p]
            if ops.get("dedupe_write"):
                e["write_scope"] = dedupe(e["write_scope"])
                t["scope"]["expected_files"] = dedupe(t["scope"]["expected_files"])
            for p in ops.get("new_add", []):
                if p not in e["planned_new_files"]:
                    e["planned_new_files"].append(p)
            for p in ops.get("new_remove", []):
                e["planned_new_files"] = [x for x in e["planned_new_files"] if x != p]
            for p in ops.get("inputs_remove", []):
                e["inputs"] = [x for x in e["inputs"] if x != p]
                if "input_contract" in e:
                    e["input_contract"] = [x for x in e["input_contract"] if x["path"] != p]
            for p in ops.get("inputs_add", []):
                if p not in e["inputs"]:
                    e["inputs"].append(p)
                if "input_contract" in e and not any(x["path"] == p for x in e["input_contract"]):
                    e["input_contract"].append({"path": p, "availability": "existing_baseline_or_current_file"})
            for argv in ops.get("checks_remove", []):
                e["required_checks"] = [a for a in e["required_checks"] if norm_argv(a) != norm_argv(argv)]
            for argv in ops.get("checks_add", []):
                if norm_argv(argv) not in [norm_argv(a) for a in e["required_checks"]]:
                    e["required_checks"].append(norm_argv(argv))
            for k, v in ops.get("ti", {}).items():
                e[k] = v
    return acc_touched


def finalize_acceptance(manifest: dict, ti: dict, acc_touched: set[str]) -> None:
    tasks = {t["id"]: t for t in manifest["tasks"]}
    entries = {e["id"]: e for e in ti["tasks"]}
    reviewers = [e for e in ti["tasks"] if e.get("requires_independent_review")]
    # A3: every independent review task carries the frontier/reuse line.
    for e in reviewers:
        acc = tasks[e["id"]]["acceptance_criteria"]
        if FRONTIER_REVIEW not in acc:
            acc.append(FRONTIER_REVIEW)
    # Review pair verifies every acceptance addition of its implementation task.
    for e in reviewers:
        impl = e.get("review_of")
        if impl in acc_touched:
            line = review_pair_line(impl)
            acc = tasks[e["id"]]["acceptance_criteria"]
            if line not in acc:
                acc.append(line)
    # Meta evidence lines last; acceptance_ids cover every other criterion by position.
    for t in manifest["tasks"]:
        acc = t["acceptance_criteria"]
        t["acceptance_criteria"] = [a for a in acc if a not in META_LINES] + [a for a in acc if a in META_LINES]
        k = sum(1 for a in t["acceptance_criteria"] if a not in META_LINES)
        entries[t["id"]]["acceptance_ids"] = [f"AC{i:02}" for i in range(1, k + 1)]


def reorder(manifest: dict) -> None:
    tasks = manifest["tasks"]
    moved = [t for t in tasks if t["id"] in MOVE_BEFORE_082]
    rest = [t for t in tasks if t["id"] not in MOVE_BEFORE_082]
    i = next(n for n, t in enumerate(rest) if t["id"] == "082")
    manifest["tasks"] = rest[:i] + moved + rest[i:]


SPEC_ORDER = ["id", "title", "objective", "requirement_ids", "complexity", "atomicity_rationale", "context_boundary",
              "dependencies", "scope", "implementation_guidance", "acceptance_criteria", "validation_commands", "subtasks",
              "provider", "model_tier", "reasoning_effort", "max_attempts", "learning_targets", "related_task_reads"]


def spec_value(t: dict, key: str):
    if key == "id":
        return int(t["id"])
    if key == "subtasks":
        return [{"id": s["id"], "title": s["title"], "objective": s["objective"]} for s in t["subtasks"]]
    return json.loads(json.dumps(t[key]))


def project_spec(spec: dict, manifest: dict) -> None:
    by_id = {f"{t['id']:03}": t for t in spec["tasks"]}
    new_tasks = []
    for t in manifest["tasks"]:
        old = by_id.get(t["id"])
        keys = list(old.keys()) if old else SPEC_ORDER
        new_tasks.append({k: spec_value(t, k) for k in keys})
    spec["tasks"] = new_tasks
    have = {r["id"] for r in spec["requirements"]}
    for r in manifest["requirements"]:
        if r["id"] not in have:
            spec["requirements"].append(json.loads(json.dumps(r)))


def update_acceptance_matrix(am: dict) -> None:
    for c in am["cases"]:
        if c["id"] == "A11":
            for key, tid in (("owner_tasks", "072"), ("review_tasks", "073")):
                if tid not in c[key]:
                    c[key] = sorted(c[key] + [tid])


def update_acceptance_matrix_md(text: str) -> str:
    return text.replace("| 074, 078 | 075, 079 |", "| 072, 074, 078 | 073, 075, 079 |")


INTEGRATION_OLD = ("currently observed Claude Fable 5.2, Codex GPT-6 Astra, Antigravity Gemini 4 Carbon and conditional other hosts")
INTEGRATION_NEW = ("observed `claude-fable-5-2` and `gpt-6.2-astra` as frontier (F6), architecture/code review only, after repeated "
                   "Opus 5.5 / Sol 6.2 failure; Antigravity has no frontier preset (Carbon is Ultra/Enterprise only and never preset)")


def update_integration_md(text: str) -> str:
    if INTEGRATION_NEW in text:
        return text
    if INTEGRATION_OLD not in text:
        raise Drift("IMPLEMENTATION_INTEGRATION.md item 14 text not found")
    return text.replace(INTEGRATION_OLD, INTEGRATION_NEW)


def update_checklist_md(text: str, manifest: dict, ids: set[str]) -> str:
    tasks = {t["id"]: t for t in manifest["tasks"]}
    out = []
    for line in text.split("\n"):
        m = re.match(r"^\| \[( |x)\] (\d{3}) \| (.*?) \| (.*?) \| (.*)$", line)
        if m and m.group(2) in ids:
            t = tasks[m.group(2)]
            line = f"| [{m.group(1)}] {t['id']} | {t['title']} | {', '.join(t['dependencies'])} | {m.group(5)}"
        out.append(line)
    return "\n".join(out)


REFINEMENT = ("2026-11-20 architecture review applied (PLAN_ARCHITECTURE_REVIEW_20261120.md sections A/B): "
              "checks, scope, dependencies and acceptance corrected; tasks 127-130 projected into the spec; "
              "task definitions re-rendered from the manifest; every task stays pending.")


def add_event(manifest: dict) -> None:
    if not any(ev.get("type") == "plan_review_corrections" and ev.get("reference") == REVIEW_REF for ev in manifest["events"]):
        manifest["events"].append({"at": APPLIED_AT, "type": "plan_review_corrections", "reference": REVIEW_REF,
                                   "task_count": len(manifest["tasks"]), "implementation_complete": False})
    manifest["updated_at"] = APPLIED_AT


# --------------------------------------------------------------------------------------
def read_json(path: Path):
    return json.loads(path.read_bytes().decode("utf-8").replace("\r\n", "\n"))


def dump_json(data, ensure_ascii: bool) -> bytes:
    return (json.dumps(data, indent=2, ensure_ascii=ensure_ascii) + "\n").replace("\n", "\r\n").encode("utf-8")


def crlf(text: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")


def self_checks(manifest: dict, spec: dict, ti: dict) -> list[str]:
    problems = []
    if len(manifest["tasks"]) != 130 or len(spec["tasks"]) != 130 or len(ti["tasks"]) != 130:
        problems.append("task count is not 130 everywhere")
    if {t["status"] for t in manifest["tasks"]} != {"pending"}:
        problems.append("a task is not pending")
    if manifest.get("autostart") is not False or spec.get("autostart") is not False:
        problems.append("autostart must stay false")
    if f"{spec['tasks'][-1]['id']:03}" != "086":
        problems.append("086 is not last in the spec")
    try:
        PC.validate_task_graph(manifest["tasks"])
    except Exception as exc:  # noqa: BLE001
        problems.append(f"dependency graph: {exc}")
    for t in manifest["tasks"]:
        e = next(x for x in ti["tasks"] if x["id"] == t["id"])
        if len(e["acceptance_ids"]) > len(t["acceptance_criteria"]):
            problems.append(f"{t['id']}: acceptance_ids exceed criteria")
    # Task-level text budgets of the plan's own contract (title/objective/scope/guidance/acceptance/subtasks).
    problems += [err for err in artifact_contract._validate_plan_text(PC, manifest) if err.startswith("Task ")]
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Report whether files would change; write nothing")
    args = ap.parse_args(argv)

    paths = {
        "manifest": PLAN / "manifest.json",
        "spec": DOC / "PLAN1_SPEC.json",
        "ti": DOC / "TASK_INPUTS.json",
        "am": DOC / "ACCEPTANCE_MATRIX.json",
        "trace": DOC / "REPLAN_TRACE.json",
    }
    manifest, spec, ti = read_json(paths["manifest"]), read_json(paths["spec"]), read_json(paths["ti"])
    am, trace = read_json(paths["am"]), read_json(paths["trace"])

    acc_touched = apply_ops(manifest, ti)
    reorder(manifest)
    finalize_acceptance(manifest, ti, acc_touched)
    add_event(manifest)
    project_spec(spec, manifest)
    update_acceptance_matrix(am)
    if REFINEMENT not in trace["post_conversion_refinements"]:
        trace["post_conversion_refinements"].append(REFINEMENT)

    problems = self_checks(manifest, spec, ti)
    if problems:
        for p in problems:
            print("PROBLEM:", p, file=sys.stderr)
        return 1

    outputs: dict[Path, bytes] = {
        paths["manifest"]: dump_json(manifest, False),
        paths["spec"]: dump_json(spec, False),
        paths["ti"]: dump_json(ti, True),
        paths["am"]: dump_json(am, True),
        paths["trace"]: dump_json(trace, True),
    }
    plan_id, work_root = manifest["plan_id"], manifest.get("work_root")
    for t in manifest["tasks"]:
        outputs[PLAN / t["file"]] = crlf(PC.render_task(t, plan_id, work_root))
    outputs[PLAN / "TODO.md"] = crlf(PC.render_todo(manifest))
    amd = DOC / "ACCEPTANCE_MATRIX.md"
    outputs[amd] = crlf(update_acceptance_matrix_md(amd.read_bytes().decode("utf-8").replace("\r\n", "\n")))
    integ = DOC / "IMPLEMENTATION_INTEGRATION.md"
    outputs[integ] = crlf(update_integration_md(integ.read_bytes().decode("utf-8").replace("\r\n", "\n")))
    checklist = DOC / "IMPLEMENTATION_CHECKLIST.md"
    changed_rows = {tid for ids, ops in OPS for tid in ids if {"title", "deps_add", "deps_set"} & set(ops)}
    outputs[checklist] = crlf(update_checklist_md(checklist.read_bytes().decode("utf-8").replace("\r\n", "\n"), manifest, changed_rows))

    changed = [p for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
    for p in changed:
        print(("would change: " if args.check else "wrote: ") + p.relative_to(ROOT).as_posix())
        if not args.check:
            p.write_bytes(outputs[p])
    print(f"{len(changed)} file(s) {'would change' if args.check else 'changed'}; acceptance edited on {len(acc_touched)} task(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
