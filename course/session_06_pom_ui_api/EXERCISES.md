# Session 6 — Exercises

## Exercise 1: Add a Page Method

The `InventoryPage` currently has `add_first_item()`. Add a method `get_item_names() -> list[str]` that returns the names of all visible products on the inventory page.

Rules:
- No raw Playwright calls in the test that uses this method.
- The method must use `expect()` before reading values to ensure elements are present.
- Write one test that uses `get_item_names()` to assert that the first item in the default sort order is "Sauce Labs Backpack".

---

## Exercise 2: Fluent API Chain

Write a test that performs the full happy-path checkout using only fluent method chaining — no intermediate variable assignments after the initial `LoginPage` construction.

The chain must cover: open → login → add item → go to cart → checkout → fill info → finish → assert order complete.

---

## Exercise 3: API Setup Fixture

The `test_e2e_pom.py` adds an item to the cart through the UI. Rewrite the fixture so the cart is populated via `APIRequestContext` instead.

1. Identify the API endpoint that adds an item to the cart.
2. Create a `cart_with_item` pytest fixture that calls the endpoint and yields the page already at the cart URL.
3. Update the test to use the new fixture.
4. Measure and record how much faster the test runs with API setup vs UI setup.

---

## Exercise 4: Data Factory

`make_incomplete_checkout_info` currently only supports `missing="first_name"`. Extend it to support `missing="last_name"` and `missing="postal_code"` as well.

Write three parametrized tests — one per missing field — that each assert the correct validation error message.

---

## Exercise 5: POM Extension

The demo site has a product detail page (click any product from the inventory). Create a `ProductDetailPage` class that:

- Has a method `get_price() -> float` returning the numeric price.
- Has a method `add_to_cart()` returning `self`.
- Extends `BasePage` and follows the lazy-locator pattern from the lecture.

Write a test that navigates to a product detail page and asserts the price is greater than zero.
