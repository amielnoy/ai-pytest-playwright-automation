# Session 18 - Automation Code Review: Raising the Quality Bar

## Learning Objectives

- Review automation changes for behavior, isolation, maintainability, and report quality.
- Identify flaky locators, weak assertions, hidden setup, and unsafe data.
- Give actionable review comments with file, risk, and fix.
- Review AI-generated tests before accepting them.

---

## Review Checklist

| Area | Questions |
|---|---|
| Behavior | Does the test verify one clear user or API behavior? |
| Layering | Are selectors in page objects, not tests? |
| Locators | Are role/label/text/test-id locators used appropriately? |
| Data | Is data isolated, unique, and secret-safe? |
| Fixtures | Is setup explicit and scoped correctly? |
| Assertions | Would the test fail for a meaningful regression? |
| Reports | Would CI artifacts explain the failure? |

---

## Before / After Review Comment

Weak:

```text
This test is bad.
```

Better:

```text
tests/web-ui/test_cart.py:42 uses `.nth(1)` to choose a product. This can add the wrong item when sort order changes. Filter the product card by product name in the page object, then click its Add to Cart button.
```

---

## Session Completion Checklist

- [ ] I reviewed one test for locator quality.
- [ ] I reviewed one fixture for scope and cleanup.
- [ ] I reviewed one assertion for concrete behavior.
- [ ] I wrote at least three actionable review comments.
