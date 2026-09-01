#!/usr/bin/env python3
"""Concise derived-artifact contract for plan-and-execute.

This module intentionally leaves the user's original request untouched. It adds
field budgets, high-confidence vagueness checks, compact Markdown projections,
and bounded runner handoffs on top of the existing deterministic controllers.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


VAGUE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("as appropriate", re.compile(r"\bas appropriate\b", re.I)),
    ("as needed", re.compile(r"\bas needed\b", re.I)),
    ("when required", re.compile(r"\bwhen required\b", re.I)),
    ("if required", re.compile(r"\bif required\b", re.I)),
    ("etc.", re.compile(r"\betc\.?\b", re.I)),
    ("and/or", re.compile(r"\band/or\b", re.I)),
    ("but not limited to", re.compile(r"\bbut not limited to\b", re.I)),
    ("user-friendly", re.compile(r"\buser[- ]friendly\b", re.I)),
    ("adequate", re.compile(r"\badequate\b", re.I)),
    ("sufficient", re.compile(r"\bsufficient\b", re.I)),
    ("robust", re.compile(r"\brobust\b", re.I)),
    ("quickly", re.compile(r"\bquickly\b", re.I)),
    ("easily", re.compile(r"\beasily\b", re.I)),
    ("conforme apropriado", re.compile(r"\bconforme apropriado\b", re.I)),
    ("conforme necessário", re.compile(r"\bconforme necess[aá]rio\b", re.I)),
    ("quando necessário", re.compile(r"\bquando necess[aá]rio\b", re.I)),
    ("se necessário", re.compile(r"\bse necess[aá]rio\b", re.I)),
    ("e/ou", re.compile(r"\be/ou\b", re.I)),
    ("adequado", re.compile(r"\badequad[oa]s?\b", re.I)),
    ("suficiente", re.compile(r"\bsuficiente(s)?\b", re.I)),
    ("robusto", re.compile(r"\brobust[oa]s?\b", re.I)),
    ("rapidamente", re.compile(r"\brapidamente\b", re.I)),
    ("facilmente", re.compile(r"\bfacilmente\b", re.I)),
)

# Character budgets are intentionally conservative rather than tiny. The goal
# is one precise semantic unit, not lossy compression.
PLAN_BUDGETS = {
    "title": 120,
    "summary": 320,
    "request_part": 280,
    "requirement": 280,
    "finding": 320,
    "decision": 240,
    "assumption": 240,
    "risk": 240,
    "question": 240,
    "strategy": 320,
    "constraint": 240,
    "reviewer": 100,
    "review_note": 240,
    "task_title": 120,
    "task_objective": 320,
    "atomicity": 320,
    "scope": 200,
    "guidance": 240,
    "acceptance": 240,
    "validation_command": 1000,
    "related_reason": 240,
}

STUDY_BUDGETS = {
    "request_summary": 320,
    "rationale": 280,
    "signal": 180,
    "location": 220,
    "finding": 320,
    "impact": 280,
    "title": 180,
    "publisher": 120,
    "version": 80,
    "authority": 220,
    "question": 240,
    "resolution": 280,
    "synthesis": 260,
    "stopping": 280,
    "reviewer": 100,
    "review_note": 240,
}

MAX_LIST_ITEMS = {
    "findings": 16,
    "assumptions": 10,
    "risks": 10,
    "questions": 10,
    "constraints": 16,
    "review_notes": 8,
    "scope": 12,
    "guidance": 12,
    "acceptance": 16,
    "validations": 16,
}


def _error(error_type: type[Exception], message: str) -> None:
    raise error_type(message)


def concise_line(
    value: Any,
    field: str,
    maximum: int,
    error_type: type[Exception],
    *,
    vague: bool = True,
    allow_empty: bool = False,
) -> str:
    text = str(value or "").strip()
    if not text:
        if allow_empty:
            return ""
        _error(error_type, f"{field} must be a non-empty string")
    if "\n" in text or "\r" in text:
        _error(error_type, f"{field} must be one semantic unit on one line")
    if len(text) > maximum:
        _error(error_type, f"{field} exceeds the {maximum}-character derived-text budget")
    if vague:
        for label, pattern in VAGUE_PATTERNS:
            if pattern.search(text):
                _error(
                    error_type,
                    f"{field} uses vague wording {label!r}; replace it with an observable condition, concrete noun, or measurable boundary",
                )
    return text


def concise_list(
    values: Any,
    field: str,
    maximum: int,
    error_type: type[Exception],
    *,
    max_items: int,
    vague: bool = True,
) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        _error(error_type, f"{field} must be a list")
    if len(values) > max_items:
        _error(error_type, f"{field} may contain at most {max_items} atomic items")
    result: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(values):
        text = concise_line(
            item,
            f"{field}[{index}]",
            maximum,
            error_type,
            vague=vague,
        )
        folded = text.casefold()
        if folded in seen:
            _error(error_type, f"{field} contains duplicate text: {text!r}")
        seen.add(folded)
        result.append(text)
    return result


def _md(items: Iterable[str], empty: str = "- None") -> str:
    values = [str(item) for item in items if str(item).strip()]
    return "\n".join(f"- {item}" for item in values) if values else empty


def _compact_plan_renderers(planctl: Any) -> None:
    def render_global_context(execution_context: dict[str, Any]) -> str:
        items = execution_context["global"]["items"]
        return "# Context — all TODOs\n\n" + "\n".join(
            planctl.render_context_item(item) for item in items
        ) + "\n"

    def render_scoped_context(context: dict[str, Any]) -> str:
        tasks = ", ".join(context["task_ids"])
        return f"# {context['title']} — TODOs {tasks}\n\n" + "\n".join(
            planctl.render_context_item(item) for item in context["items"]
        ) + "\n"

    def render_execution_context_strategy(execution_context: dict[str, Any]) -> str:
        global_context = execution_context["global"]
        if global_context["decision"] == "create":
            global_line = (
                f"- global: `{planctl.GLOBAL_CONTEXT_FILE}`; "
                f"{len(global_context['items'])} item(s); {global_context['rationale']}"
            )
        else:
            global_line = f"- global: omitted; {global_context['rationale']}"
        lines = [global_line]
        for context in execution_context["scoped"]:
            lines.append(
                f"- `{context['file']}` -> {','.join(context['task_ids'])}; {context['rationale']}"
            )
        return "\n".join(lines)

    def render_analysis(manifest: dict[str, Any]) -> str:
        analysis = manifest["request_analysis"]
        source = (
            f"`{manifest['request_source']['file']}`"
            if manifest.get("request_source")
            else "inline conversation"
        )
        lines = [
            f"# Analysis — {manifest['title']}",
            "",
            f"Request: {source}",
            "",
            "## Parts",
            "",
            planctl.render_request_part_list(analysis["request_parts"]),
            "",
            "## Repository",
            "",
            _md(analysis["repository_findings"]),
            "",
            f"Research: {analysis['research_decision']}",
        ]
        optional_sections = (
            ("External findings", analysis["research_findings"]),
            ("Assumptions", analysis["assumptions"]),
            ("Risks", analysis["risks"]),
            ("Open questions", analysis["open_questions"]),
        )
        for heading, values in optional_sections:
            if values:
                lines.extend(["", f"## {heading}", "", _md(values)])
        lines.extend(["", "## Decomposition", "", analysis["decomposition_strategy"], ""])
        return "\n".join(lines)

    def render_plan_review(manifest: dict[str, Any]) -> str:
        review = manifest["plan_review"]
        checks = ", ".join(planctl.review_checks_for_schema(manifest.get("schema_version")))
        return (
            f"# Plan review — {manifest['title']}\n\n"
            f"approved · reviewer `{review['reviewer']}` · round {review['rounds']}\n\n"
            f"Checks: {checks}\n\n"
            f"## Notes\n\n{_md(review['notes'])}\n"
        )

    def render_plan(manifest: dict[str, Any]) -> str:
        req_to_tasks = planctl.requirement_coverage(manifest["requirements"], manifest["tasks"])
        requirement_lines: list[str] = []
        for req in manifest["requirements"]:
            parts = ",".join(req.get("request_part_ids", [])) or "derived"
            tasks = ",".join(req_to_tasks[req["id"]])
            requirement_lines.append(
                f"- **{req['id']}** [{req['priority']}; {req['source']}; {parts} -> {tasks}] {req['text']}"
            )
        context = (
            render_execution_context_strategy(manifest["execution_context"])
            if int(manifest.get("schema_version", 0)) >= 3
            else "- legacy"
        )
        constraints = manifest.get("global_constraints", [])
        lines = [
            f"# {manifest['title']}",
            "",
            manifest["summary"],
            "",
            "## Requirements -> TODOs",
            "",
            "\n".join(requirement_lines),
        ]
        if constraints:
            lines.extend(["", "## Constraints", "", _md(constraints)])
        lines.extend(
            [
                "",
                "## Context",
                "",
                context,
                "",
                "Evidence: `ANALYSIS.md` · `PLAN_REVIEW.md` · attached study when present",
                "",
                f"Autostart: {'yes' if manifest['autostart'] else 'no'} · cleanup: {'yes' if manifest['cleanup_on_success'] else 'no'}",
                "",
            ]
        )
        return "\n".join(lines)

    def render_task(
        task: dict[str, Any],
        plan_id: str,
        work_root: str = planctl.WORK_ROOT_DEFAULT,
    ) -> str:
        deps = ",".join(task["dependencies"]) or "none"
        reqs = ",".join(task["requirement_ids"])
        related = ",".join(task["related_task_reads"]) or "none"
        context_refs = [
            planctl.context_reference(work_root, plan_id, item)
            for item in task.get("context_files", [])
        ]
        learning_refs = [
            planctl.context_reference(work_root, plan_id, item)
            for item in task.get("learning_files", [])
        ]
        subtask_lines: list[str] = []
        for subtask in task.get("subtasks", []):
            marker = "[x]" if subtask.get("status") == "completed" else "[ ]"
            state = " ~" if subtask.get("status") == "in_progress" else ""
            optional = " (optional)" if not subtask.get("required", True) else ""
            objective = str(subtask.get("objective", "")).strip()
            suffix = f" — {objective}" if objective else ""
            subtask_lines.append(
                f"- {marker} **{subtask.get('id','?')}** {subtask.get('title','')}{optional}{state}{suffix}"
            )
        targets: list[str] = []
        for target in task.get("learning_targets", []):
            if isinstance(target, dict):
                targets.append(
                    f"- {target.get('task_id','?')}: {', '.join(target.get('topics', []))}"
                )
        lines = [
            "---",
            f'task_id: "{task["id"]}"',
            f'status: "{task["status"]}"',
            f'requirements: "{reqs}"',
            f'dependencies: "{deps}"',
            f'allowed_related_task_reads: "{related}"',
            "---",
            "",
            f"# {task['id']} — {task['title']}",
            "",
            f"Objective: {task['objective']}",
            "",
            "## Context",
            "",
            _md([f"`{item}`" for item in context_refs]),
            "",
            "## Validated learnings",
            "",
            _md([f"`{item}`" for item in learning_refs]),
            "",
            "## Checkpoints",
            "",
            "\n".join(subtask_lines) or "- None",
        ]
        if targets:
            lines.extend(["", "## Publishable learning topics", "", "\n".join(targets)])
        scope_in = task["scope"]["in"]
        scope_out = task["scope"]["out"]
        expected = task["scope"]["expected_files"]
        if scope_in or scope_out or expected:
            lines.extend(["", "## Scope", ""])
            if scope_in:
                lines.append("In: " + "; ".join(scope_in))
            if scope_out:
                lines.append("Out: " + "; ".join(scope_out))
            if expected:
                lines.append("Files: " + ", ".join(f"`{item}`" for item in expected))
        if task["implementation_guidance"]:
            lines.extend(["", "## Guidance", "", _md(task["implementation_guidance"])])
        lines.extend(
            [
                "",
                "## Acceptance",
                "",
                _md(task["acceptance_criteria"]),
                "",
                "## Validate",
                "",
                "\n".join(f"- `{command}`" for command in task["validation_commands"]),
                "",
            ]
        )
        return "\n".join(lines)

    def render_learning_artifact(
        source_task: dict[str, Any],
        target_task: dict[str, Any],
        declaration: dict[str, Any],
        learnings: list[dict[str, Any]],
    ) -> str:
        lines = [
            f"# Learning {source_task['id']} -> {target_task['id']}",
            "",
            f"Topics: {', '.join(declaration['topics'])}",
            f"Reason: {declaration['reason']}",
            "",
        ]
        for learning in learnings:
            refs = ", ".join(f"`{item}`" for item in learning["references"])
            lines.append(f"- **{learning['kind']}** {learning['guidance']} _(refs: {refs})_")
        content = "\n".join(lines).rstrip() + "\n"
        if len(content) > planctl.MAX_LEARNING_FILE_CHARS:
            raise planctl.PlanError(
                f"Learning artifact {source_task['id']}->{target_task['id']} exceeds "
                f"{planctl.MAX_LEARNING_FILE_CHARS} characters"
            )
        return content

    planctl.render_global_context = render_global_context
    planctl.render_scoped_context = render_scoped_context
    planctl.render_execution_context_strategy = render_execution_context_strategy
    planctl.render_analysis = render_analysis
    planctl.render_plan_review = render_plan_review
    planctl.render_plan = render_plan
    planctl.render_task = render_task
    planctl.render_learning_artifact = render_learning_artifact


def _validate_plan_manifest(planctl: Any, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def check(callable_obj: Any, *args: Any, **kwargs: Any) -> None:
        try:
            callable_obj(*args, **kwargs)
        except planctl.PlanError as exc:
            errors.append(str(exc))

    check(concise_line, manifest.get("title"), "title", PLAN_BUDGETS["title"], planctl.PlanError)
    check(concise_line, manifest.get("summary"), "summary", PLAN_BUDGETS["summary"], planctl.PlanError)
    for index, item in enumerate(manifest.get("global_constraints", [])):
        check(concise_line, item, f"global_constraints[{index}]", PLAN_BUDGETS["constraint"], planctl.PlanError)
    analysis = manifest.get("request_analysis", {})
    for index, part in enumerate(analysis.get("request_parts", [])):
        check(concise_line, part.get("text"), f"request_analysis.request_parts[{index}].text", PLAN_BUDGETS["request_part"], planctl.PlanError)
    for index, req in enumerate(manifest.get("requirements", [])):
        check(concise_line, req.get("text"), f"requirements[{index}].text", PLAN_BUDGETS["requirement"], planctl.PlanError)
    list_fields = (
        ("repository_findings", "finding", "findings"),
        ("research_findings", "finding", "findings"),
        ("assumptions", "assumption", "assumptions"),
        ("risks", "risk", "risks"),
        ("open_questions", "question", "questions"),
    )
    for field, budget_key, count_key in list_fields:
        check(concise_list, analysis.get(field, []), f"request_analysis.{field}", PLAN_BUDGETS[budget_key], planctl.PlanError, max_items=MAX_LIST_ITEMS[count_key])
    check(concise_line, analysis.get("research_decision"), "request_analysis.research_decision", PLAN_BUDGETS["decision"], planctl.PlanError)
    check(concise_line, analysis.get("decomposition_strategy"), "request_analysis.decomposition_strategy", PLAN_BUDGETS["strategy"], planctl.PlanError)
    review = manifest.get("plan_review", {})
    check(concise_line, review.get("reviewer"), "plan_review.reviewer", PLAN_BUDGETS["reviewer"], planctl.PlanError, vague=False)
    check(concise_list, review.get("notes", []), "plan_review.notes", PLAN_BUDGETS["review_note"], planctl.PlanError, max_items=MAX_LIST_ITEMS["review_notes"])
    for task in manifest.get("tasks", []):
        task_id = str(task.get("id", "?"))
        for field, key in (("title", "task_title"), ("objective", "task_objective"), ("atomicity_rationale", "atomicity")):
            check(concise_line, task.get(field), f"Task {task_id} {field}", PLAN_BUDGETS[key], planctl.PlanError)
        for field_name in ("in", "out"):
            check(concise_list, task.get("scope", {}).get(field_name, []), f"Task {task_id} scope.{field_name}", PLAN_BUDGETS["scope"], planctl.PlanError, max_items=MAX_LIST_ITEMS["scope"])
        check(concise_list, task.get("implementation_guidance", []), f"Task {task_id} implementation_guidance", PLAN_BUDGETS["guidance"], planctl.PlanError, max_items=MAX_LIST_ITEMS["guidance"])
        check(concise_list, task.get("acceptance_criteria", []), f"Task {task_id} acceptance_criteria", PLAN_BUDGETS["acceptance"], planctl.PlanError, max_items=MAX_LIST_ITEMS["acceptance"])
        check(concise_list, task.get("validation_commands", []), f"Task {task_id} validation_commands", PLAN_BUDGETS["validation_command"], planctl.PlanError, max_items=MAX_LIST_ITEMS["validations"], vague=False)
        boundary = task.get("context_boundary", {})
        check(concise_line, boundary.get("why_one_todo"), f"Task {task_id} context_boundary.why_one_todo", 360, planctl.PlanError)
        check(concise_list, boundary.get("shared_context", []), f"Task {task_id} context_boundary.shared_context", 200, planctl.PlanError, max_items=6)
        check(concise_list, boundary.get("separate_from", []), f"Task {task_id} context_boundary.separate_from", 200, planctl.PlanError, max_items=6)
        for subtask in task.get("subtasks", []):
            sid = str(subtask.get("id", "?"))
            check(concise_line, subtask.get("title"), f"Task {task_id} subtask {sid} title", 120, planctl.PlanError)
            if str(subtask.get("objective", "")).strip():
                check(concise_line, subtask.get("objective"), f"Task {task_id} subtask {sid} objective", 280, planctl.PlanError)
        for target in task.get("learning_targets", []):
            tid = str(target.get("task_id", "?"))
            check(concise_line, target.get("reason"), f"Task {task_id} learning target {tid} reason", 280, planctl.PlanError)
            check(concise_list, target.get("topics", []), f"Task {task_id} learning target {tid} topics", 80, planctl.PlanError, max_items=6)
    return errors


def install_plan_contract() -> Any:
    import planctl

    if getattr(planctl, "_concise_artifact_contract", False):
        return planctl

    planctl.MAX_CONTEXT_TEXT_CHARS = min(planctl.MAX_CONTEXT_TEXT_CHARS, 220)
    planctl.MAX_CONTEXT_NECESSITY_CHARS = min(planctl.MAX_CONTEXT_NECESSITY_CHARS, 260)
    planctl.MAX_CONTEXT_RATIONALE_CHARS = min(planctl.MAX_CONTEXT_RATIONALE_CHARS, 320)
    planctl.MAX_CONTEXT_FILE_CHARS = min(planctl.MAX_CONTEXT_FILE_CHARS, 2200)
    planctl.MAX_TASK_BOUNDARY_TEXT_CHARS = min(planctl.MAX_TASK_BOUNDARY_TEXT_CHARS, 360)
    planctl.MAX_TASK_BOUNDARY_ITEM_CHARS = min(planctl.MAX_TASK_BOUNDARY_ITEM_CHARS, 200)
    planctl.MAX_SUBTASK_TITLE_CHARS = min(planctl.MAX_SUBTASK_TITLE_CHARS, 120)
    planctl.MAX_SUBTASK_OBJECTIVE_CHARS = min(planctl.MAX_SUBTASK_OBJECTIVE_CHARS, 280)
    planctl.MAX_LEARNING_TOPIC_CHARS = min(planctl.MAX_LEARNING_TOPIC_CHARS, 80)
    planctl.MAX_LEARNING_GUIDANCE_CHARS = min(planctl.MAX_LEARNING_GUIDANCE_CHARS, 320)
    planctl.MAX_LEARNING_FILE_CHARS = min(planctl.MAX_LEARNING_FILE_CHARS, 2200)

    original_create_plan = planctl.create_plan
    original_validate_plan = planctl.validate_plan
    original_fail_task = planctl.fail_task

    def create_plan(*args: Any, **kwargs: Any) -> Path:
        spec = args[1] if len(args) > 1 else kwargs.get("spec")
        if not isinstance(spec, dict):
            raise planctl.PlanError("Plan spec root must be an object")
        concise_line(spec.get("title"), "title", PLAN_BUDGETS["title"], planctl.PlanError)
        concise_line(spec.get("summary"), "summary", PLAN_BUDGETS["summary"], planctl.PlanError)
        concise_list(spec.get("global_constraints", []), "global_constraints", PLAN_BUDGETS["constraint"], planctl.PlanError, max_items=MAX_LIST_ITEMS["constraints"])
        return original_create_plan(*args, **kwargs)

    def validate_plan(plan_dir: Path, manifest: dict[str, Any] | None = None) -> list[str]:
        errors = original_validate_plan(plan_dir, manifest)
        if manifest is None:
            try:
                _plan_dir, loaded = planctl.load_plan(plan_dir)
                manifest = loaded
            except planctl.PlanError:
                return errors
        errors.extend(_validate_plan_manifest(planctl, manifest))
        return errors

    def fail_task(plan_dir: Path, manifest: dict[str, Any], task_id: str, reason: str, *, rate_limited: bool = False) -> dict[str, Any]:
        clipped = str(reason).strip()
        if len(clipped) > 1400:
            clipped = clipped[:1397].rstrip() + "..."
        return original_fail_task(plan_dir, manifest, task_id, clipped, rate_limited=rate_limited)

    planctl.create_plan = create_plan
    planctl.validate_plan = validate_plan
    planctl.fail_task = fail_task
    _compact_plan_renderers(planctl)
    planctl._concise_artifact_contract = True
    return planctl


def _validate_study(studyctl: Any, study: dict[str, Any]) -> None:
    err = studyctl.StudyError
    concise_line(study.get("request_summary"), "request_summary", STUDY_BUDGETS["request_summary"], err)
    if study.get("schema_version", 1) >= 2:
        complexity = study["complexity_assessment"]
        concise_line(complexity["rationale"], "complexity_assessment.rationale", STUDY_BUDGETS["rationale"], err)
        concise_list(complexity["signals"], "complexity_assessment.signals", STUDY_BUDGETS["signal"], err, max_items=8)
        internal = study["internal_study"]
        concise_line(internal["rationale"], "internal_study.rationale", STUDY_BUDGETS["rationale"], err)
        concise_line(internal["plan_finding"], "internal_study.plan_finding", STUDY_BUDGETS["finding"], err)
    for index, source in enumerate(study.get("internal_sources", [])):
        concise_line(source["location"], f"internal_sources[{index}].location", STUDY_BUDGETS["location"], err, vague=False)
        concise_line(source["finding"], f"internal_sources[{index}].finding", STUDY_BUDGETS["finding"], err)
        concise_line(source["planning_impact"], f"internal_sources[{index}].planning_impact", STUDY_BUDGETS["impact"], err)
    external = study["external_research"]
    concise_line(external["rationale"], "external_research.rationale", STUDY_BUDGETS["rationale"], err)
    for index, source in enumerate(external.get("sources", [])):
        concise_line(source["title"], f"external_research.sources[{index}].title", STUDY_BUDGETS["title"], err, vague=False)
        concise_line(source["publisher"], f"external_research.sources[{index}].publisher", STUDY_BUDGETS["publisher"], err, vague=False)
        concise_line(source["version_or_date"], f"external_research.sources[{index}].version_or_date", STUDY_BUDGETS["version"], err, vague=False)
        concise_line(source["why_authoritative"], f"external_research.sources[{index}].why_authoritative", STUDY_BUDGETS["authority"], err)
        concise_line(source["finding"], f"external_research.sources[{index}].finding", STUDY_BUDGETS["finding"], err)
        concise_line(source["planning_impact"], f"external_research.sources[{index}].planning_impact", STUDY_BUDGETS["impact"], err)
    for index, question in enumerate(study.get("material_questions", [])):
        concise_line(question["question"], f"material_questions[{index}].question", STUDY_BUDGETS["question"], err)
        if question.get("resolution"):
            concise_line(question["resolution"], f"material_questions[{index}].resolution", STUDY_BUDGETS["resolution"], err)
        if question.get("planning_impact"):
            concise_line(question["planning_impact"], f"material_questions[{index}].planning_impact", STUDY_BUDGETS["impact"], err)
    synthesis = study["synthesis"]
    for field in studyctl.SYNTHESIS_FIELDS:
        concise_list(synthesis[field], f"synthesis.{field}", STUDY_BUDGETS["synthesis"], err, max_items=12)
    concise_list(synthesis["unresolved_questions"], "synthesis.unresolved_questions", STUDY_BUDGETS["question"], err, max_items=10)
    concise_line(synthesis["stopping_reason"], "synthesis.stopping_reason", STUDY_BUDGETS["stopping"], err)
    review = study["review"]
    concise_line(review["reviewer"], "review.reviewer", STUDY_BUDGETS["reviewer"], err, vague=False)
    concise_list(review["notes"], "review.notes", STUDY_BUDGETS["review_note"], err, max_items=8)


def _compact_study_renderer(studyctl: Any, study: dict[str, Any]) -> str:
    external = study["external_research"]
    lines = ["# Study", "", study["request_summary"]]
    if study.get("schema_version", 1) >= 2:
        complexity = study["complexity_assessment"]
        internal = study["internal_study"]
        lines.extend(["", "## Triage", "", f"- complexity: **{complexity['level']}** — {complexity['rationale']}", f"- internal: **{internal['depth']}** ({internal['selection_source']}) — {internal['plan_finding']}", f"- external: **{external['depth']}** ({external['selection_source']}); {external['decision']} — {external['rationale']}"])
    if study["material_questions"]:
        lines.extend(["", "## Questions", ""])
        for item in study["material_questions"]:
            evidence = ",".join(item["evidence_ids"]) or "none"
            tail = item["resolution"] or "open"
            impact = f" -> {item['planning_impact']}" if item["planning_impact"] else ""
            lines.append(f"- **{item['id']}** [{item['importance']}/{item['status']}; {evidence}] {item['question']} — {tail}{impact}")
    if study["internal_sources"]:
        lines.extend(["", "## Repository evidence", ""])
        for item in study["internal_sources"]:
            lines.append(f"- **{item['id']}** `{item['location']}` — {item['finding']} -> {item['planning_impact']}")
    if external["sources"]:
        lines.extend(["", "## External evidence", ""])
        for item in external["sources"]:
            lines.append(f"- **{item['id']}** {item['publisher']}, {item['title']} ({item['version_or_date']}) — {item['finding']} -> {item['planning_impact']} · {item['url']}")
    synthesis = study["synthesis"]
    for heading, field in (("Constraints", "planning_constraints"), ("Derived requirements", "derived_requirements"), ("Risks", "risks"), ("Validation", "validation_implications"), ("Unresolved", "unresolved_questions")):
        if synthesis[field]:
            lines.extend(["", f"## {heading}", "", _md(synthesis[field])])
    lines.extend(["", f"Stop: {synthesis['stopping_reason']}", f"Ready: **{'yes' if synthesis['ready_for_planning'] else 'no'}**", "", f"Review: `{study['review']['reviewer']}` — " + ", ".join(field for field in studyctl.REVIEW_CHECKS if study['review'][field]), "", _md(study["review"]["notes"]), ""])
    return "\n".join(lines)


def install_study_contract() -> Any:
    import studyctl

    if getattr(studyctl, "_concise_artifact_contract", False):
        return studyctl
    original_normalize_study = studyctl.normalize_study

    def normalize_study(raw: Any, *, require_ready: bool = True) -> dict[str, Any]:
        study = original_normalize_study(raw, require_ready=require_ready)
        _validate_study(studyctl, study)
        return study

    studyctl.normalize_study = normalize_study
    studyctl.render_study = lambda study: _compact_study_renderer(studyctl, study)
    studyctl._concise_artifact_contract = True
    return studyctl


def install_runner_contract(run_isolated: Any) -> Any:
    planctl = install_plan_contract()
    script_dir = Path(run_isolated.__file__).resolve().parent
    controller = script_dir / "planctl_concise.py"

    def worker_prompt(plan_dir: Path, manifest: dict[str, Any], task: dict[str, Any], route: dict[str, str]) -> str:
        task_path = (plan_dir / task["file"]).resolve()
        schema_path = run_isolated.completion_schema_path().resolve()
        return f"""You implement one isolated TODO. Keep context narrow and return only the required JSON report.

Rules:
1. Read `{task_path}` first, then exactly the context and learning files listed there. Do not read other plan files, task definitions, logs, results, or `.ai-work` artifacts.
2. You may read/edit repository source, tests, build files, and runtime output needed for this TODO. Preserve unrelated working-tree changes.
3. Stay inside the task scope and acceptance criteria. Do not edit planning/context/learning artifacts.
4. Checkpoint subtasks only with `{controller}` using `subtask-start`, `subtask-complete`, or `subtask-reset` for parent `{task['id']}`.
5. Run the task validation commands before reporting completion.
6. Report exact `context_files_read`, `learning_files_read`, and all completed subtask ids. Related task reads are allowed only if explicitly allowlisted in the task definition and must include a reason.
7. Publish reusable learning only to predeclared future targets/topics, with concrete repository or command references. Prefer no learning over generic advice.
8. Output one JSON object matching `{schema_path}`; keep summary/details/risks/follow-ups concise.

Repository: `{manifest['repo_root']}`
Task: `{task['id']}`
Route: {route['provider']} / {route['model']} / {route['effort']}
"""

    original_validation = run_isolated.run_validation_commands

    def run_validation_commands(*args: Any, **kwargs: Any) -> tuple[bool, list[dict[str, Any]], str | None]:
        passed, results, reason = original_validation(*args, **kwargs)
        for item in results:
            if isinstance(item, dict) and isinstance(item.get("output_tail"), str):
                tail = item["output_tail"]
                item["output_tail"] = tail[-800:] if len(tail) > 800 else tail
        if reason and len(reason) > 1500:
            reason = reason[:1497].rstrip() + "..."
        return passed, results, reason

    def compact_report(plan_dir: Path, task: dict[str, Any]) -> dict[str, Any]:
        result_file = task.get("result_file")
        report: dict[str, Any] = {}
        if isinstance(result_file, str) and result_file:
            path = plan_dir / result_file
            if path.is_file():
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(raw, dict):
                        report = raw
                except (OSError, json.JSONDecodeError):
                    pass
        return {"id": task.get("id"), "title": task.get("title"), "summary": str(report.get("summary") or "")[:360], "changed_files": task.get("changed_files", []), "validation": [{"command": item.get("command"), "passed": item.get("passed"), "exit_code": item.get("exit_code")} for item in task.get("validation_results", []) if isinstance(item, dict)], "risks": report.get("risks", [])[:8] if isinstance(report.get("risks"), list) else [], "follow_ups": report.get("follow_ups", [])[:8] if isinstance(report.get("follow_ups"), list) else []}

    def compose_summary_input(plan_dir: Path, manifest: dict[str, Any]) -> Path:
        repo_root = Path(manifest["repo_root"])
        bundle = {"title": manifest["title"], "goal": manifest["summary"], "tasks": [compact_report(plan_dir, task) for task in manifest["tasks"]], "git_diff_stat": run_isolated.git_diff_stat(repo_root)[:4000]}
        path = plan_dir / "SUMMARY_INPUT.json"
        planctl.atomic_write_json(path, bundle)
        return path

    def summary_prompt(plan_dir: Path, manifest: dict[str, Any], input_path: Path) -> str:
        output_path = plan_dir / "FINAL_SUMMARY.md"
        return f"""Write the final implementation handoff from `{input_path}` only.
Be concise and concrete. Include outcome, changed areas, validation, and only remaining risks/follow-ups that are present in the input. Do not invent work or restate planning history. Write Markdown to `{output_path}`."""

    run_isolated.worker_prompt = worker_prompt
    run_isolated.run_validation_commands = run_validation_commands
    run_isolated.compose_summary_input = compose_summary_input
    run_isolated.summary_prompt = summary_prompt
    return run_isolated
