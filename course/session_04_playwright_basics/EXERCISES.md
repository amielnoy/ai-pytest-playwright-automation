# Session 4 — Exercises

## Exercise 1: Locator Audit

Open `test_login.py` and inspect every locator used.

1. For each locator, identify which step in the locator strategy hierarchy it falls on (1 = most stable, 7 = most fragile).
2. If any locator is a CSS class or XPath, rewrite it using the highest-ranked stable alternative.
3. Confirm the test still passes after your changes.

---

## Exercise 2: Fix the Assertion

The following test uses a bare `assert` that reads the DOM once. Rewrite it using `expect()`.

```python
def test_cart_badge(page):
    page.goto("https://tutorialsninja.com/demo")
    page.locator(".add-to-cart").first.click()
    badge = page.locator("#cart-total").inner_text()
    assert "1 item" in badge
```

Explain in one sentence why the original is flaky.

---

## Exercise 3: Add a Parametrized Negative Test

In `test_login.py`, add a parametrized test that covers:

- Empty username, valid password → expected error message
- Valid username, empty password → expected error message
- Both empty → expected error message

Use `@pytest.mark.parametrize` with a tuple of `(username, password, expected_msg)`.

---

## Exercise 4: Debug with the Trace Viewer

1. Intentionally break a locator in `test_add_to_cart.py` (rename it to something that does not exist).
2. Run the test with tracing enabled (add the tracing fixture from the lecture).
3. Open `playwright show-trace trace.zip` and identify the exact step where the failure occurred.
4. Fix the locator and confirm the test passes.

---

## Exercise 5: Parallel Execution Timing

1. Run the full session test suite serially: `pytest -n 0` — record the elapsed time.
2. Run it in parallel: `pytest -n auto` — record the elapsed time.
3. Calculate the speedup ratio.
4. Explain one scenario where parallel execution could cause a test to fail even if the test logic is correct.
