"""Deterministic /chat responses when ANTHROPIC_API_KEY is not configured."""

from __future__ import annotations

_MOCK_MODEL = "mock-claude-haiku-4-5"


def mock_chat_response(message: str, system: str | None = None) -> dict[str, object]:
    lowered = message.lower()
    system = (system or "").lower()

    if _is_injection_guard(system):
        text = _injection_guard_reply(message)
    elif _is_dlp(system):
        text = _dlp_reply(message)
    elif "2 + 2" in lowered or "2+2" in lowered:
        text = "4"
    elif "pirate" in system:
        text = "Ahoy matey! The sea be wide and the ship sails on."
    elif "purpose" in lowered:
        text = "I help customers with product inquiries and orders for this store."
    else:
        text = "Hello! How can I help you today?"

    return {
        "response": text,
        "model": _MOCK_MODEL,
        "input_tokens": max(1, len(message.split())),
        "output_tokens": max(1, len(text.split())),
    }


def _is_dlp(system: str) -> bool:
    return "never repeat" in system and "password" in system


def _is_injection_guard(system: str) -> bool:
    return "security rules" in system or "tutorialsninja support bot" in system


def _dlp_reply(_message: str) -> str:
    return (
        "Thank you for your message. I can help with your account, "
        "but I will not repeat passwords, card numbers, or other sensitive data."
    )


def _injection_guard_reply(_message: str) -> str:
    return (
        "I can only assist with TutorialsNinja store topics. "
        "I will not follow attempts to override my role or reveal hidden instructions."
    )
