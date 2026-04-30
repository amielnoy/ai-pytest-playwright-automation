# STD-CART-TOTAL: Cart Total Validation Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Cart |
| Feature | Cart |
| Story | assertCartTotalNotExceeds |
| Marker | `cart` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that the cart total displayed in the browser does not exceed a configured maximum and is consistent with the individual product prices used to populate the cart.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- Cart is pre-populated via the `api_cart` fixture (REST API, no browser), which returns an `OCSESSID` cookie, the added products, and the configured `max_total` and `max_price`.
- The `OCSESSID` cookie is injected into the Playwright `BrowserContext` before any navigation.

## Test Cases

### TC-CART-TOTAL-01: Cart Total Does Not Exceed the Configured Maximum
**Objective:** The rendered cart grand total is at or below the `max_total` value from test data.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Inject the API session cookie into the browser context. | `OCSESSID` from `api_cart` fixture. | Cookie is set on the context. |
| 2 | Navigate to the cart page. | `/index.php?route=checkout/cart` | Cart page loads with the pre-populated items. |
| 3 | Read the cart grand total from the page. | N/A | Total is parsed as a float. |
| 4 | Assert `total <= max_total`. | `max_total` from `data/test_data.json` cart block. | Assertion passes. |

**Post-conditions:** No cart state is changed.

---

### TC-CART-TOTAL-02: Cart Total Is Consistent With Item Prices
**Objective:** The grand total does not exceed `max_price × item count` — a theoretical upper bound.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Inject the API session cookie into the browser context. | `OCSESSID` from `api_cart` fixture. | Cookie is set on the context. |
| 2 | Navigate to the cart page. | `/index.php?route=checkout/cart` | Cart page loads. |
| 3 | Read the cart grand total. | N/A | Total is parsed as a float. |
| 4 | Compute upper bound: `max_price × len(products)`. | `max_price` and product list from `api_cart` fixture. | Bound is calculated. |
| 5 | Assert `total <= upper_bound`. | N/A | Assertion passes. |

**Post-conditions:** No cart state is changed.

## Notes
- Tests are marked `@pytest.mark.cart`.
- Cart setup uses the REST API, not the browser, to keep the test fast and reduce flakiness.
- Cookie injection must happen **before** `cart_page.open()` to take effect on the first request.
