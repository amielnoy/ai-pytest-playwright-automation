# STD-ADD-TO-CART: Add Items to Cart Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Cart |
| Feature | Cart |
| Story | addItemsToCart |
| Marker | `cart` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that products matching a search query and price filter can be added to the cart via the browser UI, and that no items are added when the price filter matches nothing.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- `data/test_data.json` contains a `search` block with `query`, `max_price`, and `limit`.

## Test Cases

### TC-CART-ADD-01: Add Items Under max_price to Cart
**Objective:** Confirm products found under the configured price cap are successfully added to the cart.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Fetch products matching the configured query priced at or below `max_price`. | From `data/test_data.json` `search` block. | At least one product is returned. |
| 2 | Add each product to the cart via the Add to Cart button; wait for the success alert after each. | Products from step 1. | Each add triggers a success alert. |
| 3 | Assert the count of successfully added products equals the count of matching products. | N/A | Counts match. |
| 4 | Navigate to the cart page. | `/index.php?route=checkout/cart` | Cart page loads. |
| 5 | Assert the cart is not empty. | N/A | Cart contains items. |

**Post-conditions:** Cart contains the matched products.

---

### TC-CART-ADD-02: No Items Added When Nothing Matches the Price Filter
**Objective:** Confirm the search/add flow gracefully handles a result set with zero matching products.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Fetch products for `MacBook` priced at or below `$0.01`. | Query: `MacBook`, `max_price: 0.01`, `limit: 5` | Empty product list returned. |
| 2 | Assert the returned list is empty. | N/A | `products == []`. |

**Post-conditions:** Cart remains empty.

## Notes
- Tests are marked `@pytest.mark.cart`.
- Test data is driven by `data/test_data.json`; the price cap is not hard-coded in the test.
