---
name: api-test
description: Conventions for writing or changing API behavior tests in this repo (tests/api/, service classes, rest_client, response constants). Use when adding or editing API tests.
---

# API Test Skill

- Put API behavior tests under `tests/api/`.
- Use service classes from `services/api/`; do not call `requests` directly in tests.
- Use `services/rest_client.py` for HTTP methods, retries, and timeouts.
- Use response constants from `services/api/http_response_constants.py`; do not hard-code response codes.
- Keep write operations idempotent or explicitly account for retries before enabling write retries.
