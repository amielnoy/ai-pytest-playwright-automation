# Session 3 — Python Foundations For Automation Testing

## Learning Objectives

By the end of this session you will be able to:

- Use variables, strings, numbers, booleans, lists, and dictionaries in test code.
- Write small functions with clear inputs and outputs.
- Use list comprehensions for readable test-data transformations.
- Create simple `dataclass` models for structured test data.
- Raise useful assertion failures from helper functions.
- Read Python code in the rest of the automation framework with confidence.

---

## Session Flow

| Time | Activity | Output |
| --- | --- | --- |
| 0:00-0:15 | Python in automation code | Identify strings, lists, dictionaries, functions in real tests |
| 0:15-0:40 | Core data types and naming | Small test-data variables |
| 0:40-1:05 | Functions and assertions | Reusable helper with focused failure message |
| 1:05-1:30 | Lists, comprehensions, and dictionaries | Filter product data |
| 1:30-1:50 | Dataclasses and test IDs | Structured product model and stable ID helper |
| 1:50-2:00 | Run tests and review failures | Passing targeted pytest run |

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

Automation code mostly moves text, numbers, booleans, lists, and dictionaries between the browser, APIs, files, and assertions.

```python
product_name = "MacBook"
price = 602.00
in_stock = True
tags = ["laptop", "featured"]
payload = {"email": "student@example.com", "password": "secret"}
```

Good automation code uses simple types until structure is needed.

| Type | Automation use | Example |
| --- | --- | --- |
| `str` | selectors, URLs, error messages, test IDs | `"button[type='submit']"` |
| `int` / `float` | quantities, prices, status codes, timeouts | `status_code = 201` |
| `bool` | feature flags, stock state, validation results | `is_visible = True` |
| `list` | result rows, products, cases, required fields | `["email", "password"]` |
| `dict` | API payloads, JSON responses, config | `{"quantity": 1}` |

### Naming rule

Name variables after the business meaning, not the technical type:

```python
# Clear
checkout_total = 90.00
required_fields = ["email", "password"]

# Weak
value = 90.00
list1 = ["email", "password"]
```

---

## Functions

Functions should do one clear job:

```python
def parse_price(raw_price: str) -> float:
    cleaned = raw_price.replace("$", "").replace(",", "").strip()
    return float(cleaned)
```

This is easier to test than repeating parsing logic inside UI tests.

Good helper functions for automation:

- Accept explicit inputs.
- Return a value or raise a focused assertion.
- Avoid hidden browser, file, or network state unless the function name makes that dependency obvious.
- Are small enough to test with two or three examples.

### Function shape

```python
def function_name(input_value: InputType) -> OutputType:
    transformed = ...
    return transformed
```

Type hints are not required for Python to run, but they help the next person understand what the helper expects.

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

Equivalent loop:

```python
cheap_products = []
for product in products:
    if product.in_stock and product.price <= 200:
        cheap_products.append(product)
```

The comprehension is shorter, but the loop is easier to debug for beginners. Use the one the team can maintain.

### Dictionaries for API payloads

```python
user_payload = {
    "email": "student@example.com",
    "password": "secret",
    "first_name": "Student",
}
```

Dictionaries are how Python represents JSON-like data. In tests, validate both required keys and meaningful values.

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

Use a dataclass when several fields travel together and the object has a real domain meaning:

- `Product`
- `User`
- `Address`
- `Order`

Do not create a class for every two-line helper. Start with dictionaries or simple variables, then promote to a dataclass when structure improves readability.

---

## Assertions In Helpers

Helpers can raise focused assertions when they validate a reusable contract:

```python
assert_required_fields(payload, ["email", "password"])
```

The message should tell the reader exactly what is missing.

Example failure message:

```text
Missing required fields: email, password
```

This is better than `AssertionError` because it points directly to the broken contract.

---

## Reading Tracebacks

When a test fails, read from the bottom up:

1. Final line: exception type and message.
2. Previous few lines: exact assertion or function call that failed.
3. File path and line number: where to open the code.
4. Variables shown by pytest: what values were compared.

Do not fix the first line you see. First identify whether the failure is in the test data, helper function, product behaviour, or expectation.

---

## Course Code Map

| File | Purpose |
| --- | --- |
| `course/framework/python_basics/core.py` | Reusable helpers used by this session |
| `course/session_03_python_foundations/lecture.py` | Runnable demo that prints helper output |
| `course/session_03_python_foundations/test_python_foundations.py` | Pytest coverage for the helpers |
| `course/session_03_python_foundations/EXERCISES.md` | Practice tasks |

---

## Runnable Example

```bash
python course/session_03_python_foundations/lecture.py
pytest course/session_03_python_foundations -q
```

The reusable implementation lives in `course/framework/python_basics/`.

Expected result:

- The lecture script prints normalized text, product names, affordable products, and a test ID.
- Pytest reports all session 3 tests passing.

---

## Session Completion Checklist

- [ ] I can explain the difference between a list and a dictionary.
- [ ] I wrote one function that returns a value.
- [ ] I wrote one list comprehension.
- [ ] I created one dataclass for test data.
- [ ] I wrote one test for a helper function.
- [ ] I completed the exercises in `EXERCISES.md`.
