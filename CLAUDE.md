# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Playwright-based UI automation test suite for the [TutorialsNinja demo e-commerce site](https://tutorialsninja.com/demo). Uses pytest with the Page Object Model (POM) pattern and Allure for reporting.

## Commands

**Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

**Run all tests:**
```bash
pytest
```

**Run by marker:**
```bash
pytest -m registration
pytest -m search
pytest -m cart
pytest -m api
pytest -m contract
```

**Run a single test file or test:**
```bash
pytest tests/web-ui/test_registration.py
pytest tests/web-ui/test_registration.py::TestRegistration::test_register_new_user
```

**Run by test layer:**
```bash
pytest tests/unit
pytest tests/api
pytest tests/contract
pytest tests/web-ui
```

**Run tests with Docker:**
```bash
docker build -t ness-automation-tests .
docker run --rm -v "$PWD/docker-artifacts:/app/test-artifacts" \
  ness-automation-tests pytest tests/ --alluredir=/app/test-artifacts/allure-results
```

**Generate and view Allure report:**
```bash
npm run allure:generate
npm run allure:open
```

## Claude Skills

Use these repo-specific skills when changing code:

### UI Test Skill

- Put browser tests under `tests/web-ui/`.
- Use page objects from `pages/`; do not put Playwright selectors directly in tests.
- Add page behavior to the relevant page/component class before adding assertions in tests.
- Use fixtures from root `conftest.py` for browser, context, page, and page objects.
- Keep tests isolated; use API setup fixtures such as `api_cart` when UI setup would be slow or flaky.

### API Test Skill

- Put API behavior tests under `tests/api/`.
- Use service classes from `services/api/`; do not call `requests` directly in tests.
- Use `services/rest_client.py` for HTTP methods, retries, and timeouts.
- Use response constants from `services/api/http_response_constants.py`; do not hard-code response codes.
- Keep write operations idempotent or explicitly account for retries before enabling write retries.

### Contract Test Skill

- Put API/page structure contract tests under `tests/contract/`.
- Validate stable contracts: status codes, required fields, parseable product IDs, prices, and page markers.
- Keep contract cases map-driven when multiple endpoints or queries share the same assertion shape.
- Do not import reusable data from `conftest.py`; move shared cases to a normal module if they grow.

### Unit Test Skill

- Put fast unit tests under `tests/unit/`.
- Mock network/session boundaries for utility and REST client behavior.
- Unit tests should not require Playwright, Docker, secrets, or external network access.

### DevOps Skill

- Keep Docker, README commands, and GitHub Actions aligned.
- If Docker is changed, verify with `docker build` and a containerized `pytest` run.
- Keep generated outputs out of git: `allure-results/`, `allure-report/`, `docker-artifacts/`, caches, and secrets.
- Prefer pinned dependency versions for reproducible CI.

### Review Skill

- Prioritize test isolation, flake risk, CI reproducibility, secret handling, retry safety, and report/debug quality.
- Review findings should include file and line references, severity, impact, and a concrete fix.
- Run collection before broad execution: `pytest --collect-only -q`.

## Architecture

### Page Object Model

All page interactions live in `pages/`. Every page class extends `BasePage` (`pages/base_page.py`), which provides shared navigation, title/URL accessors, and screenshot helpers.

| Page class | Responsibility |
|---|---|
| `HomePage` | Search, nav to login/register, logout, login status |
| `RegisterPage` | Registration form submission and validation errors |
| `LoginPage` | Login form submission and success/error checks |
| `SearchResultsPage` | Product parsing, price filtering, add-to-cart |
| `CartPage` | Cart contents, total calculation, empty cart detection |

### Test Data & Configuration

- **`config/config.json`** — Browser settings (`headless`, `slow_mo`, `timeout`, viewport). Set `headless: true` for CI.
- **`data/test_data.json`** — All test inputs (credentials, search queries, price limits). Supports a `{ts}` placeholder that `data_loader.get_test_data()` resolves to a Unix timestamp at load time, ensuring unique email addresses per run.
- **`utils/data_loader.py`** — `get_config()` and `get_test_data(key)` are the only entry points for loading external data; never read config/data files directly in tests.

### Fixtures (`conftest.py`)

| Fixture | Scope | Purpose |
|---|---|---|
| `browser_instance` | session | Single Chromium browser for the entire run |
| `context` | request | Fresh browser context per test |
| `page` | function | New page per test |
| `app_url` | function | Base URL from config |

A `pytest_runtest_makereport` hook automatically attaches a screenshot to the Allure report on test failure.

### API Service Layer

All API tests should go through:

- `services/rest_client.py` — shared REST client with `get`, `post`, `put`, `delete`, retries, and default timeout.
- `services/api/search_service.py` — search endpoint and search HTML parsing.
- `services/api/cart_service.py` — cart add/fetch and cart total parsing.
- `services/api/account_service.py` — account/registration page endpoints.
- `services/api/public_service.py` — generic public endpoint checks.

### Test Markers

Tests must be tagged with the relevant marker: `registration`, `search`, `cart`, `api`, or `contract`. Markers are defined in `pytest.ini`.

### Allure Decorators

All tests use Allure decorators for structured reporting:
- `@allure.feature` / `@allure.story` / `@allure.title` / `@allure.severity`
- `with allure.step(...)` wraps logical steps inside test functions

Follow this pattern when adding new tests.
