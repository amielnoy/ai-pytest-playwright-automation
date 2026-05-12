# Session 4 - Playwright Locators: Best Practices for Stable Tests

## Learning Objectives

By the end of this session you will be able to:

- Choose locators according to Playwright's recommended priority.
- Use role, label, text, placeholder, alt text, title, and test id locators correctly.
- Explain why locators are preferred over raw CSS and XPath selectors.
- Use filtering and chaining to target one element without relying on brittle order.
- Avoid common locator anti-patterns that create flaky tests.
- Refactor generated or legacy selectors into production-quality page object methods.

---

## Why Locators Matter

Locators are Playwright's main way to find elements. They include auto-waiting and retry behavior, so Playwright can wait for an element to become actionable before clicking, filling, or asserting against it.

Good locators describe what a user or assistive technology can perceive. Bad locators describe fragile DOM implementation details.

---

## Locator Priority

Use this priority order:

| Priority | Locator | Use when |
|---|---|---|
| 1 | `get_by_role()` | The element has a clear semantic role and accessible name. |
| 2 | `get_by_label()` | Locating a form control by its visible label. |
| 3 | `get_by_text()` | Verifying or selecting visible text. |
| 4 | `get_by_placeholder()` | The input is best identified by placeholder text. |
| 5 | `get_by_alt_text()` | Locating images or media by alternative text. |
| 6 | `get_by_title()` | The element has a meaningful `title` attribute. |
| 7 | `get_by_test_id()` | The UI needs an explicit stable testing contract. |
| 8 | `locator("css")` / XPath | Last resort for legacy or non-semantic markup. |

Prefer user-facing locators first. Use test ids when user-facing attributes are unstable, translated, duplicated, or not specific enough.

---

## Role Locators

Role locators are usually the best first choice because they match how users and assistive technologies understand the page.

```python
page.get_by_role("button", name="Search").click()
page.get_by_role("link", name="Shopping Cart").click()
expect(page.get_by_role("heading", name="Shopping Cart")).to_be_visible()
```

Always provide the accessible name when possible. This avoids strictness errors and documents intent.

Weak:

```python
page.get_by_role("button").click()
```

Better:

```python
page.get_by_role("button", name="Add to Cart").click()
```

---

## Form Locators

Use labels for form controls:

```python
page.get_by_label("E-Mail Address").fill("student@example.com")
page.get_by_label("Password").fill("secret")
```

Use placeholders only when the placeholder is the clearest stable text:

```python
page.get_by_placeholder("Search").fill("iPod")
```

If a field has no label and only a placeholder, consider raising that as both a testability and accessibility improvement.

---

## Text Locators

Use text locators for visible copy that is part of the expected behavior:

```python
expect(page.get_by_text("Your shopping cart is empty!")).to_be_visible()
```

Avoid broad text locators for actions when a role locator would be clearer.

Weak:

```python
page.get_by_text("Continue").click()
```

Better:

```python
page.get_by_role("button", name="Continue").click()
```

---

## Test IDs

Test ids are stable explicit contracts between developers and automation.

```python
page.get_by_test_id("cart-total").click()
```

Use them when:

- The element has no reliable role or accessible name.
- Text changes because of localization or content experiments.
- Several identical controls appear in a complex component.
- You need a stable hook for a dynamic UI.

Do not use test ids to hide poor accessibility. If a user-facing locator should exist, fix the markup where possible.

---

## Chaining and Filtering

Use chaining to scope actions to a specific part of the page:

```python
product = page.get_by_role("listitem").filter(has_text="iPod Classic")
product.get_by_role("button", name="Add to Cart").click()
```

Use filtering instead of brittle positional selectors:

```python
page.get_by_role("row").filter(has_text="MacBook").get_by_role("button", name="Add").click()
```

Avoid:

```python
page.get_by_role("button", name="Add").nth(2).click()
```

`nth()`, `first`, and `last` can be useful, but they are fragile when order changes. Prefer a locator that uniquely identifies the intended element.

---

## Strictness

Playwright locators are strict for single-element actions. If a click matches multiple elements, Playwright throws instead of guessing.

This is good. It catches ambiguous tests early.

Ambiguous:

```python
page.get_by_role("button", name="Add").click()
```

Specific:

```python
product = page.get_by_role("listitem").filter(has_text="MacBook")
product.get_by_role("button", name="Add to Cart").click()
```

---

## CSS and XPath Last

Avoid selectors that depend on DOM shape, generated classes, or layout:

```python
page.locator("#content > div:nth-child(3) .btn-primary").click()
page.locator("//div[@class='product-thumb'][2]//button").click()
```

Use CSS or XPath only when:

- You are working with legacy markup that has no useful role, text, or test id.
- You are inside a page object, not directly in a test.
- You have a clear reason and a comment would help future maintainers.

---

## Refactoring Rules

When reviewing locators, apply these rules:

| If you see | Replace with |
|---|---|
| Raw selector in a test | Page object method. |
| CSS class selector | Role, label, text, or test id. |
| XPath based on DOM position | Chained locator with `filter()`. |
| `nth()` on a dynamic list | Filter by product name, row text, or test id. |
| `page.get_by_text(...).click()` | `get_by_role()` if the target is a button or link. |
| Sleep before click | Locator action or assertion with auto-waiting. |

---

## Page Object Example

```python
class SearchResultsPage(BasePage):
    def product_card(self, product_name: str):
        return self.page.get_by_role("listitem").filter(has_text=product_name)

    def add_product_to_cart(self, product_name: str) -> None:
        self.product_card(product_name).get_by_role("button", name="Add to Cart").click()
```

Test:

```python
def test_add_ipod_to_cart(home_page, search_results_page):
    home_page.search("iPod")
    search_results_page.add_product_to_cart("iPod Classic")
```

The test describes the behavior. The page object owns the locator strategy.

---

## Session Completion Checklist

- [ ] I can list the recommended locator priority order.
- [ ] I replaced at least one CSS or XPath selector with a user-facing locator.
- [ ] I used chaining or filtering to avoid a positional selector.
- [ ] I can explain when `get_by_test_id()` is appropriate.
- [ ] I can explain why `nth()` should be rare.
- [ ] I moved locator details into a page object instead of a test file.
