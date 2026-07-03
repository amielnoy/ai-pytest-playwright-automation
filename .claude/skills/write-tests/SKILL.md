---
name: write-tests
description: Turn an STD (stds/*.md) into a runnable pytest + Playwright test in tests/web-ui/, following the project's Page Object Model, fixtures, Allure and marker conventions. Use after planning, when the user wants tests written from a plan.
---

# Write tests from an STD

**Input:** an STD in `stds/` (the planner's output).
**Output:** `tests/web-ui/test_<feature>.py`.

## Preferred: run the writer agent
Needs `ANTHROPIC_API_KEY` in `.env`. From the repo root:

```bash
python -m agents.test_writer_agent STD_Login.md   # one STD
python -m agents.test_writer_agent               # all STDs
```

## Or do it directly (must follow every project convention)
- **No raw selectors in tests.** Drive the browser only through Page Object business methods in `pages/`. If the STD needs an interaction no Page Object exposes, add a short comment noting it — do not invent selectors inline.
- Use the shared fixtures from `conftest.py` (browser/context/page + page-object fixtures); prefer API setup fixtures (e.g. `api_cart`) when UI setup would be slow or flaky.
- Decorate every test with `@allure.feature/.story/.title/.severity` and wrap steps in `with allure.step(...)`.
- Tag with the correct marker (`registration`/`search`/`cart`/`api`/`contract`/`sanity`) matching the STD's Marker field.
- Read test data via `utils/data_loader.get_test_data` — never hard-code credentials.
- Mirror the structure/imports of the existing `tests/web-ui/` files, then validate: `pytest --collect-only tests/web-ui/test_<feature>.py`.

Next stage: **heal-test** fixes it if it later fails.
