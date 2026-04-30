# STD-API-INTEGRATIONS: API Integration Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja API Integration |
| Feature | API Integration Tests |
| Marker | `api` |
| Priority | Medium |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Extend core API coverage with additional search and cart scenarios: multi-word queries, response structure validation, quantity edge cases, negative IDs, and cart state consistency across operations.

## Preconditions
- The TutorialsNinja demo store is reachable at the configured base URL.
- Each test uses a fresh HTTP session.
- No browser is required.

## Test Cases — Search Integration (`TestSearchApiIntegration`)

### TC-API-INT-SEARCH-01: Unknown Query Returns No Product Cards
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results with a randomly generated unknown query. | Query: `unknown-product-<uuid>` | HTTP 200 returned. |
| 2 | Assert no product cards are present in the response HTML. | N/A | Cards list is empty. |

---

### TC-API-INT-SEARCH-02: Search Product Names Are Non-Empty
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `iPod`. | Query: `iPod` | HTTP 200. |
| 2 | Assert at least one name is returned and every name has non-whitespace content. | N/A | All names are non-empty. |

---

### TC-API-INT-SEARCH-03: Product Cards Have Matching IDs and Names
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `MacBook`. | Query: `MacBook` | HTTP 200. |
| 2 | Assert card count, name count, and ID count all align (one name per card, at least one ID per card). | N/A | Counts are consistent. |

---

### TC-API-INT-SEARCH-04: Multi-Word Query Returns Expected Product
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `MacBook Pro`. | Query: `MacBook Pro` | HTTP 200. |
| 2 | Assert `MacBook Pro` is in the returned product names. | N/A | Product name found. |

---

### TC-API-INT-SEARCH-05: Search Page Exposes Refine-Search Controls
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET search results for `MacBook`. | Query: `MacBook` | HTTP 200. |
| 2 | Assert `id="input-search"`, `name="category_id"`, and `id="button-search"` are present in the HTML. | N/A | All three markers found. |

---

## Test Cases — Cart Integration (`TestCartApiIntegration`)

### TC-API-INT-CART-01: New API Session Starts With an Empty Cart
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | GET the cart page immediately after creating a fresh session. | N/A | HTTP 200. |
| 2 | Assert the cart page reports empty. | N/A | Cart is empty. |

---

### TC-API-INT-CART-02: Cart Total Is Positive After Adding Quantity > 1
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find the MacBook product ID. | Query: `MacBook` | ID resolved. |
| 2 | POST to cart/add with `quantity=2`. | `quantity: 2` | HTTP 200. |
| 3 | GET the cart page and assert parsed total > 0. | N/A | Total > 0. |

---

### TC-API-INT-CART-03: Cart Keeps Multiple Products in Same Session
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Add a MacBook and an iPhone to the same session cart. | Queries: `MacBook`, `iPhone` | Both POSTs return HTTP 200. |
| 2 | GET the cart page and assert the product row sum and grand total are both > 0. | N/A | Row sum > 0 and total > 0. |

---

### TC-API-INT-CART-04: Cart Add Response Contains Success Message and Total
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find MacBook product ID and POST to cart/add. | Query: `MacBook` | HTTP 200. |
| 2 | Parse the JSON response. | N/A | Response is a JSON object. |
| 3 | Assert `success` field exists and contains `MacBook`. | N/A | Success message present. |
| 4 | Assert `total` field exists and contains `item(s)`. | N/A | Total string present. |

---

### TC-API-INT-CART-05: Cart Add Response Total Matches Cart Page Total
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | POST MacBook with `quantity=2` to cart/add. | `quantity: 2` | HTTP 200. |
| 2 | Parse the `total` field from the add response. | N/A | Response total parsed. |
| 3 | GET the cart page and parse the grand total. | N/A | Page total parsed. |
| 4 | Assert page total equals response total. | N/A | Values match. |

---

## Test Cases — Cart Negative Scenarios (`TestCartApiNegative`)

### TC-API-INT-CART-NEG-01: Cart Add Ignores Missing or Unknown Product IDs (Parametrised)
**Severity:** Normal  
**Parameters:** `""` (empty string), `"999999"` (non-existent ID)

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | POST the invalid product_id to cart/add. | `product_id` from parameter. | HTTP 200 returned. |
| 2 | Assert response body is an empty JSON array `[]`. | N/A | Body is `[]`. |
| 3 | GET the cart page and assert it is empty. | N/A | Cart is empty. |

---

### TC-API-INT-CART-NEG-02: Cart Add With Non-Positive Quantity Does Not Add Items (Parametrised)
**Severity:** Normal  
**Parameters:** `quantity=0`, `quantity=-1`

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Find MacBook product ID. | Query: `MacBook` | ID resolved. |
| 2 | POST to cart/add with the given quantity. | `quantity` from parameter. | HTTP 200 returned. |
| 3 | Assert response contains `0 item(s)`. | N/A | Zero-item cart summary in response. |
| 4 | GET the cart page and assert it is empty. | N/A | Cart is empty. |

## Notes
- Tests are marked `@pytest.mark.api`.
