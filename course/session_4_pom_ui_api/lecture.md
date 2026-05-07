# Session 4 — Advanced Playwright: POM + UI + API

## The Page Object Model

The POM separates *what a test does* from *how the page works*.
Tests read like a business scenario; page objects hide all Playwright details.

**Rule:** No raw selectors, `locator()` calls, or `expect()` in test functions. Every interaction goes through a page class method.

Structure for this session:
- `BasePage` — `navigate()`, `page`, `base_url`
- `LoginPage` — `open()`, `login()`, `expect_error()`
- `InventoryPage` — `add_first_item()`, `add_item_by_name()`, `sort_by()`, `go_to_cart()`
- `CartPage` — `item_count()`, `remove_item_by_name()`, `proceed_to_checkout()`
- `CheckoutPage` — `fill_info()`, `continue_to_overview()`, `finish()`, `expect_order_complete()`

---

## Fluent API

Every page method returns either `self` (same page) or the next page object (after navigation).
This enables readable chained calls:

```python
LoginPage(page, BASE_URL).open().login("standard_user", "secret_sauce")
    .add_first_item()
    .expect_cart_count(1)
    .go_to_cart()
    .proceed_to_checkout()
    .fill_info(info)
    .finish()
    .expect_order_complete()
```

Tests become a linear story with no Playwright internals visible.

---

## Defining Locators

Define locators in `__init__` so they are evaluated lazily at call time, not at import time.
This avoids "element not found" errors when the page is not yet loaded.

```python
def __init__(self, page: Page, base_url: str):
    super().__init__(page, base_url)
    self.username = page.get_by_placeholder("Username")
    self.login_btn = page.get_by_role("button", name="Login")
    self.error = page.locator('[data-test="error"]')
```

---

## UI vs API Setup

Prefer **API setup** for preconditions — it is faster and does not depend on UI stability.
Use **UI setup** only when you are specifically testing the UI flow that creates the state.

Example: to test cart checkout, add items via the cart API endpoint rather than clicking "Add to cart" for each item through the browser.

Playwright's `APIRequestContext` lets you make HTTP calls inside a test:

```python
api = playwright.request.new_context(base_url="https://api.example.com")
resp = api.post("/cart/items", data={"product_id": 1})
assert resp.status == 201
api.dispose()
```

---

## Data Factory

Use `faker` + `dataclasses` for typed, realistic, and unique test data.
A factory function like `make_checkout_info()` returns a `CheckoutInfo` dataclass with random first name, last name, and postal code.
A `make_incomplete_checkout_info(missing="first_name")` variant omits one field to drive validation error tests.
This keeps test data out of test functions and eliminates magic strings.
