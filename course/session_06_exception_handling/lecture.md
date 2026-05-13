# Session 6 - Exception Handling: Clear Failures Without Hiding Bugs

## Learning Objectives

By the end of this session you will be able to:

- Explain the difference between expected framework failures and programmer errors.
- Create custom exception types for configuration, test data, and external services.
- Preserve the original exception with `raise ... from exc`.
- Catch only the errors you can handle.
- Add useful context to failures without swallowing the real stack trace.
- Retry only known transient errors.

---

## Why Exception Handling Matters In Automation

Automation code fails for different reasons:

| Failure type | Example | Good behavior |
|---|---|---|
| Product failure | Checkout returns the wrong total | Let the test assertion fail. |
| Configuration failure | `BASE_URL` is missing | Raise a clear `ConfigurationError`. |
| Test data failure | Required user fixture is missing | Raise a clear `TestDataError`. |
| External dependency failure | API times out | Retry if known transient, then raise `ExternalServiceError`. |
| Programmer error | Page object calls `len(None)` | Do not hide it. Let the original error fail fast. |

The goal is not to make failures disappear. The goal is to make failures easier to diagnose.

---

## Custom Framework Exceptions

Use framework exceptions for errors the automation framework can describe better than Python can:

```python
class FrameworkError(Exception):
    """Base error for expected automation framework failures."""


class ConfigurationError(FrameworkError):
    """Raised when required local configuration is missing or invalid."""
```

This gives reports and logs a stable vocabulary.

---

## Catch Specific Exceptions

Weak:

```python
try:
    price = float(raw_price)
except Exception:
    price = 0.0
```

This hides bugs and may make a broken test pass.

Better:

```python
try:
    price = float(raw_price)
except ValueError as exc:
    raise FrameworkError(f"Could not parse price: {raw_price}") from exc
```

The test still fails, but the failure explains the automation problem.

---

## Preserve The Original Cause

Always use `raise ... from exc` when translating a lower-level error:

```python
raise ConfigurationError("Missing required value: BASE_URL") from exc
```

This keeps the original traceback available for debugging.

---

## Retry Only Known Transient Errors

Retries are useful for network timeouts and known temporary service errors. They are harmful when used for assertions, locator mistakes, or data bugs.

Use retry rules like this:

```python
retry_expected(action, attempts=2, expected_errors=(TimeoutError,))
```

Do not retry every exception type.

---

## Runnable Example

```bash
python course/session_06_exception_handling/lecture.py
pytest course/session_06_exception_handling -q
```

The reusable implementation lives in `course/framework/exceptions/`.

---

## Session Completion Checklist

- [ ] I created at least one custom framework exception.
- [ ] I replaced a broad `except Exception` with a specific exception type.
- [ ] I used `raise ... from exc` when translating an error.
- [ ] I explained which errors should not be caught.
- [ ] I completed the exercises in `EXERCISES.md`.
