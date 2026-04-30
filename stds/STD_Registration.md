# STD-REGISTRATION: User Registration Tests

## Overview
| Field | Value |
|---|---|
| Test Suite | TutorialsNinja Web UI Registration |
| Feature | Registration |
| Story | User Account Creation |
| Marker | `registration` |
| Priority | High |
| Author | QA Agent |
| Date | 2026-04-30 |

## Objective
Validate that a new user can successfully complete the registration form and that submitting an empty form surfaces the appropriate validation errors.

## Preconditions
- Browser can open `https://tutorialsninja.com/demo/`.
- Registration secrets are configured (email, password, confirm_password fields populated in `data/secrets.json`).
- A unique email address is generated per run via the `{ts}` placeholder.

## Test Cases

### TC-REG-01: Successful New-User Registration
**Objective:** Confirm a fully filled registration form creates an account.  
**Severity:** Critical

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Home page loads. |
| 2 | Click the account menu and select "Register". | N/A | Register Account page loads. |
| 3 | Fill all required fields (First Name, Last Name, Email, Telephone, Password, Confirm Password). | From `data/secrets.json` registration block; unique email via `{ts}`. | All fields are populated. |
| 4 | Select Newsletter preference. | `newsletter` value from test data. | Radio is selected. |
| 5 | Check the Privacy Policy checkbox. | N/A | Checkbox is checked. |
| 6 | Click **Continue**. | N/A | Form submits. |
| 7 | Verify success heading is visible. | Heading: `Your Account Has Been Created!` | Success heading is visible. |

**Post-conditions:** A new user account exists with the generated email address.

---

### TC-REG-02: Registration Fails with Missing Required Fields
**Objective:** Confirm submitting an empty form surfaces at least one validation error.  
**Severity:** Normal

| Step | Action | Test Data | Expected Result |
|------|--------|-----------|-----------------|
| 1 | Navigate to the store home page. | `https://tutorialsninja.com/demo/` | Home page loads. |
| 2 | Click the account menu and select "Register". | N/A | Register Account page loads. |
| 3 | Leave all fields empty and click **Continue**. | All fields: `""`. | Form submits with blank values. |
| 4 | Read the error alert text. | N/A | Error message is non-empty. |

**Post-conditions:** No account is created; user remains on the registration page.

## Notes
- Skips automatically when `data/secrets.json` is absent or missing required fields.
- Tests are marked `@pytest.mark.registration`.
