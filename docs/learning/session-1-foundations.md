# Session 1 — Foundations: Playwright, POM & Fixtures (90 min)

**Audience:** QA engineers new to automation.
**Goal:** By the end, every attendee has run the UI suite, can read a test end-to-end (test → fixture → page object → config/data), and has written one new assertion.

## Agenda

### 1. Why this framework exists (10 min)

- The system under test: https://tutorialsninja.com/demo (e-commerce demo).
- The test pyramid in this repo: `tests/unit` → `tests/api` → `tests/contract` → `tests/web-ui`. Show the folder tree; explain why UI tests are the fewest and slowest.
- Live demo: `pytest tests/web-ui/test_registration.py -q` (set `"headless": false` in `config/config.json` so the browser is visible).

### 2. Anatomy of one test (20 min)

Walk through `tests/web-ui/test_registration.py::test_register_new_user` line by line:

- `@pytest.mark.registration` — markers in `pytest.ini`; run subsets with `pytest -m registration`.
- `@allure.feature / @allure.story / @allure.title / @allure.severity` — reporting metadata.
- `with allure.step(...)` — logical steps that appear in the report.
- The test contains **no selectors** — everything goes through page objects.

### 3. Page Object Model (20 min)

- `pages/base_page.py` — shared navigation, title/URL accessors, screenshot helpers. Every page extends it.
- `pages/home_page.py`, `pages/register_page.py` — locators live here, once, with behavior methods (`go_to_register()`, `register(...)`).
- Rule: **selectors never appear in tests.** Show what happens when the site changes: fix one line in the page object vs. twenty tests.
- Skim `pages/search_results_page.py` and `pages/cart_page.py` to show parsing and calculation logic belongs in the page layer too.

### 4. Fixtures & configuration (20 min)

Open root `conftest.py`:

- `browser_instance` (session scope) → `context` (per test) → `page` (per test): why isolation matters and why the browser is shared.
- `app_url` — base URL from `config/config.json` via `utils/data_loader.get_config()`. Never read config files directly in tests.
- `data/test_data.json` and the `{ts}` placeholder — unique emails per run via `get_test_data()`.
- `log` autouse fixture + `utils/logger.py` — `get_logger(name)` is the only logging entry point; logs are attached to Allure per test. No `print()`.
- The `pytest_runtest_makereport` hook — automatic failure screenshots.

### 5. Hands-on exercise (15 min)

Working in pairs:

1. Run `pytest tests/web-ui/test_search_under_price.py -q` and read the test + `SearchResultsPage` together.
2. Add one assertion to an existing test (e.g., verify page title after registration) using only page-object methods.
3. Stretch: add a new search query to `data/test_data.json` and re-run.

### 6. Wrap-up (5 min)

- Homework: run the full suite with `python3 -m pytest`, generate the report with `npm run allure:generate && npm run allure:open`, find your test in it.
- Preview Session 2: the layers below the UI.

## Instructor checklist

- [ ] tutorialsninja.com/demo is reachable (there is a fallback route handler in `conftest.py`, but verify).
- [ ] `config/config.json` set to headed mode for demos.
- [ ] Everyone completed the prerequisites (`pytest tests/unit -q` passes).
