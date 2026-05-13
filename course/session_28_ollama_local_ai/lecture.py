"""
Session 28 - Ollama Local AI

Runnable examples for using local models through Ollama in QA automation while
keeping privacy, verification, and fallback rules explicit.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.ollama import (  # noqa: E402
    OllamaTaskType,
    build_ollama_command,
    create_workflow,
    fallback_note,
    should_use_ollama,
)


def demo() -> None:
    workflow = create_workflow(
        OllamaTaskType.GENERATE_TEST_IDEAS,
        "Suggest edge cases for shopping cart quantity validation.",
    )
    print("Model:", workflow.model.name)
    print("Command:", build_ollama_command(workflow.model.name, workflow.prompt))
    print("Privacy:", workflow.privacy_note)
    print("Use Ollama:", should_use_ollama(workflow.task_type, contains_secrets=False))
    print("Fallback:", fallback_note(workflow.task_type))


if __name__ == "__main__":
    demo()


__all__ = [
    "OllamaTaskType",
    "build_ollama_command",
    "create_workflow",
    "fallback_note",
    "should_use_ollama",
]
