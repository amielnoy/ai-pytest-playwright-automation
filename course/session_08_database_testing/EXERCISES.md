# Session 8 - Exercises

## Exercise 1: Run the Database Demo

Run:

```bash
python course/session_08_database_testing/lecture.py
```

Record:

- The product names printed.
- The cart total.
- Which SQL query calculates the total.

---

## Exercise 2: Write a Schema Constraint Test

Create a test that proves invalid product data is rejected.

Requirements:

- Use an isolated SQLite connection.
- Create the schema from `lecture.py`.
- Try inserting a product with a negative price.
- Assert that `sqlite3.IntegrityError` is raised.

Suggested command:

```bash
pytest course/session_08_database_testing -q
```

---

## Exercise 3: Test Foreign Key Behavior

Create a test for `cart_items.product_id`.

Steps:

1. Create schema and seed products.
2. Create a cart.
3. Try to add product ID `999999`.
4. Assert that the database rejects the row.

Explain why `PRAGMA foreign_keys = ON` matters in SQLite.

---

## Exercise 4: Test Cart Upsert Behavior

Write a test that:

1. Creates a cart.
2. Adds product `43` with quantity `1`.
3. Adds product `43` again with quantity `2`.
4. Queries `cart_items`.
5. Asserts there is one row with quantity `3`.

This proves that duplicate cart lines are merged instead of inserted twice.

---

## Exercise 5: API + Database Test Design

Write a short test design, not code, for this scenario:

> A user adds a product to cart through the API. The response says success, but the row is not persisted.

Include:

- Preconditions.
- API action.
- Response assertions.
- Database assertion.
- Cleanup strategy.
- Why this should not be a full browser test.

---

## Exercise 6: Migration Review

Imagine a migration adds:

```sql
ALTER TABLE products ADD COLUMN sku TEXT;
```

Write five checks you would run before approving the migration.

At least two checks must protect existing production data.
