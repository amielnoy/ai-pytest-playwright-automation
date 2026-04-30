# STD-UNIT: Unit Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Unit Tests |
| Feature | Unit — Page Objects, REST Client, FastAPI Server |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Verify internal logic of page objects, components, the REST client wrapper, and the internal FastAPI server without requiring a browser, live network, or Docker. All external dependencies are mocked.

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
