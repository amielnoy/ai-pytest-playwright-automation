# STD-ACCESSIBILITY: Accessibility Sanity Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Accessibility |
| Feature | Accessibility |
| Story | Sanity accessibility checks |
| Markers | `sanity`, `accessibility` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Confirm that critical pages and controls meet basic programmatic accessibility requirements: language declaration, labelled controls, alt text on images, and visible warning text.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- No authenticated session required.

## Test Cases

### TC-A11Y-01: Home Page Declares English Document Language
**Objective:** The `<html>` element carries `lang="en"`.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Page loads. |
| 2 | Read `lang` attribute from `<html>`. | N/A | Value is `"en"`. |

---

### TC-A11Y-02: Home Page Critical Header Controls Have Accessible Names
**Objective:** The currency dropdown, search input, cart summary, and account menu all have programmatic names resolvable by assistive technology.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Page loads. |
| 2 | Assert account menu, currency dropdown, search input, and cart summary are visible and named. | N/A | All four controls are accessible. |

---

### TC-A11Y-03: Home Featured Product Images Expose Alt Text
**Objective:** Every visible featured product image has a non-empty `alt` attribute.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Page loads. |
| 2 | Collect all visible `.product-thumb img` elements missing an `alt` attribute or with an empty `alt`. | N/A | List is empty. |

---

### TC-A11Y-04: Login Form Fields Have Programmatic Labels
**Objective:** The E-Mail Address and Password inputs and the Login button are all reachable by accessible role/name queries.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the login page. | `/index.php?route=account/login` | Login page loads. |
| 2 | Assert email textbox, password label, and Login button are visible. | N/A | All three controls are visible. |

---

### TC-A11Y-05: Invalid Login Warning Is Exposed as Visible Text
**Objective:** After a failed login the warning is presented as readable text (not only an ARIA live region hidden from sighted users).  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the login page. | `/index.php?route=account/login` | Login page loads. |
| 2 | Submit invalid credentials. | `accessibility_invalid@example.com` / `bad-password` | Form submits. |
| 3 | Assert the `.alert-danger` element is visible and contains the expected warning text. | `Warning: No match for E-Mail Address and/or Password.` | Warning text is visible. |

---

### TC-A11Y-06: Registration Required Fields Have Programmatic Labels
**Objective:** All six required form inputs are reachable by their label text.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to home; click Register. | N/A | Register page loads. |
| 2 | Assert each required field label is visible: First Name, Last Name, E-Mail, Telephone, Password, Password Confirm. | N/A | All six labels are visible. |

---

### TC-A11Y-07: Registration Newsletter Radios Have Accessible Names
**Objective:** The Yes and No newsletter radio buttons both have programmatic names.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to home; click Register. | N/A | Register page loads. |
| 2 | Assert the `Yes` and `No` radio buttons are visible. | N/A | Both radios are visible. |

---

### TC-A11Y-08: Search Page Filter Controls Have Labels
**Objective:** The Search Criteria, Sort By, and Show controls on the search results page have programmatic labels.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to home and search. | Query: `MacBook` | Search results page loads. |
| 2 | Assert `Search Criteria`, `Sort By:`, and `Show:` label elements are visible. | N/A | All three labels are visible. |

---

### TC-A11Y-09: Search Results Product Title Links Have Accessible Names
**Objective:** Every product title link on the search results page has non-empty inner text.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to home and search. | Query: `MacBook` | Search results page loads. |
| 2 | Collect all `.product-thumb h4 a` inner texts. | N/A | List is non-empty and every name has content. |

---

### TC-A11Y-10: Product Detail Form Fields Have Labels and No Duplicate IDs
**Objective:** The Review tab form fields have labels and the page has no duplicate HTML `id` attributes.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to home, search, and open the MacBook product detail page. | Query: `MacBook` | Product detail page loads. |
| 2 | Click the **Reviews** tab. | N/A | Review form is visible. |
| 3 | Assert all review form fields have labels. | N/A | All labels are visible. |
| 4 | Assert no duplicate `id` attributes exist on the page. | N/A | Duplicate ID list is empty. |

## Notes
- Tests are marked `@pytest.mark.sanity` and `@pytest.mark.accessibility`.
