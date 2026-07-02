# Session 2 — Beyond the UI: API, Contract & Resilient Tests (90 min)

**Audience:** Attendees of Session 1.
**Goal:** Understand the full test pyramid in this repo, write an API test through the service layer, and learn the resilience patterns (self-healing locators, soft assertions, retries) that keep suites stable.

## Agenda

### 1. Recap & the cost of UI tests (5 min)

- Compare runtime: `pytest tests/unit -q` vs `pytest tests/web-ui -q`. Speed is the argument for testing below the UI.

### 2. The API service layer (25 min)

- `services/rest_client.py` — one shared client with `get/post/put/delete`, retries, and a default timeout. Tests never call `requests` directly.
- `services/api/search_service.py`, `cart_service.py`, `account_service.py` — endpoint knowledge and HTML parsing live here (the API-layer mirror of page objects).
- `services/api/http_response_constants.py` — no hard-coded status codes in tests.
- Walk through `tests/api/test_api.py` and `tests/api/test_api_data_driven.py`; show `@log_annotated_call` from `utils/logger.py` logging parametrized inputs.
- Fixtures in `tests/fixtures/services.py` — how service objects reach tests.

### 3. Contract tests (15 min)

- `tests/contract/test_contracts.py` — validating *stable contracts*: status codes, required fields, parseable product IDs and prices, page markers.
- Why they're map-driven: one assertion shape, many endpoints. Contrast with functional API tests.
- Discussion: what breaks a contract test vs. a UI test? Which failure tells you more?

### 4. Unit tests & mocking boundaries (10 min)

- `tests/unit/test_rest_client.py`, `test_price_parser` cases in `tests/unit/` — mock the network/session boundary, no Playwright, no Docker, no secrets.
- `utils/price_parser.py` and `utils/factories.py` as examples of logic worth unit-testing in isolation.

### 5. Resilience patterns (20 min)

- **Self-healing locators:** `pages/self_healing.py` — deterministic fallback locators owned by the page object; every healed lookup is recorded as a `SelfHealEvent` for selector cleanup. No AI guessing. See `tests/unit/test_self_healing.py`.
- **Soft assertions:** `tests/web-ui/test_soft_assertions_demo.py` — collect multiple failures in one run.
- **Flakiness:** `tests/unit/test_flaky_demo.py` — what flaky looks like and why retries on write operations are dangerous (idempotency rule from the API skill).
- **API setup for UI tests:** using service-layer setup (e.g., cart via API) instead of slow/flaky UI setup.

### 6. Hands-on exercise (10 min)

1. Add one data-driven case to `tests/api/test_api_data_driven.py` (new search query) using the existing service class.
2. Stretch: add a fallback locator to one element in a page object via `SelfHealingLocator` and prove it heals by breaking the primary selector.

### 7. Wrap-up (5 min)

- Homework: run `pytest tests/web-ui/test_intentional_failure.py`, then `npm run allure:generate && npm run allure:open` — study the failure screenshot and attached logs. Keep the `allure-results` for Session 3.
- Preview Session 3: AI as the thing under test, and AI as the tester.

## Instructor checklist

- [ ] Attendees kept a failing run's `allure-results/` (needed in Session 3 for the failure agent demo).
- [ ] Review pinned-dependency point in `requirements.txt` if CI reproducibility comes up.
