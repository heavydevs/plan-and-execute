#!/usr/bin/env python3
"""Regression checks for sequential complex-study choice prompts after progressive disclosure."""

from __future__ import annotations

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
ORCHESTRATION = (SKILL_DIR / "references" / "ORCHESTRATION.md").read_text(encoding="utf-8")
STUDY = (SKILL_DIR / "references" / "ADAPTIVE_STUDY.md").read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} is missing required interaction contract: {needle!r}")


def main() -> None:
    # The router must point to orchestration, and orchestration must route study detail
    # to ADAPTIVE_STUDY instead of duplicating the interaction contract in SKILL.md.
    require(SKILL, "references/ORCHESTRATION.md", "SKILL.md")
    require(ORCHESTRATION, "ADAPTIVE_STUDY.md", "ORCHESTRATION.md")

    for needle in (
        "Ask only one choice per chat turn",
        "Choice 1 — internal study",
        "Choice 2 — external study",
        "Interactive choice UI",
        "vscode/askQuestions",
        "#vscode/askQuestions",
        "clicking with the mouse",
        "clickable **single-select** options",
        "Do not render a duplicate Markdown/numbered choice list",
        "Do not enable multi-select",
        "free-text input",
        "fall back to the same question plus exactly three numbered text options",
        "Do not mention or preview the external-study question in this turn",
        "Do not repeat the internal question or its options",
        "Never ask both questions together for convenience",
        "Recommendation marker",
        "exactly one recommended option",
        "(recomendado)",
        "never preselect the recommended option",
        "keep the underlying canonical value unchanged",
        "strip/ignore the display suffix",
        "Pacotes relacionados",
        "Busca por palavras-chave em todo o workspace",
        "Projeto completo",
        "Sem estudo externo",
        "Pesquisa focalizada",
        "Pesquisa ampla",
    ):
        require(STUDY, needle, "ADAPTIVE_STUDY.md")

    internal_pos = STUDY.index("Choice 1 — internal study")
    external_pos = STUDY.index("Choice 2 — external study")
    if internal_pos >= external_pos:
        raise AssertionError("Internal study choice must be defined before external study choice")
    if STUDY.count("Append **`(recomendado)`** to exactly one") != 2:
        raise AssertionError("Both study questions must require exactly one recommended display option")
    if STUDY.count("call `vscode/askQuestions` so the three options are clickable") != 2:
        raise AssertionError("Both study questions must use VS Code clickable choices when available")

    print("Sequential clickable study-choice interaction contract validated through progressive disclosure.")


if __name__ == "__main__":
    main()
