# STD-UNIT: Unit Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Unit Tests |
| Feature | Unit — Page Objects, REST Client, FastAPI Server |
| Priority | High |
| Author | QA Agent |
| Date | 2026-05-28 |

## Objective
Verify internal logic of page objects, components, the REST client wrapper, the internal FastAPI server, and test data factories without requiring a browser, live network, or Docker. Factory tests cover correctness, uniqueness, field limits, password complexity, telephone format, DIP/OCP compliance, seeded reproducibility, and cross-factory isolation. All external dependencies are mocked.

## Preconditions
- No browser, network, or Docker required.
- `pytest` can import all page and service modules.

---

## REST Client (`test_rest_client.py`)

### TC-UNIT-REST-01: HTTP Methods Delegate to `request` With Default Timeout
**Objective:** `get`, `post`, `put`, and `delete` all pass the correct method string, URL, and default timeout to the underlying session.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create `RestClient(timeout=7)` and replace session with a `FakeSession`. | Client configured. |
| 2 | Call `get`, `post`, `put`, `delete` in sequence. | Each call recorded by FakeSession. |
| 3 | Assert recorded calls match expected method, URL, and `timeout=7`. | Exact match. |

---

### TC-UNIT-REST-02: Per-Request Timeout Overrides Default
**Objective:** Passing `timeout=30` to `get` replaces the default.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create `RestClient(timeout=7)` with a FakeSession. | Client configured. |
| 2 | Call `client.get(url, timeout=30)`. | Call recorded. |
| 3 | Assert recorded timeout is `30`, not `7`. | Override takes effect. |

---

## Page Objects (`test_page_objects.py`)

### TC-UNIT-PO-01: `BaseComponent` Stores Page Reference
### TC-UNIT-PO-02: `BasePage.navigate` Builds Correct URLs (Base and Relative)
### TC-UNIT-PO-03: `BasePage` Exposes Title, URL, Screenshot, and Alert Error
### TC-UNIT-PO-04: `BasePage.wait_for_visible` Uses First-Matching Locator
### TC-UNIT-PO-05: `BasePage` Accessibility Helpers Use Class Locators
### TC-UNIT-PO-06: `HomePage` Delegates Navigation and Nav Actions
### TC-UNIT-PO-07: `HomePage` Accessibility Helpers Delegate to Nav and Image Locator
### TC-UNIT-PO-08: `CartPage` Delegates to Summary Component
### TC-UNIT-PO-09: `RegisterPage` Delegates Full Registration Flow to Form
### TC-UNIT-PO-10: `LoginPage` Open/Login/Status Checks Use Class Locators
### TC-UNIT-PO-11: `LoginPage` Accessibility Helpers Use Class Locators
### TC-UNIT-PO-12: `SearchResultsPage` Returns Empty When No-Results Message Is Visible
### TC-UNIT-PO-13: `SearchResultsPage` Filters Products Under Price and Respects Limit
### TC-UNIT-PO-14: `SearchResultsPage` Adds Items to Cart and Waits for Success Alert
### TC-UNIT-PO-15: `SearchResultsPage.open_product` Clicks Title Link in Matching Card
### TC-UNIT-PO-16: `SearchResultsPage` View, Sort, and Cards Helpers
### TC-UNIT-PO-17: `SearchResultsPage` Product Names, Sort Check, and Stored Information
### TC-UNIT-PO-18: `SearchResultsPage` Accessibility Helpers Use Class Locators
### TC-UNIT-PO-19: `AlertComponent` Returns Banner, Field Error, Success, and Waits
### TC-UNIT-PO-20: `AlertComponent` Prefers Visible Banner; Returns Empty Without Errors
### TC-UNIT-PO-21: `CartSummaryComponent` Reads Total, Count, and Empty State
### TC-UNIT-PO-22: `CartSummaryComponent` Returns 0.0 When Total Is Hidden or Unparseable
### TC-UNIT-PO-23: `NavBarComponent` Search, Currency, Login, Register, Logout, and Status
### TC-UNIT-PO-24: `NavBarComponent` Accessibility Helpers Use Class Locators
### TC-UNIT-PO-25: `RegistrationFormComponent` Fill, Accept, Submit, and Success State
### TC-UNIT-PO-26: `RegistrationFormComponent` Chooses "No" Newsletter by Default
### TC-UNIT-PO-27: `RegistrationFormComponent` Accessibility Helpers Use Class Locators
### TC-UNIT-PO-28: `ProductCardComponent` Reads Fields and Adds to Cart
### TC-UNIT-PO-29: `ProductCardComponent` Stored Info and Price Parse Error
### TC-UNIT-PO-30: `ProductDetailPage` Uses Class Locator Members

All page object cases follow the same pattern:

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Construct the component/page with a `MagicMock` page. | Object initialised. |
| 2 | Call the method under test. | Underlying Playwright APIs are invoked with the expected arguments. |
| 3 | Assert call arguments and return values match class-level locator constants. | Assertions pass without any real browser. |

---

## FastAPI Server (`test_fastapi_app.py`)

### TC-UNIT-SERVER-01: `/health` Returns `{"status": "ok"}`
### TC-UNIT-SERVER-02: `/automation/test-data/search` Returns Search Data
### TC-UNIT-SERVER-03: `/automation/test-data/<unknown>` Returns 404
### TC-UNIT-SERVER-04: `/reports/allure/status` Exposes Report URL
### TC-UNIT-SERVER-05: `/reports/allure/summary` Returns 404 When Summary File Is Missing
### TC-UNIT-SERVER-06: Mock Cart Flow (Search → Add → Fetch)
### TC-UNIT-SERVER-07: Mock Product Search Returns Matching Products (Parametrised: `MacBook`, `iPhone`)
### TC-UNIT-SERVER-08: Mock Cart Add Calculates Total From Quantity (Parametrised)
### TC-UNIT-SERVER-09: Mock Cart Add Returns 404 for Unknown Product
### TC-UNIT-SERVER-10: `/runs/pytest` Rejects Unsafe Arguments

All server cases use `fastapi.testclient.TestClient`; no real server process is started.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send the relevant HTTP request to the `TestClient`. | Response received. |
| 2 | Assert status code and JSON body match the expected contract. | Assertions pass. |

## Notes
- No markers are applied; these tests run with `pytest tests/unit`.
- All network and browser interactions are mocked.
- FastAPI tests use `monkeypatch` for file-path injection where needed.

---

## Factories (`test_factories.py`)

Tests for `utils/factories.py`. Cover all four public factory functions (`make_registration`, `make_search`, `make_cart_scenario`, `make_invalid_credentials`), the `FakerLike` protocol, and cross-cutting properties (isolation, seeding, field limits). No external network or browser is required.

---

### TC-UNIT-FACT-01: `TestMakeRegistration` — RegistrationData factory (13 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `all_fields_present` | Call `make_registration()` with no arguments. | All fields (`first_name`, `last_name`, `email`, `password`, `confirm_password`, `telephone`) are non-empty. |
| `password_matches_confirm` | Standard build, compare `password` and `confirm_password`. | Both fields are identical. |
| `email_format` | Check the email string against a regex. | Matches `auto+<8 hex chars>@example.com`. |
| `telephone_numeric` | Inspect the `telephone` field. | Exactly 10 decimal digits. |
| `emails_are_unique` | Generate 20 instances, collect emails into a set. | Set size is 20 (no duplicates). |
| `newsletter_defaults_false` | Read `newsletter` on a default build. | Value is `False`. |
| `override_first_name_blank` | Pass `first_name=""`. | `first_name` is `""`, all other required fields remain non-empty. |
| `override_last_name_blank` | Pass `last_name=""`. | `last_name` is `""`, `first_name` remains non-empty. |
| `override_email_blank` | Pass `email=""`. | `email` is `""`, `first_name` remains non-empty. |
| `override_password_blank` | Pass `password=""`. | `password` is `""`. |
| `override_telephone_blank` | Pass `telephone=""`. | `telephone` is `""`, `first_name` remains non-empty. |
| `asdict_has_all_keys` | Serialise via `dataclasses.asdict`. | Dict contains all seven expected keys; `first_name` and `email` values match the object. |
| `accepts_faker_like_injection` | Inject a seeded `Faker` instance (seed 42), build twice. | Both builds produce the same `email` (DIP compliance). |

---

### TC-UNIT-FACT-02: `TestMakeSearch` — SearchData factory (7 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `fields_present` | Call `make_search()` with no arguments. | `query` is non-empty, `max_price > 0`, `limit >= 1`. |
| `override_query` | Pass `query="iPhone"`. | Returned `query` is exactly `"iPhone"`. |
| `override_max_price` | Pass `max_price=499.99`. | Returned `max_price` is `499.99`. |
| `override_limit` | Pass `limit=3`. | Returned `limit` is `3`. |
| `max_price_in_range` | Generate 20 instances, check `max_price`. | All values satisfy `200 ≤ max_price ≤ 2000`. |
| `limit_in_range` | Generate 20 instances, check `limit`. | All values satisfy `1 ≤ limit ≤ 10`. |
| `custom_products_pool` | Pass a custom two-element `products` tuple, generate 20 instances. | Every `query` is one of the supplied products (OCP compliance). |

---

### TC-UNIT-FACT-03: `TestMakeCartScenario` — CartScenario factory (3 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `fields_present` | Call `make_cart_scenario()` with no arguments. | `query`, `max_price`, `limit`, and `max_total` are all populated and positive. |
| `max_total_exceeds_item_price` | Compare `max_total` and `max_price` on a default build. | `max_total > max_price`. |
| `overrides_forwarded` | Pass `query="iPhone"` and `max_price=300.0`. | `query` is `"iPhone"` and `max_price` is `300.0`. |

---

### TC-UNIT-FACT-04: `TestMakeInvalidCredentials` — LoginCredentials factory (4 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `fields_present` | Call `make_invalid_credentials()` with no arguments. | Both `email` and `password` are non-empty strings. |
| `email_domain` | Inspect the email domain. | Contains `@nowhere.example` to prevent accidental real-account matches. |
| `emails_are_unique` | Generate 20 instances, collect emails into a set. | Set size is 20 (no duplicates). |
| `password_length` | Generate 10 instances, check length. | Every password is at least 8 characters. |

---

### TC-UNIT-FACT-05: `TestFakerLikeProtocol` — FakerLike structural check (1 case)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `faker_has_all_protocol_methods` | Use `hasattr` to verify the required methods on a `Faker` instance. | All eight required methods (`first_name`, `last_name`, `password`, `numerify`, `uuid4`, `random_element`, `pyfloat`, `random_int`) are present. |

---

### TC-UNIT-FACT-06: `TestRegistrationPasswordComplexity` — Password quality (4 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `password_min_length` | Generate 10 passwords, check length. | All passwords are at least 12 characters long. |
| `password_has_uppercase` | Generate 10 passwords, scan for uppercase. | Every password contains at least one uppercase letter. |
| `password_has_digit` | Generate 10 passwords, scan for digits. | Every password contains at least one digit. |
| `password_has_special_char` | Generate 10 passwords, scan for special characters. | Every password contains at least one character from the defined special-character set. |

---

### TC-UNIT-FACT-07: `TestRegistrationFieldLimits` — Field length constraints (3 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `first_name_max_length` | Generate 20 instances, check `len(first_name)`. | All values ≤ 32 characters (OpenCart limit). |
| `last_name_max_length` | Generate 20 instances, check `len(last_name)`. | All values ≤ 32 characters. |
| `email_max_length` | Generate 20 instances, check `len(email)`. | All values ≤ 96 characters. |

---

### TC-UNIT-FACT-08: `TestTelephoneFormat` — Telephone format validation (2 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `starts_with_05` | Generate 20 telephones, check prefix. | Every telephone starts with `"05"` (Israeli mobile format). |
| `exactly_ten_digits` | Generate 20 telephones, check content and length. | Every telephone is all digits and exactly 10 characters long. |

---

### TC-UNIT-FACT-09: `TestParametrizedMissingFields` — Parametrised blank-field isolation (5 parametrised cases)

One test method (`test_blank_field_is_isolated`) is parametrised over `["first_name", "last_name", "email", "password", "telephone"]`.

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call `make_registration(**{field: ""})` for each parameter value. | The targeted field is `""`. |
| 2 | Assert all other non-password text fields remain non-empty. | No collateral blanking occurs. |

---

### TC-UNIT-FACT-10: `TestFactoryIsolation` — Statelessness and cross-factory uniqueness (3 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `no_shared_state_registration` | Generate 50 registration emails. | All 50 are distinct. |
| `no_shared_state_credentials` | Generate 50 invalid-credentials emails. | All 50 are distinct. |
| `cross_factory_no_email_collision` | Generate 20 registration emails and 20 credentials emails. | The two sets are completely disjoint. |

---

### TC-UNIT-FACT-11: `TestSearchProductCoverage` — Known-product reachability (2 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `all_known_products_reachable` | Generate 200 `make_search()` calls, collect `query` values. | The result set is a superset of `_KNOWN_PRODUCTS`. |
| `single_product_pool` | Pass a single-element `products` tuple, generate 10 instances. | Every `query` equals the sole product in the pool. |

---

### TC-UNIT-FACT-12: `TestCartScenarioMath` — max_total arithmetic (3 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `max_total_is_5x_max_price` | Generate 20 scenarios, check the ratio. | `max_total == round(max_price * 5, 2)` for every scenario. |
| `override_max_price_recalculates_max_total` | Pass `max_price=100.0`. | `max_total` is `500.0`. |
| `max_total_always_exceeds_item_price` | Generate 20 scenarios. | `max_total > max_price` in every case. |

---

### TC-UNIT-FACT-13: `TestCrossFactorySeeding` — Seeded reproducibility (3 cases)

| Case | Description | Expected Result |
|------|-------------|-----------------|
| `seeded_registration_is_reproducible` | Inject `Faker` seeded with `99`, build twice. | Both `RegistrationData` emails are identical. |
| `seeded_search_is_reproducible` | Inject `Faker` seeded with `77`, build twice. | Both `SearchData` queries are identical. |
| `seeded_credentials_are_reproducible` | Inject `Faker` seeded with `55`, build twice. | Both `LoginCredentials` emails are identical. |

---

### Shared Test Pattern

All factory tests follow this pattern:

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Call the factory function (with or without overrides / a seeded `Faker`). | A typed dataclass instance is returned. |
| 2 | Assert field values, lengths, formats, or set sizes against documented constraints. | All assertions pass without any network, browser, or external process. |
