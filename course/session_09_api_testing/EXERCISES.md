# Session 9 - Exercises

## Exercise 1: Run the API Lecture Demo

Run:

```bash
python course/session_09_api_testing/lecture.py
```

Record:

- The five API test types.
- The generated search path for `Apple Cinema`.
- One production test file where each API test type appears.

---

## Exercise 2: Add a Contract Assertion

Use `assert_product_contract()` from `lecture.py`.

Create a product dictionary with:

- `product_id`
- `name`
- `price`

Assert that the helper accepts it.

Then remove one field and assert the helper fails.

---

## Exercise 3: Design a Negative API Test

Write a test design for:

> Adding product ID `999999` to the cart should not create a valid cart item.

Include:

- Request method.
- Endpoint or service method.
- Test data.
- Expected response behavior.
- Expected state behavior.
- Cleanup needs.

---

## Exercise 4: Refactor Raw Request Logic

Find one production API test that performs repeated setup or repeated parsing.

Propose a refactor into:

- `services/api/`
- `flows/`
- or a pytest fixture

Explain why that layer is the right place.

---

## Exercise 5: API Setup For UI

Explain how `api_cart` supports a UI cart-total test.

Answer:

- What state is created through the API?
- Which cookie must be injected into Playwright?
- What behavior is still verified through the browser?
- Why is this less flaky than adding products through the UI every time?

---

## Exercise 6: Run Production API Coverage

Run:

```bash
pytest tests/api tests/contract -q
```

Record:

- Number of tests collected.
- Any failures.
- One assertion that checks HTTP status.
- One assertion that checks business meaning.
