# STD-CONTRACT: Contract Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Contract Tests |
| Feature | Contract Tests |
| Marker | `contract` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate stable structural contracts of the store's HTTP responses: page availability, required HTML markers, product field shape, price positivity, and cart total consistency.

## Preconditions
- The TutorialsNinja demo store is reachable at the configured base URL.
- Each test uses a fresh HTTP session.
- No browser is required.

## Test Cases — Public Endpoint Contract (`TestPublicEndpointContract`)

### TC-CONTRACT-PUBLIC-01: Mapped Public Endpoints Return OK and Expected Page Markers (Parametrised)
**Severity:** Critical  
**Parameters:** `home`, `search`, `cart`, `register`, `login` (defined in `PUBLIC_ENDPOINT_MAP`)

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET the endpoint path for the parameter. | Path and required text from `PUBLIC_ENDPOINT_MAP`. | HTTP 200 returned. |
| 2 | Assert the required text marker is present in the response HTML. | Required text from map entry. | Marker found in HTML. |

---

## Test Cases — Search Response Contract (`TestSearchContract`)

### TC-CONTRACT-SEARCH-01: Mapped Search Queries Return Expected Product Cards (Parametrised)
**Severity:** Critical  
**Parameters:** `macbook` → `MacBook`, `iphone` → `iPhone` (defined in `SEARCH_QUERY_MAP`)

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for the mapped query. | Query and expectations from `SEARCH_QUERY_MAP`. | HTTP 200. |
| 2 | Assert the card count meets the `min_cards` threshold. | `min_cards` from map entry. | Count ≥ minimum. |
| 3 | Assert every expected product name appears in the response text. | `expected_names` from map entry. | All names present. |

---

### TC-CONTRACT-SEARCH-02: Search Results Contain Product Names and Prices
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `MacBook`. | Query: `MacBook` | HTTP 200. |
| 2 | Assert at least one product name is parsed. | N/A | Names list non-empty. |
| 3 | Assert at least one parseable price is present. | N/A | Prices list non-empty. |

---

### TC-CONTRACT-SEARCH-03: Non-Existent Query Returns No Product Cards
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for a nonsense query. | Query: `xyznonexistent<uuid>` | HTTP 200. |
| 2 | Assert no product cards are present. | N/A | Cards list is empty. |

---

### TC-CONTRACT-SEARCH-04: Search Result Product IDs Are Parseable Integers
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `Apple`. | Query: `Apple` | HTTP 200. |
| 2 | Assert at least one product ID is returned and every ID is a digit string. | N/A | All IDs are `isdigit()`. |

---

## Test Cases — Registration Page Contract (`TestRegistrationPageContract`)

### TC-CONTRACT-REG-01: Registration Page Returns OK and Contains All Required Field IDs
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET the registration page. | `/index.php?route=account/register` | HTTP 200. |
| 2 | Assert all six required `id` attributes exist in the HTML: `input-firstname`, `input-lastname`, `input-email`, `input-telephone`, `input-password`, `input-confirm`. | N/A | No required IDs missing. |

---

### TC-CONTRACT-REG-02: Registration Page Contains Privacy Policy Checkbox
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET the registration page. | `/index.php?route=account/register` | HTTP 200. |
| 2 | Assert `name="agree"` is present in the HTML. | N/A | Checkbox present. |

---

## Test Cases — Price Data Integrity (`TestPriceContract`)

### TC-CONTRACT-PRICE-01: All Prices in Search Results Are Positive
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `MacBook`. | Query: `MacBook` | HTTP 200. |
| 2 | Parse all prices from the HTML. | N/A | At least one price found. |
| 3 | Assert no price is ≤ 0. | N/A | All prices > 0. |

---

### TC-CONTRACT-PRICE-02: Cart Total Matches Sum of Individual Item Row Prices
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find a product ID from the configured search query. | `data/test_data.json` search query. | ID resolved. |
| 2 | POST the product to the cart. | N/A | HTTP 200. |
| 3 | GET the cart page and parse individual row prices and the grand total. | N/A | Both parsed successfully. |
| 4 | Assert `abs(row_sum - grand_total) < $1.00`. | N/A | Row sum and grand total are consistent. |

## Notes
- Tests are marked `@pytest.mark.contract`.
- `PUBLIC_ENDPOINT_MAP` and `SEARCH_QUERY_MAP` are defined in `tests/conftest.py` and drive parametrised cases.
