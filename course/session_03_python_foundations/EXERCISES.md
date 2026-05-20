# Session 3 — Exercises

## How to Submit

Create or update a Python file named `session_03_answers.py`.
For each exercise, include at least one small example call or pytest test.

## Review Criteria

Your work is complete when:

- Functions have clear names, inputs, return values, and type hints.
- Helpers do one job.
- Tests cover normal input and at least one edge or invalid input where relevant.
- Assertion failures explain what is wrong.
- `pytest course/session_03_python_foundations -q` still passes.

---

## Exercise 1: Normalize UI Text

Write a function that receives text copied from a web page and returns it trimmed with repeated spaces removed.

Example:

```python
normalize_text("  Add   to   Cart  ") == "Add to Cart"
```

Add one more example with a newline or tab character.

---

## Exercise 2: Parse Prices

Write tests for `parse_price()` with these inputs:

- `$602.00`
- `$1,202.00`
- `  $123.20  `

Then add one invalid input test, such as `"free"` or `""`, and assert that Python raises `ValueError`.

---

## Exercise 3: Product Data

Create three `Product` objects and return only the products that are in stock and under a chosen max price.

Required cases:

- One product under the max price and in stock.
- One product over the max price.
- One product under the max price but out of stock.

Write an assertion for the returned product names, not just the object count.

---

## Exercise 4: Required API Fields

Create a dictionary that represents a user payload. Validate that `email`, `password`, and `first_name` exist.

Then remove one field and verify the assertion message names the missing field.

---

## Exercise 5: Test IDs

Write a helper that turns a feature and behavior into a readable test ID, then test it with at least two examples.

Expected style:

```python
format_test_id("Search Results", "Sort A to Z") == "search_results__sort_a_to_z"
```

Add a case with extra spaces.

---

## Exercise 6: Build a Mini Test Data Helper

Create a function named `build_user_payload()` that accepts `email`, `password`, and `first_name`, then returns a dictionary:

```python
{
    "email": "student@example.com",
    "password": "secret",
    "first_name": "Student",
}
```

Write two tests:

- It returns all expected keys.
- It works with a different user's values.
