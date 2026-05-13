from __future__ import annotations

from course.framework.codex import (
    CodexCommand,
    CodexTaskType,
    CodexWorkflow,
    commands_requiring_approval,
    create_workflow,
    format_codex_prompt,
    workflow_has_verification,
)


def test_implement_test_workflow_has_test_edit_scope_and_verification() -> None:
    workflow = create_workflow(CodexTaskType.IMPLEMENT_TEST, "Add web UI test")

    assert "tests/" in workflow.edit_scope
    assert workflow_has_verification(workflow)
    assert any("pytest" in command.command for command in workflow.verification_commands)


def test_review_workflow_is_read_only() -> None:
    workflow = create_workflow(CodexTaskType.REVIEW, "Review course changes")

    assert workflow.edit_scope == ()
    assert "git diff --stat" in [command.command for command in workflow.inspection_commands]


def test_prompt_includes_goal_scope_and_verification() -> None:
    workflow = create_workflow(CodexTaskType.FIX_FAILURE, "Fix failing API test")
    prompt = format_codex_prompt(workflow)

    assert "Fix failing API test" in prompt
    assert "fix_failure" in prompt
    assert "Verification:" in prompt


def test_commands_requiring_approval_filters_flagged_commands() -> None:
    workflow = CodexWorkflow(
        task_type=CodexTaskType.REFACTOR,
        goal="Example",
        inspection_commands=(
            CodexCommand("git status --short", "Inspect"),
            CodexCommand("open allure-report/index.html", "Open browser", needs_approval=True),
        ),
        edit_scope=("tests/",),
        verification_commands=(),
    )

    approval_commands = commands_requiring_approval(workflow)

    assert len(approval_commands) == 1
    assert approval_commands[0].command.startswith("open ")


def test_refactor_workflow_defaults_to_framework_and_tests_scope() -> None:
    workflow = create_workflow(CodexTaskType.REFACTOR, "Simplify page objects")

    assert "pages/" in workflow.edit_scope
    assert "tests/" in workflow.edit_scope
