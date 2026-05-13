# Session 3 - Python Foundations For Automation Testing

## Learning Objectives

By the end of this session you will be able to:

- Use variables, strings, numbers, booleans, lists, and dictionaries in test code.
- Write small functions with clear inputs and outputs.
- Use list comprehensions for readable test-data transformations.
- Create simple `dataclass` models for structured test data.
- Raise useful assertion failures from helper functions.
- Read Python code in the rest of the automation framework with confidence.

---

## Why Python Comes Before Playwright

Playwright and pytest are Python libraries in this course. Before writing browser tests, students need the language basics that make automation code readable:

- strings for selectors, URLs, and messages
- lists for product rows and result sets
- dictionaries for API payloads and JSON responses
- functions for reusable validation
- classes and dataclasses for structured page or data objects
- exceptions and assertions for clear failures

This session keeps Python focused on automation instead of abstract exercises.

---

## Core Data Types

```python
product_name = "MacBook"
price = 602.00
in_stock = True
tags = ["laptop", "featured"]
payload = {"email": "student@example.com", "password": "secret"}
```

Good automation code uses simple types until structure is needed.

---

## Functions

Functions should do one clear job:

```python
def parse_price(raw_price: str) -> float:
    cleaned = raw_price.replace("$", "").replace(",", "").strip()
    return float(cleaned)
```

This is easier to test than repeating parsing logic inside UI tests.

---

## Lists And Filtering

```python
cheap_products = [
    product
    for product in products
    if product.in_stock and product.price <= 200
]
```

Use comprehensions when the transformation stays readable. If the condition grows complex, move it into a named function.

---

## Dataclasses

```python
@dataclass(frozen=True)
class Product:
    name: str
    price: float
    in_stock: bool = True
```

Dataclasses give test data a clear shape without a lot of boilerplate.

---

## Assertions In Helpers

Helpers can raise focused assertions when they validate a reusable contract:

```python
assert_required_fields(payload, ["email", "password"])
```

The message should tell the reader exactly what is missing.

---

## Runnable Example

```bash
python course/session_03_python_foundations/lecture.py
pytest course/session_03_python_foundations -q
```

The reusable implementation lives in `course/framework/python_basics/`.

---

## Session Completion Checklist

- [ ] I can explain the difference between a list and a dictionary.
- [ ] I wrote one function that returns a value.
- [ ] I wrote one list comprehension.
- [ ] I created one dataclass for test data.
- [ ] I wrote one test for a helper function.
- [ ] I completed the exercises in `EXERCISES.md`.
