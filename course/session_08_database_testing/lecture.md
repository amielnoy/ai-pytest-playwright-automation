# Session 8 - Database Testing

## Learning Objectives

By the end of this session you will be able to:

- Explain what database tests should and should not prove.
- Create isolated database fixtures that are safe for parallel test runs.
- Validate schema constraints, foreign keys, and data integrity rules.
- Compare API/UI behavior against database state without coupling every test to SQL.
- Use transactions, seed data, and cleanup strategies deliberately.
- Recognize when a database assertion belongs in unit, integration, API, or E2E coverage.

---

## Why Database Testing Matters

UI and API tests prove what the application exposes. Database tests prove that the persisted state is correct, constrained, and recoverable.

Good database tests catch failures such as:

- A cart item is shown in the UI but not persisted.
- Duplicate rows are created instead of updating an existing record.
- Negative prices or quantities are accepted.
- Foreign key relationships are broken.
- A migration silently drops a required column.
- Cleanup logic leaves test data that pollutes future runs.

Database testing is not a replacement for API or UI testing. It is a lower-level safety net for persistence rules.

---

## Test Scope

| Layer | What it proves | Example |
|---|---|---|
| Unit | Query builder or repository logic handles inputs correctly | `cart_total()` sums item price and quantity |
| Integration | Real database constraints and joins work | `cart_items.product_id` rejects unknown products |
| API + DB | API changes persistent state correctly | `POST /cart` creates one row with expected quantity |
| UI + DB | A critical user flow persists expected state | Add to cart in browser, then verify database row |
| Migration | Schema evolves safely | New column exists and existing rows remain readable |

Use the lowest layer that proves the risk. Do not add a database assertion to every browser test.

---

## Isolation Patterns

### In-memory database

Use SQLite `:memory:` for fast teaching examples and pure repository logic.

```python
connection = sqlite3.connect(":memory:")
```

### Temporary file database

Use `tmp_path` when the database must behave like a file-backed database.

```python
db_path = tmp_path / "test.db"
connection = sqlite3.connect(db_path)
```

### Transaction rollback

For shared test databases, wrap each test in a transaction and roll it back in teardown.

```python
connection.execute("BEGIN")
yield connection
connection.rollback()
```

This works only when the application under test uses the same transaction boundary or a compatible database strategy.

### Unique test data

When tests hit a shared environment, generate unique values:

```text
email: db_test_{timestamp}@example.com
order_ref: QA-{uuid}
```

Never rely on deleting broad records such as `DELETE FROM users WHERE email LIKE '%test%'` in a shared database.

---

## What To Assert

Strong database assertions are specific and tied to business rules:

- Row exists with the expected primary key or unique identifier.
- Exactly one row was created.
- Quantity increased instead of duplicate rows being inserted.
- Foreign key rejects invalid references.
- `CHECK` constraint rejects invalid numeric values.
- Calculated total matches persisted item rows.
- Required fields are `NOT NULL`.
- Migration leaves existing data readable.

Weak assertions are broad and brittle:

- "There are more rows than before" without filtering by test data.
- "The whole table equals this fixture" in a shared database.
- UI test asserts every column in an internal table.
- Test depends on row order without `ORDER BY`.

---

## Example: Cart Persistence

The runnable example in `lecture.py` creates a small SQLite schema:

- `products`
- `carts`
- `cart_items`

It demonstrates:

- `PRIMARY KEY`
- `NOT NULL`
- `CHECK`
- `FOREIGN KEY`
- join-based total calculation
- upsert behavior for adding the same product twice

Run it:

```bash
python course/session_08_database_testing/lecture.py
```

Example output:

```text
Products: ['Apple Cinema 30', 'MacBook', 'iPhone']
Cart ID: 1
Cart total: 848.4
```

---

## pytest Fixture Pattern

```python
import pytest

from course.session_08_database_testing.lecture import (
    connect_database,
    create_schema,
    seed_products,
)


@pytest.fixture
def db():
    connection = connect_database()
    create_schema(connection)
    seed_products(connection)
    yield connection
    connection.close()
```

This fixture is:

- Isolated per test.
- Fast.
- Deterministic.
- Safe with `pytest-xdist` because no database file is shared.

---

## API + Database Assertion Pattern

When combining API and database checks:

1. Arrange test data through the database or a test fixture.
2. Act through the public API.
3. Assert the API response.
4. Assert one focused database state change.

Example:

```python
def test_add_cart_item_persists_quantity(api_client, db):
    response = api_client.post("/cart/items", json={"product_id": 43, "quantity": 2})

    assert response.status_code == 200

    row = db.execute(
        "SELECT quantity FROM cart_items WHERE product_id = ?",
        (43,),
    ).fetchone()
    assert row["quantity"] == 2
```

Avoid asserting internal database state in every API test. Use it for high-risk persistence behavior.

---

## Migration Test Checklist

For every migration, ask:

- Does the new table or column exist?
- Are required indexes present?
- Are old rows still readable?
- Are default values correct?
- Are constraints enforced?
- Can the rollback path run in lower environments?

Migration tests are especially valuable when production data already exists.

---

## Common Mistakes

- Sharing one mutable database across parallel tests.
- Cleaning data by broad patterns instead of unique test identifiers.
- Asserting internal implementation details in E2E tests.
- Forgetting to enable SQLite foreign keys with `PRAGMA foreign_keys = ON`.
- Using SQL string interpolation instead of parameters.
- Forgeting that database row order is undefined without `ORDER BY`.
- Testing mocks instead of real constraints for integration coverage.

---

## Session Completion Checklist

- [ ] I can explain which database risks belong below UI/API tests.
- [ ] I created an isolated database fixture.
- [ ] I tested at least one constraint failure.
- [ ] I tested one calculated query or join.
- [ ] I wrote one API + DB assertion with a focused persistence check.
- [ ] I avoided broad cleanup that could delete another test's data.
