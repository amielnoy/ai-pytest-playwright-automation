Generate a complete pytest + Playwright test file for the following feature: $ARGUMENTS

## Rules

You must follow every convention in this project exactly.

### File placement
- Put the file in `tests/web-ui/test_<feature_slug>.py`
- If the feature is purely API-level, put it in `tests/api/test_<feature_slug>.py`

### Imports
Always start with:
```python
import allure
import pytest
from pages.<relevant_page> import <RelevantPage>
```
Never import `playwright` directly in a test file.

### Page objects
- All UI interactions go through a page object in `pages/`
- If the needed page object does not exist, create it in `pages/` first, then import it
- No raw `page.locator()`, `page.click()`, or `page.fill()` calls in test functions

### Allure decorators
Every class must have `@allure.feature(...)` and `@allure.story(...)`.
Every test method must have `@allure.title(...)` and `@allure.severity(allure.severity_level.CRITICAL | NORMAL | MINOR)`.
Wrap each logical step with `with allure.step("...")`.

### Assertions
Use `expect()` from `playwright.sync_api` — never bare `assert` on DOM values.

### Test data
Load data with `utils.data_loader.get_test_data(key)` — never hardcode credentials, URLs, or search terms.
Use `faker` for generated data (names, emails, addresses).

### Markers
Tag the class with the correct pytest marker from `pytest.ini`: `registration`, `search`, `cart`, `api`, or `contract`.

### Coverage minimum
Include at least:
- 1 positive (happy path) test
- 1 negative test (invalid input or error state)
- 1 edge case (boundary, empty, or unexpected input)

### Output
Output ONLY the Python file content — no explanation, no markdown fences.
After writing the file, run `pytest --collect-only -q <path>` to confirm collection succeeds.
