---
name: unit-test
description: Conventions for writing or changing fast unit tests in this repo (tests/unit/, mocked boundaries, no Playwright/network/secrets). Use when adding or editing unit tests.
---

# Unit Test Skill

- Put fast unit tests under `tests/unit/`.
- Mock network/session boundaries for utility and REST client behavior.
- Unit tests should not require Playwright, Docker, secrets, or external network access.
