"""
Session 6 - Exception Handling

Runnable examples for turning low-level errors into clear automation framework
failures while preserving the original exception chain.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.exceptions import (  # noqa: E402
    ConfigurationError,
    ErrorContext,
    ExternalServiceError,
    FrameworkError,
    require_value,
    retry_expected,
    safe_call,
)


def load_required_base_url(raw_value: str | None) -> str:
    return require_value(raw_value, "BASE_URL")


def parse_price(raw_price: str) -> float:
    context = ErrorContext(
        operation="Parse product price",
        target=raw_price,
        details="expected numeric text after removing currency symbols",
    )
    return safe_call(
        lambda: float(raw_price.replace("$", "").replace(",", "")),
        context,
        expected_errors=(ValueError,),
    )


def fetch_with_one_transient_failure() -> str:
    attempts = {"count": 0}

    def action() -> str:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise TimeoutError("temporary timeout")
        return "ok"

    return retry_expected(action, attempts=2, expected_errors=(TimeoutError,))


def demo() -> None:
    print("Base URL:", load_required_base_url("https://tutorialsninja.com/demo/"))
    print("Parsed price:", parse_price("$602.00"))
    print("Transient fetch:", fetch_with_one_transient_failure())

    try:
        load_required_base_url("")
    except ConfigurationError as exc:
        print("Configuration error:", exc)


if __name__ == "__main__":
    demo()


__all__ = [
    "ConfigurationError",
    "ErrorContext",
    "ExternalServiceError",
    "FrameworkError",
    "fetch_with_one_transient_failure",
    "load_required_base_url",
    "parse_price",
    "require_value",
    "retry_expected",
    "safe_call",
]
