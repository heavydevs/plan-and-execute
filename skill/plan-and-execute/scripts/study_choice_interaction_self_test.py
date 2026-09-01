#!/usr/bin/env python3
"""Regression checks for sequential complex-study choice prompts."""

from __future__ import annotations

from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
STUDY = (SKILL_DIR / "references" / "ADAPTIVE_STUDY.md").read_text(encoding="utf-8")


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} is missing required interaction contract: {needle!r}")


def main() -> None:
    for needle in (
        "Ask **only the internal-study question first**",
        "Ask **only the external-study question** in a new turn",
        "Never combine or preview both questions",
    ):
        require(SKILL, needle, "SKILL.md")

    for needle in (
        "Ask only one choice per chat turn",
        "Choice 1 — internal study",
        "Choice 2 — external study",
        "native single-choice UI",
        "Do not mention or preview the external-study question in this turn",
        "Do not repeat the internal question or its options",
        "Never ask both questions together for convenience",
    ):
        require(STUDY, needle, "ADAPTIVE_STUDY.md")

    internal_pos = STUDY.index("Choice 1 — internal study")
    external_pos = STUDY.index("Choice 2 — external study")
    if internal_pos >= external_pos:
        raise AssertionError("Internal study choice must be defined before external study choice")

    print("Sequential study-choice interaction contract validated.")


if __name__ == "__main__":
    main()
