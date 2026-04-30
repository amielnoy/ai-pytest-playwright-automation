# STD-API: Core API Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja API |
| Feature | API Tests |
| Marker | `api` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate the core behaviour of the search and cart REST endpoints: correct HTTP status codes, expected product data in responses, session cookie issuance, and cart isolation between sessions.

## Preconditions
- The TutorialsNinja demo store is reachable at the configured base URL.
- Each test uses a fresh HTTP session with its own `OCSESSID` (no shared cart state).
- No browser is required; tests use `RestClient` directly.

## Test Cases — Search Endpoint (`TestSearchApi`)

### TC-API-SEARCH-01: Search Returns 200 and Non-Empty Product Cards
**Objective:** A GET to the search endpoint for a known query returns HTTP 200 and includes parseable product card elements.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `MacBook`. | Query: `MacBook` | Response received. |
| 2 | Assert HTTP 200. | N/A | Status is 200. |
| 3 | Assert at least one product card is present in the HTML. | N/A | Product cards list is non-empty. |

---

### TC-API-SEARCH-02: Search Returns Expected Product Names (Parametrised)
**Severity:** Critical  
**Parameters:** `MacBook` → `MacBook`, `iPhone` → `iPhone`

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for the query. | Query from parameter. | Response received. |
| 2 | Assert HTTP 200 and the expected product name appears in the parsed names. | Expected name from parameter. | Name is present. |

---

### TC-API-SEARCH-03: Search Returns Positive Prices (Parametrised)
**Severity:** Normal  
**Parameters:** `MacBook`, `iPhone`

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for the query. | Query from parameter. | Response received. |
| 2 | Assert HTTP 200, at least one price is parsed, and all prices are > 0. | N/A | All prices positive. |

---

### TC-API-SEARCH-04: Search Returns Numeric Product IDs (Parametrised)
**Severity:** Normal  
**Parameters:** `MacBook`, `iPhone`

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for the query. | Query from parameter. | Response received. |
| 2 | Assert HTTP 200, at least one product ID is found, and all IDs consist only of digits. | N/A | All IDs are digit strings. |

---

## Test Cases — Cart Endpoint (`TestCartApi`)

### TC-API-CART-01: Cart Add Returns OK and Issues OCSESSID Cookie
**Objective:** A POST to cart/add returns HTTP 200 and the server sets the session cookie.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find the first MacBook product ID from the search endpoint. | Query: `MacBook` | Product ID resolved. |
| 2 | POST the product ID to cart/add. | `product_id` from step 1. | HTTP 200 returned. |
| 3 | Assert `OCSESSID` cookie is present in the session. | N/A | Cookie exists. |

---

### TC-API-CART-02: Cart Page Reflects Product Added via API
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find MacBook product ID and POST it to cart/add. | Query: `MacBook` | Product added. |
| 2 | GET the cart page with the same session. | N/A | Cart page returned. |
| 3 | Assert cart is not empty. | N/A | Cart is non-empty. |
| 4 | Assert cart total is parseable and > 0. | N/A | Total > 0. |

---

### TC-API-CART-03: Cart Accepts Products From Known Search Results (Parametrised)
**Severity:** Normal  
**Parameters:** `MacBook`, `iPhone`

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find first product ID for the query. | Query from parameter. | Product ID resolved. |
| 2 | POST product ID to cart/add. | N/A | HTTP 200 returned. |
| 3 | GET the cart page and assert it is not empty. | N/A | Cart is non-empty. |

---

### TC-API-CART-04: Two Concurrent Sessions Have Independent Carts
**Objective:** Adding a product in session A does not affect session B.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Create session A and session B independently. | N/A | Two separate sessions. |
| 2 | Add a MacBook to session A's cart. | Query: `MacBook` | Product added to A. |
| 3 | Initialise session B (GET base URL to receive cookie). | N/A | Session B has its own OCSESSID. |
| 4 | GET the cart page from session B. | N/A | Session B cart is empty. |
| 5 | Assert session A and B OCSESSID values are different. | N/A | IDs differ. |

## Notes
- Tests are marked `@pytest.mark.api`.
- Parametrised tests generate one result per parameter value in the Allure report.
