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
```

**Run a single test file or test:**
```bash
pytest tests/test_registration.py
pytest tests/test_registration.py::TestRegistration::test_register_new_user
```

**Generate and view Allure report:**
```bash
allure serve allure-results
```

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

- **`config/config.yaml`** — Browser settings (`headless`, `slow_mo`, `timeout`, viewport). Set `headless: true` for CI.
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

### Test Markers

Tests must be tagged with one of: `registration`, `search`, `cart`. Markers are defined in `pytest.ini`.

### Allure Decorators

All tests use Allure decorators for structured reporting:
- `@allure.feature` / `@allure.story` / `@allure.title` / `@allure.severity`
- `with allure.step(...)` wraps logical steps inside test functions

Follow this pattern when adding new tests.
