"""
Session 26 - Codex CLI workflow reference layer.

The helpers model repeatable QA automation workflows for a coding agent:
inspect, plan, patch, verify, and summarize.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CodexTaskType(StrEnum):
    IMPLEMENT_TEST = "implement_test"
    FIX_FAILURE = "fix_failure"
    REVIEW = "review"
    REFACTOR = "refactor"


@dataclass(frozen=True)
class CodexCommand:
    command: str
    purpose: str
    writes_files: bool = False
    needs_approval: bool = False


@dataclass(frozen=True)
class CodexWorkflow:
    task_type: CodexTaskType
    goal: str
    inspection_commands: tuple[CodexCommand, ...]
    edit_scope: tuple[str, ...]
    verification_commands: tuple[CodexCommand, ...]


DEFAULT_INSPECTION_COMMANDS: tuple[CodexCommand, ...] = (
    CodexCommand("rg -n \"def test_|class Test\" tests", "Map existing tests"),
    CodexCommand("rg --files pages services flows tests", "Map framework files"),
)


def create_workflow(task_type: CodexTaskType, goal: str) -> CodexWorkflow:
    if task_type == CodexTaskType.IMPLEMENT_TEST:
        return CodexWorkflow(
            task_type=task_type,
            goal=goal,
            inspection_commands=DEFAULT_INSPECTION_COMMANDS,
            edit_scope=("tests/", "pages/", "flows/", "services/"),
            verification_commands=(
                CodexCommand(".venv/bin/pytest --collect-only -q tests", "Verify collection"),
                CodexCommand(".venv/bin/pytest -q", "Run relevant tests"),
            ),
        )

    if task_type == CodexTaskType.FIX_FAILURE:
        return CodexWorkflow(
            task_type=task_type,
            goal=goal,
            inspection_commands=(
                CodexCommand("git status --short", "Check worktree state"),
                CodexCommand("rg -n \"FAILED|ERROR|Traceback\" .", "Find failure context"),
            ),
            edit_scope=("tests/", "pages/", "services/", "conftest.py"),
            verification_commands=(
                CodexCommand(".venv/bin/pytest -q", "Confirm the failure is fixed"),
            ),
        )

    if task_type == CodexTaskType.REVIEW:
        return CodexWorkflow(
            task_type=task_type,
            goal=goal,
            inspection_commands=(
                CodexCommand("git diff --stat", "Summarize changed files"),
                CodexCommand("git diff --check", "Check whitespace and patch issues"),
            ),
            edit_scope=(),
            verification_commands=(
                CodexCommand(".venv/bin/pytest --collect-only -q", "Check test discovery"),
            ),
        )

    return CodexWorkflow(
        task_type=task_type,
        goal=goal,
        inspection_commands=DEFAULT_INSPECTION_COMMANDS,
        edit_scope=("pages/", "services/", "flows/", "tests/"),
        verification_commands=(
            CodexCommand(".venv/bin/pytest --collect-only -q", "Check collection"),
            CodexCommand(".venv/bin/pytest -q", "Run regression tests"),
        ),
    )


def format_codex_prompt(workflow: CodexWorkflow) -> str:
    scope = ", ".join(workflow.edit_scope) if workflow.edit_scope else "read-only"
    verify = "; ".join(command.command for command in workflow.verification_commands)
    return (
        f"Goal: {workflow.goal}\n"
        f"Task type: {workflow.task_type.value}\n"
        f"Edit scope: {scope}\n"
        f"Verification: {verify}"
    )


def commands_requiring_approval(workflow: CodexWorkflow) -> list[CodexCommand]:
    return [
        command
        for command in (*workflow.inspection_commands, *workflow.verification_commands)
        if command.needs_approval
    ]


def workflow_has_verification(workflow: CodexWorkflow) -> bool:
    return bool(workflow.verification_commands)
