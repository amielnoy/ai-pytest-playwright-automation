# Session 11 - Test Data Strategy: Stable, Isolated, and Meaningful Data

## Learning Objectives

- Choose between static data, factories, API-created data, and secrets.
- Keep tests parallel-safe with unique values and cleanup.
- Use boundary and equivalence data without burying intent.
- Store reusable data in `data/test_data.json`.
- Avoid leaking secrets into git or reports.

---

## Data Types

| Type | Use for | Example |
|---|---|---|
| Static JSON | Stable public inputs | Search terms, price limits. |
| Factory | Unique data per run | Email with timestamp. |
| API-created | Preconditions | Cart with item, existing account. |
| Secret | Private credentials | Registration email account. |

Test data should explain behavior. Randomness should create uniqueness, not hide intent.

---

## Parallel-Safe Data

Bad:

```python
email = "student@example.com"
```

Better:

```python
email = f"student_{int(time.time())}@example.com"
```

Best in this project: use the existing `{ts}` placeholder through `utils.data_loader.get_test_data()`.

---

## Before / After

Weak:

```python
def test_register(page):
    page.fill("#email", "test@test.com")
```

Better:

```python
registration_data = get_test_data("registration.valid_user")
register_page.register(registration_data)
```

The test reuses the project data loader and stays isolated.

---

## Session Completion Checklist

- [ ] I identified which tests need unique data.
- [ ] I moved hardcoded reusable data into `data/test_data.json`.
- [ ] I used a factory or timestamp for data that must be unique.
- [ ] I confirmed no secrets are committed.
- [ ] I completed the exercises.
