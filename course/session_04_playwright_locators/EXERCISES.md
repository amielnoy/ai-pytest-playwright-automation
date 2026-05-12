# Session 4 - Exercises

## Exercise 1: Locator Audit

Pick one file from `pages/` or `tests/web-ui/`.

Find at least five locators or direct UI interactions and classify each as:

- Strong user-facing locator.
- Acceptable test id locator.
- Fragile CSS/XPath/positional locator.
- Locator placed in the wrong layer.

Write the replacement you would use for each weak locator.

---

## Exercise 2: Refactor a Raw Selector

Find or create one raw selector in a test file.

Refactor it so:

- The test calls a page object or component method.
- The page object uses `get_by_role()`, `get_by_label()`, `get_by_text()`, or `get_by_test_id()`.
- The assertion remains concrete.

Run the narrowest relevant test.

---

## Exercise 3: Replace Positional Selection

Find a place where a test or page object uses `first`, `last`, `nth()`, or an index-based product selection.

Replace it with a locator that identifies the intended item by:

- Product name.
- Row text.
- Accessible name.
- Test id.

Explain why the new locator is less fragile.

---

## Exercise 4: Test ID Decision

Choose one element that is hard to locate by role, label, or text.

Write a short proposal for adding a test id:

- Element.
- Current locator problem.
- Proposed test id name.
- Why user-facing locators are not enough.
- Where the test id would be used.

---

## Exercise 5: Codegen Locator Review

Use Playwright codegen from Session 14 to generate a short flow.

For each generated locator:

- Keep as-is.
- Improve to a role or label locator.
- Replace with a test id.
- Reject as too brittle.

Then convert one improved locator into a page object method.
