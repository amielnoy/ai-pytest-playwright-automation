# Session 3 — Playwright Basics & Your First Python Framework

## How Playwright Works

Playwright controls a real browser (Chromium, Firefox, WebKit) over the DevTools Protocol.
Every action — `click`, `fill`, `goto` — automatically waits for the element to be ready.
This built-in **auto-wait** eliminates the need for `time.sleep()` calls.

The Python sync API (`from playwright.sync_api import sync_playwright`) runs sequentially and is easier to read and debug than the async variant. Use the sync API for UI automation unless you have a specific async requirement.

---

## Locator Strategy

Choose locators in this order (most stable → most fragile):

1. `get_by_role('button', name='Login')` — semantic, matches what screen readers see.
2. `get_by_label('Email address')` — best for form inputs.
3. `get_by_placeholder('Search…')` — inputs with placeholder text.
4. `get_by_text('Submit')` — static visible text.
5. `get_by_test_id('submit-btn')` — `data-testid` attribute added by developers.
6. `locator('[data-test="error"]')` — attribute fallback.
7. `locator('.css-class')` — last resort; breaks on style refactors.

Never use XPath in new code. Avoid nth-child selectors.

---

## Assertions with `expect()`

Always use `expect()` — it retries until the condition is true or the timeout expires:

- `expect(locator).to_be_visible()` — element present and visible.
- `expect(locator).to_have_text('…')` — exact or regex text.
- `expect(locator).to_contain_text('…')` — partial match.
- `expect(locator).to_have_value('…')` — input field value.
- `expect(locator).to_have_count(n)` — exactly n matching elements.
- `expect(page).to_have_url('…')` — navigation completed.

Never use bare `assert locator.inner_text() == '…'` — it reads the DOM once with no retry.

---

## pytest Fixtures

Fixtures provide setup and teardown for tests. Scope controls sharing:

- `session` — one browser instance for the whole run (fastest, no isolation).
- `module` — new context per file.
- `function` — new page per test (default; full isolation).

A `logged_in_page` fixture logs in once and yields the page, so login steps are not repeated in every test that needs an authenticated state.

---

## Parametrize for Negative Tests

`@pytest.mark.parametrize` turns one test function into N test cases — ideal for covering multiple invalid inputs with a single block of assertion logic.

```python
@pytest.mark.parametrize("user,pwd,msg", [
    ("locked_out_user", "secret_sauce", "locked out"),
    ("",                "secret_sauce", "Username is required"),
    ("standard_user",   "",             "Password is required"),
])
def test_login_negative(page, user, pwd, msg):
    …
```
