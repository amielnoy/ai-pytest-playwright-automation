"""
Session 6 - exception handling layer for the teaching framework.

The goal is to keep failures explicit and actionable without hiding test
failures behind broad ``except Exception`` blocks.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


class FrameworkError(Exception):
    """Base error for expected automation framework failures."""


class ConfigurationError(FrameworkError):
    """Raised when required local configuration is missing or invalid."""


class TestDataError(FrameworkError):
    """Raised when test data cannot support the requested test scenario."""


class ExternalServiceError(FrameworkError):
    """Raised when an external dependency returns an unusable response."""


@dataclass(frozen=True)
class ErrorContext:
    """Small structured context object for logging and reporting failures."""

    operation: str
    target: str
    details: str = ""

    def message(self) -> str:
        suffix = f" ({self.details})" if self.details else ""
        return f"{self.operation} failed for {self.target}{suffix}"


def require_value(value: T | None, name: str) -> T:
    """Return a required value or raise a framework-level config error."""

    if value is None:
        raise ConfigurationError(f"Missing required value: {name}")
    if isinstance(value, str) and not value.strip():
        raise ConfigurationError(f"Missing required value: {name}")
    return value


def safe_call(
    action: Callable[[], T],
    context: ErrorContext,
    expected_errors: tuple[type[Exception], ...],
    wrapper: type[FrameworkError] = FrameworkError,
) -> T:
    """
    Run an action and translate only expected lower-level errors.

    Unexpected exceptions are allowed to escape with their original type because
    they usually represent a bug in the test or framework code.
    """

    try:
        return action()
    except expected_errors as exc:
        raise wrapper(f"{context.message()}: {exc}") from exc


def retry_expected(
    action: Callable[[], T],
    attempts: int,
    expected_errors: tuple[type[Exception], ...],
) -> T:
    """Retry only known transient errors and fail fast for programmer errors."""

    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return action()
        except expected_errors as exc:
            last_error = exc

    raise ExternalServiceError(f"Action failed after {attempts} attempts") from last_error
