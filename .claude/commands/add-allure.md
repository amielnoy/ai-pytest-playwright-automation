Add complete Allure decorators to the test file(s): $ARGUMENTS

If no argument is given, apply to all test files under `tests/` that are missing decorators.

## What to add

### On every test class
```python
@allure.feature("Feature area — e.g. Cart, Registration, Search")
@allure.story("Specific story — e.g. Add to cart, Register new user")
class TestName:
```

### On every test method
```python
@allure.title("Human-readable title — e.g. Adding one item shows badge count of 1")
@allure.severity(allure.severity_level.CRITICAL)  # choose the right level
def test_name(self, ...):
```

**Severity mapping:**
- `BLOCKER` — failure blocks the release (login, checkout payment)
- `CRITICAL` — core feature broken (add to cart, search)
- `NORMAL` — important but has a workaround
- `MINOR` — cosmetic or low-impact
- `TRIVIAL` — negligible impact

### Inside test methods
Wrap every logical group of actions with `with allure.step("verb + object"):`.

Good step names: "Navigate to login page", "Submit registration form", "Assert cart badge shows 1 item"
Bad step names: "Step 1", "Do thing", "Assert"

### Required import
```python
import allure
```

## Rules
- Do NOT change any test logic, assertions, or fixture usage.
- Do NOT rename test functions or classes.
- Infer the feature and story from the file name and test names — do not invent them.
- After editing, run `pytest --collect-only -q <file>` to confirm nothing is broken.

Output each modified file in full.
