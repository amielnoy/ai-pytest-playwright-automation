"""Exception handling helpers added in Session 6."""

from course.framework.exceptions.handling import (
    ConfigurationError,
    ErrorContext,
    ExternalServiceError,
    FrameworkError,
    TestDataError,
    require_value,
    retry_expected,
    safe_call,
)

__all__ = [
    "ConfigurationError",
    "ErrorContext",
    "ExternalServiceError",
    "FrameworkError",
    "TestDataError",
    "require_value",
    "retry_expected",
    "safe_call",
]
