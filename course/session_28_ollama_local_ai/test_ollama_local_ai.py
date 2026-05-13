from __future__ import annotations

from course.framework.ollama import (
    OllamaTaskType,
    build_ollama_command,
    create_workflow,
    fallback_note,
    recommend_model,
    should_use_ollama,
)


def test_recommend_model_uses_coder_profile_for_small_diff_review() -> None:
    model = recommend_model(OllamaTaskType.REVIEW_SMALL_DIFF)

    assert model.name == "qwen2.5-coder"


def test_recommend_model_uses_general_profile_for_test_ideas() -> None:
    model = recommend_model(OllamaTaskType.GENERATE_TEST_IDEAS)

    assert model.name == "llama3.1"


def test_build_ollama_command_quotes_prompt() -> None:
    command = build_ollama_command("llama3.1", 'Summarize "failed tests"')

    assert command == 'ollama run llama3.1 "Summarize \\"failed tests\\""'


def test_create_workflow_includes_privacy_and_verification() -> None:
    workflow = create_workflow(OllamaTaskType.CLASSIFY_FAILURE, "Classify this traceback")

    assert "secrets" in workflow.privacy_note
    assert workflow.verification_steps


def test_should_not_use_ollama_when_prompt_contains_secrets() -> None:
    assert should_use_ollama(OllamaTaskType.SUMMARIZE, contains_secrets=True) is False


def test_fallback_note_mentions_deterministic_checks_for_review() -> None:
    assert "pytest" in fallback_note(OllamaTaskType.REVIEW_SMALL_DIFF)
