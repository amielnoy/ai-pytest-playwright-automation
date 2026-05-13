from __future__ import annotations

import pytest

from course.framework.exceptions import (
    ConfigurationError,
    ErrorContext,
    ExternalServiceError,
    FrameworkError,
    require_value,
    retry_expected,
    safe_call,
)


def test_require_value_returns_present_value() -> None:
    assert require_value("https://example.com", "BASE_URL") == "https://example.com"


def test_require_value_rejects_missing_strings() -> None:
    with pytest.raises(ConfigurationError, match="BASE_URL"):
        require_value("  ", "BASE_URL")


def test_safe_call_wraps_expected_error_with_context() -> None:
    with pytest.raises(FrameworkError, match="Parse price failed for N/A"):
        safe_call(
            lambda: float("N/A"),
            ErrorContext("Parse price", "N/A"),
            expected_errors=(ValueError,),
        )


def test_safe_call_does_not_hide_unexpected_errors() -> None:
    with pytest.raises(TypeError):
        safe_call(
            lambda: len(None),  # type: ignore[arg-type]
            ErrorContext("Read length", "value"),
            expected_errors=(ValueError,),
        )


def test_retry_expected_retries_known_transient_error() -> None:
    attempts = {"count": 0}

    def action() -> str:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise TimeoutError("temporary")
        return "ok"

    assert retry_expected(action, attempts=2, expected_errors=(TimeoutError,)) == "ok"
    assert attempts["count"] == 2


def test_retry_expected_raises_framework_error_after_attempts() -> None:
    with pytest.raises(ExternalServiceError, match="2 attempts"):
        retry_expected(
            lambda: (_ for _ in ()).throw(TimeoutError("still down")),
            attempts=2,
            expected_errors=(TimeoutError,),
        )
