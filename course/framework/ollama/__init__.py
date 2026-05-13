"""Ollama local AI helpers added in Session 28."""

from course.framework.ollama.local_ai import (
    MODEL_PROFILES,
    OllamaModelProfile,
    OllamaTaskType,
    OllamaWorkflow,
    build_ollama_command,
    create_workflow,
    fallback_note,
    recommend_model,
    should_use_ollama,
)

__all__ = [
    "MODEL_PROFILES",
    "OllamaModelProfile",
    "OllamaTaskType",
    "OllamaWorkflow",
    "build_ollama_command",
    "create_workflow",
    "fallback_note",
    "recommend_model",
    "should_use_ollama",
]
