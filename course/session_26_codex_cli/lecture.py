"""
Session 26 - Codex CLI

Runnable examples for using Codex CLI as a disciplined QA automation coding
partner: inspect first, keep edits scoped, verify, then summarize.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.codex import (  # noqa: E402
    CodexTaskType,
    create_workflow,
    format_codex_prompt,
    workflow_has_verification,
)


def demo() -> None:
    workflow = create_workflow(
        CodexTaskType.IMPLEMENT_TEST,
        "Add web UI coverage for account navigation",
    )
    print(format_codex_prompt(workflow))
    print("\nInspection commands:")
    for command in workflow.inspection_commands:
        print(f"  - {command.command}  # {command.purpose}")
    print("\nHas verification:", workflow_has_verification(workflow))


if __name__ == "__main__":
    demo()


__all__ = [
    "CodexTaskType",
    "create_workflow",
    "format_codex_prompt",
    "workflow_has_verification",
]
