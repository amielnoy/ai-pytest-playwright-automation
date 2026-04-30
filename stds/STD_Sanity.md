# STD-SANITY: Critical UI Sanity Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Sanity |
| Feature | Critical UI availability |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that the demo store's most critical user-facing surfaces are reachable and functional before running deeper regression suites. These cases intentionally cover only high-value sanity checks not already covered by the existing registration, search filtering, sorting, iPod storage, add-to-cart, and cart-total tests.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- The demo store is reachable and returns the standard TutorialsNinja UI.
- No authenticated session is required.
- Cart starts in the default empty state for a new browser context.

## Existing Coverage Considered
- Registration success and required-field validation are already covered.
- Search price filtering, no-results handling, sorting, iPod product extraction, add-to-cart, and cart total checks are already covered.
- These sanity tests add coverage only for home/header availability, login failure feedback, and product detail navigation.

## Test Cases

### TC-SANITY-01: Home Page Header Controls Are Available
**Objective:** Confirm the home page loads and exposes the critical header controls needed by most UI flows.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Page loads successfully. |
| 2 | Read the browser page title. | N/A | Title is `Your Store`. |
| 3 | Locate the currency control in the header. | N/A | `Currency` button is visible. |
| 4 | Locate the search field in the header. | Placeholder: `Search` | Search input is visible. |
| 5 | Locate the cart summary button in the header. | Button name: `0 item(s) - $0.00` | Empty cart summary is visible. |

**Post-conditions:** Browser remains on the home page with no cart or account changes.

### TC-SANITY-02: Invalid Login Shows Warning
**Objective:** Confirm the login page accepts input and returns a clear validation warning for invalid credentials.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the account login page. | `/index.php?route=account/login` | Login page loads with Returning Customer form. |
| 2 | Fill `E-Mail Address`. | `sanity_invalid@example.com` | Email field contains the provided value. |
| 3 | Fill `Password`. | `bad-password` | Password field contains the provided value. |
| 4 | Click `Login`. | N/A | Form submits and remains on login flow. |
| 5 | Verify login state. | N/A | `My Account` heading is not visible. |
| 6 | Verify warning message. | Expected text: `Warning: No match for E-Mail Address and/or Password.` | Warning is visible. |

**Post-conditions:** User remains unauthenticated.

### TC-SANITY-03: Product Detail Opens From Search
**Objective:** Confirm a shopper can search for a known product and open its product detail page.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Page loads successfully. |
| 2 | Fill the header search input. | `MacBook` | Search input contains `MacBook`. |
| 3 | Click the header search button. | N/A | Search results page loads. |
| 4 | Click the `MacBook` product link in the first matching product card. | Product name: `MacBook` | Product detail page opens. |
| 5 | Read the browser page title. | N/A | Title is `MacBook`. |
| 6 | Verify product heading. | Heading: `MacBook` | Product heading is visible. |
| 7 | Verify quantity input. | Label: `Qty`, value: `1` | Quantity field is visible with value `1`. |
| 8 | Verify purchase control. | Button: `Add to Cart` | Add to Cart button is visible. |

**Post-conditions:** Browser remains on the MacBook product detail page; no item is added to cart.

## Notes
- These tests are marked `@pytest.mark.sanity`.
- The plan was informed by live Playwright MCP inspection of the home, login, search results, and product detail pages.
- The cases are intentionally small and should be run before broader regression suites.
