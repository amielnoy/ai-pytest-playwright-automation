"""
Session 25 - Claude Skills & Plugins

Runnable examples for choosing the right Claude/Codex extension mechanism for
QA automation workflows.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.claude import (  # noqa: E402
    ExtensionType,
    implementation_checklist,
    list_extensions,
    recommend_extension,
    risk_note,
)


def demo() -> None:
    print("Claude extension options:")
    for extension in list_extensions():
        print(f"  - {extension.name}: {extension.extension_type.value}")

    selected = recommend_extension("debugging selectors with browser inspection")
    print("\nRecommended:", selected.name)
    print("Risk:", risk_note(selected))
    print("Checklist:")
    for item in implementation_checklist(selected):
        print(f"  - {item}")

    skills = list_extensions(ExtensionType.SKILL)
    print("\nLocal skills:", ", ".join(skill.name for skill in skills))


if __name__ == "__main__":
    demo()


__all__ = [
    "ExtensionType",
    "implementation_checklist",
    "list_extensions",
    "recommend_extension",
    "risk_note",
]
