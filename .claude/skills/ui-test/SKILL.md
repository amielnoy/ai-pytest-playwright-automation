---
name: ui-test
description: Conventions for writing or changing Playwright browser/UI tests in this repo (tests/web-ui/, Page Object Model, shared fixtures). Use when adding or editing UI tests.
---

# UI Test Skill

- Put browser tests under `tests/web-ui/`.
- Use page objects from `pages/`; do not put Playwright selectors directly in tests.
- Add page behavior to the relevant page/component class before adding assertions in tests.
- Use fixtures from root `conftest.py` for browser, context, page, and page objects.
- Keep tests isolated; use API setup fixtures such as `api_cart` when UI setup would be slow or flaky.
