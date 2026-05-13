# Session 9 - API Testing

## Learning Objectives

By the end of this session you will be able to:

- Design API tests that validate behavior, not only status codes.
- Separate smoke, contract, negative, state, and integration API coverage.
- Build service-layer clients so tests do not repeat request details.
- Assert response schema and business meaning clearly.
- Use session isolation for cart/account flows.
- Decide when an API test should replace slow UI setup.
- Add API results and response details to Allure reports safely.

---

## Why API Testing Matters

API tests sit between unit tests and browser tests. They are faster than UI tests and closer to real product behavior than mocks.

API tests are strong for:

- Endpoint availability.
- Search, filtering, and sorting behavior.
- Cart and account state changes.
- Validation errors.
- Response contracts.
- Cross-call flows such as search product -> add to cart -> verify cart.

API tests are weak for:

- Visual layout.
- Accessibility semantics.
- Browser-only behavior.
- User interaction timing.
- Client-side rendering bugs.

Use API tests to cover business behavior quickly, then keep a smaller number of UI tests for critical user journeys.

---

## API Test Types

| Type | Purpose | Example |
|---|---|---|
| Smoke | Confirm endpoint is reachable | `GET /search` returns 200 |
| Contract | Confirm response shape | Product has `product_id`, `name`, `price` |
| Negative | Confirm invalid input is handled | Cart ignores unknown product ID |
| State | Confirm write changed expected state | Add item creates cart session |
| Integration | Confirm multiple endpoints work together | Search product, add it, open cart |

---

## Project Pattern

The production framework already separates API concerns:

| Layer | Directory | Responsibility |
|---|---|---|
| HTTP transport | `services/rest_client.py` | Session, retries, cookies, timeout handling |
| API services | `services/api/` | Domain operations such as search, cart, account |
| API tests | `tests/api/` | Endpoint behavior and integration checks |
| Contract tests | `tests/contract/` | Stable response/page structure contracts |
| Test data | `data/test_data.json` | Queries, thresholds, limits |

Tests should call a service object instead of building raw request URLs in every test.

---

## What To Assert

A useful API assertion usually combines:

1. Status code.
2. Response body marker or JSON field.
3. Business rule.
4. State isolation or cookie behavior when relevant.

Example:

```python
response = search_service.search("MacBook")

assert response.status_code == 200
assert "MacBook" in response.text
assert response.elapsed.total_seconds() < 5
```

For JSON APIs:

```python
payload = response.json()

assert payload["product_id"] > 0
assert payload["name"]
assert payload["price"] >= 0
```

---

## Contract Assertions

Contract tests should be stable and intentionally narrow.

Good contract checks:

- Required fields exist.
- Field types are compatible.
- Required page markers exist in HTML.
- Product IDs are integers.
- Prices parse as positive numbers.

Poor contract checks:

- Exact full HTML equality.
- Every field in an internal payload.
- Dynamic timestamps without tolerance.
- Row order without a documented sort.

---

## Negative Testing

Negative API tests prove the server handles bad input safely.

Examples:

- Unknown product ID does not add to cart.
- Quantity `0` or `-1` is rejected or ignored.
- Missing required account fields return a validation response.
- Unknown search query returns no product cards.
- Unsafe query strings do not break the endpoint.

Every negative test should assert both:

- The response is controlled.
- The system state is not corrupted.

---

## Session Isolation

Cart and account tests often depend on cookies.

This project uses a fresh HTTP session per API test:

```python
@pytest.fixture
def session(api_base_url: str) -> RestClient:
    client = build_session()
    client.get(api_base_url)
    yield client
    client.close()
```

This prevents one test's cart from affecting another test's cart, including when running with `pytest-xdist`.

---

## API Setup For UI Tests

Use API setup when the UI path is not what the test is proving.

Example:

- A cart total UI test does not need to search and add products through the browser.
- It can create the cart through the API.
- Then it injects the session cookie into Playwright.
- The browser opens the cart page and verifies display behavior.

This makes tests faster and less flaky while preserving end-to-end confidence for the UI assertion.

---

## Running Examples

Run the lecture demo:

```bash
python course/session_09_api_testing/lecture.py
```

Run the session tests:

```bash
pytest course/session_09_api_testing -q
```

Run production API tests:

```bash
pytest tests/api -q
pytest tests/contract -q
```

---

## Session Completion Checklist

- [ ] I can explain the difference between API smoke, contract, negative, state, and integration tests.
- [ ] I wrote status, body, and business-rule assertions in one API test.
- [ ] I used a service object instead of raw request code in the test body.
- [ ] I tested at least one negative API scenario.
- [ ] I can explain how API setup can make UI tests faster.
- [ ] I ran the production API and contract tests.
