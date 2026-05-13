# STD-LOGIN: Login

## Overview
| Field | Value |
|---|---|
| Test Suite | Web UI |
| Feature | Login |
| Priority | High |
| Author | Playwright CLI STD Agent |
| Date | 2026-05-13 |
| Source URL | https://tutorialsninja.com/demo/index.php?route=account/login |

## Objective
Validate the visible behavior, navigation anchors, forms, and command controls discovered on the target page.

## Playwright CLI Evidence
The agent captured the page with:

```bash
python -m playwright screenshot --wait-for-timeout 1000 "https://tutorialsninja.com/demo/index.php?route=account/login" "artifacts/std_page_snapshots/login.png"
```

## Page Inventory
- Title: `Account Login`
- URL after load: `https://tutorialsninja.com/demo/index.php?route=account/login`
- Screenshot: `artifacts/std_page_snapshots/login.png`
- Headings: Qafox.com, New Customer, Returning Customer
- Forms found: 2
- Buttons/commands found: 7
- Navigation links found: 20
- Alerts visible on load: None

## Preconditions
- Chromium browser binaries are installed for Playwright.
- The target URL is reachable from the test environment.
- Test data that mutates server state must use unique values or disposable accounts.
- Tests should start from a clean browser context.

## Test Cases

### TC-LOGIN-01: Page loads with expected title and primary content
**Objective:** Validate that the target URL is reachable and renders the expected page shell.
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL in Chromium | https://tutorialsninja.com/demo/index.php?route=account/login | Page loads without browser or HTTP error. |
| 2 | Read the browser page title | N/A | Title is `Account Login`. |
| 3 | Verify the primary page content is visible | N/A | `Qafox.com` is visible. |
| 4 | Check that the page remains on the expected URL | N/A | Current URL matches the loaded route or expected redirect. |

**Post-conditions:** Browser remains on the loaded page.

### TC-LOGIN-02: Primary navigation links are visible and usable
**Objective:** Validate that the page exposes stable navigation anchors for users and tests.
**Severity:** High

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL | N/A | Page loads successfully. |
| 2 | Inspect the header or navigation area | N/A | Navigation links are visible and have readable names. |
| 3 | Verify navigation link `My Account` | https://tutorialsninja.com/demo/index.php?route=account/account | Link has a non-empty href and can be used as a navigation target. |
| 4 | Verify navigation link `Register` | https://tutorialsninja.com/demo/index.php?route=account/register | Link has a non-empty href and can be used as a navigation target. |
| 5 | Verify navigation link `Login` | https://tutorialsninja.com/demo/index.php?route=account/login | Link has a non-empty href and can be used as a navigation target. |
| 6 | Verify navigation link `Wish List (0)` | https://tutorialsninja.com/demo/index.php?route=account/wishlist | Link has a non-empty href and can be used as a navigation target. |
| 7 | Verify navigation link `Shopping Cart` | https://tutorialsninja.com/demo/index.php?route=checkout/cart | Link has a non-empty href and can be used as a navigation target. |
| 8 | Verify navigation link `Checkout` | https://tutorialsninja.com/demo/index.php?route=checkout/checkout | Link has a non-empty href and can be used as a navigation target. |
| 9 | Verify navigation link `Qafox.com` | https://tutorialsninja.com/demo/index.php?route=common/home | Link has a non-empty href and can be used as a navigation target. |
| 10 | Verify navigation link `Desktops` | https://tutorialsninja.com/demo/index.php?route=product/category&path=20 | Link has a non-empty href and can be used as a navigation target. |

**Post-conditions:** No navigation click is required; page state is unchanged.

### TC-LOGIN-03: Form #1 validates missing required input
**Objective:** Confirm that incomplete form submission is blocked and visible feedback is provided.
**Severity:** High

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL | N/A | Page loads successfully. |
| 2 | Locate form #1 | https://tutorialsninja.com/demo/index.php?route=common/currency/currency | Form is visible and ready for input. |
| 3 | Click `$ Currency` without filling required fields | Empty form | Validation prevents incomplete submission. |

**Post-conditions:** No valid data is submitted.

### TC-LOGIN-04: Form #1 accepts valid user input
**Objective:** Validate the expected happy-path behavior for the form.
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL | N/A | Page loads successfully. |
| 2 | Locate form #1 | https://tutorialsninja.com/demo/index.php?route=common/currency/currency | Form fields are visible. |
| 3 | Click `$ Currency` | N/A | Submission completes or shows expected server-side feedback. |

**Post-conditions:** Application reaches the expected post-submit state or displays server feedback.

### TC-LOGIN-05: Form #2 validates missing required input
**Objective:** Confirm that incomplete form submission is blocked and visible feedback is provided.
**Severity:** High

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL | N/A | Page loads successfully. |
| 2 | Locate form #2 | https://tutorialsninja.com/demo/index.php?route=account/login | Form is visible and ready for input. |
| 3 | Click `submit` without filling required fields | Empty form | Validation prevents incomplete submission. |
| 4 | Verify validation feedback for `E-Mail Address` | Empty value | A visible validation message or browser required-field state is shown. |
| 5 | Verify validation feedback for `Password` | Empty value | A visible validation message or browser required-field state is shown. |

**Post-conditions:** No valid data is submitted.

### TC-LOGIN-06: Form #2 accepts valid user input
**Objective:** Validate the expected happy-path behavior for the form.
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL | N/A | Page loads successfully. |
| 2 | Locate form #2 | https://tutorialsninja.com/demo/index.php?route=account/login | Form fields are visible. |
| 3 | Fill `E-Mail Address` | test_{timestamp}@example.com | Field accepts the value and keeps it visible. |
| 4 | Fill `Password` | Password123! | Field accepts the value and keeps it visible. |
| 5 | Fill `input` | sample value | Field accepts the value and keeps it visible. |
| 6 | Click `submit` | N/A | Submission completes or shows expected server-side feedback. |

**Post-conditions:** Application reaches the expected post-submit state or displays server feedback.

### TC-LOGIN-07: Visible page commands are available
**Objective:** Validate that important command controls can be discovered before deeper flow testing.
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Open the target URL | N/A | Page loads successfully. |
| 2 | Inspect visible command controls | N/A | Buttons and command links are visible with readable labels. |
| 3 | Verify command `$ Currency` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |
| 4 | Verify command `€Euro` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |
| 5 | Verify command `£Pound Sterling` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |
| 6 | Verify command `$US Dollar` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |
| 7 | Verify command `0 item(s) - $0.00` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |
| 8 | Verify command `Continue` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |
| 9 | Verify command `Login` is discoverable | N/A | Control is visible, enabled, and has a clear accessible name. |

**Post-conditions:** Page state is unchanged.

## Notes
- Generated from live page structure; review expected results against product requirements before implementation.
- Refactor generated actions into page objects and flows before adding automation tests.
- Prefer accessible locators and user-visible labels when implementing these cases in Playwright.
