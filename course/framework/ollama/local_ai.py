"""
Session 28 - Ollama local AI reference layer.

These helpers model when a QA workflow can use a local model through Ollama
and when it should fall back to a stronger hosted model or deterministic code.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OllamaTaskType(StrEnum):
    SUMMARIZE = "summarize"
    GENERATE_TEST_IDEAS = "generate_test_ideas"
    CLASSIFY_FAILURE = "classify_failure"
    REVIEW_SMALL_DIFF = "review_small_diff"


@dataclass(frozen=True)
class OllamaModelProfile:
    name: str
    strengths: tuple[str, ...]
    max_context_notes: str
    recommended_for: tuple[OllamaTaskType, ...]


@dataclass(frozen=True)
class OllamaWorkflow:
    task_type: OllamaTaskType
    model: OllamaModelProfile
    prompt: str
    privacy_note: str
    verification_steps: tuple[str, ...]


MODEL_PROFILES: tuple[OllamaModelProfile, ...] = (
    OllamaModelProfile(
        name="llama3.1",
        strengths=("general reasoning", "summaries", "test ideas"),
        max_context_notes="Good default for short QA notes and local summaries.",
        recommended_for=(
            OllamaTaskType.SUMMARIZE,
            OllamaTaskType.GENERATE_TEST_IDEAS,
        ),
    ),
    OllamaModelProfile(
        name="qwen2.5-coder",
        strengths=("code review", "small diffs", "failure analysis"),
        max_context_notes="Better for focused code snippets than large repository context.",
        recommended_for=(
            OllamaTaskType.CLASSIFY_FAILURE,
            OllamaTaskType.REVIEW_SMALL_DIFF,
        ),
    ),
)


def recommend_model(task_type: OllamaTaskType) -> OllamaModelProfile:
    for profile in MODEL_PROFILES:
        if task_type in profile.recommended_for:
            return profile
    return MODEL_PROFILES[0]


def build_ollama_command(model: str, prompt: str) -> str:
    escaped_prompt = prompt.replace('"', '\\"')
    return f'ollama run {model} "{escaped_prompt}"'


def create_workflow(task_type: OllamaTaskType, prompt: str) -> OllamaWorkflow:
    model = recommend_model(task_type)
    return OllamaWorkflow(
        task_type=task_type,
        model=model,
        prompt=prompt,
        privacy_note="Keep secrets, credentials, and private customer data out of prompts.",
        verification_steps=(
            "Check the model output against source files or test results.",
            "Convert useful suggestions into deterministic tests or code.",
            "Run the narrowest relevant pytest command before trusting the result.",
        ),
    )


def should_use_ollama(task_type: OllamaTaskType, contains_secrets: bool) -> bool:
    if contains_secrets:
        return False
    return task_type in {
        OllamaTaskType.SUMMARIZE,
        OllamaTaskType.GENERATE_TEST_IDEAS,
        OllamaTaskType.CLASSIFY_FAILURE,
        OllamaTaskType.REVIEW_SMALL_DIFF,
    }


def fallback_note(task_type: OllamaTaskType) -> str:
    if task_type == OllamaTaskType.REVIEW_SMALL_DIFF:
        return "Use deterministic linters, pytest, and human review if local model quality is weak."
    return "Use rules, source evidence, or a hosted model when the local model is insufficient."
