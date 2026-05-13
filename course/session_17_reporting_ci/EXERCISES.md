# Session 17 — Exercises

## Exercise 1: Decorate a Full Test Class

Pick one test file from `tests/web-ui/` that is missing Allure decorators.

Add:
- `@allure.feature(...)` on the class.
- `@allure.story(...)` on each test method.
- `@allure.title(...)` on each test method.
- `@allure.severity(...)` on each test method (choose the correct level: BLOCKER, CRITICAL, NORMAL, MINOR, TRIVIAL).
- At least three `with allure.step(...)` blocks inside one test.

Generate the report and verify the decorators appear correctly.

---

## Exercise 2: categories.json

Create `allure-results/categories.json` that defines two custom categories:

1. **Selector failures** — matched when the failure message contains "locator" or "selector".
2. **Timeout failures** — matched when the failure message contains "timeout" or "timed out".

Trigger one of each failure type, generate the report, and confirm the failures appear under the correct category in the Categories tab.

---

## Exercise 3: environment.properties

Create `allure-results/environment.properties` with the following keys:

- `Browser` — the browser name from `config/config.json`.
- `BaseURL` — the base URL under test.
- `HeadlessMode` — true or false from config.
- `PythonVersion` — the Python version from `sys.version`.

Generate the report and verify the environment table appears on the Overview tab.

---

## Exercise 4: Trend History

1. Run the suite once and generate the report.
2. Copy `allure-report/history/` to `allure-results/history/`.
3. Run the suite again (optionally break a test to change the pass rate).
4. Generate the report again.
5. Confirm the Trend chart on the Overview tab shows two data points.

---

## Exercise 5: End-to-End Pipeline Verification

Push a commit that intentionally fails one test. Verify:

1. The test job fails and `allure-results/` is still uploaded as an artifact.
2. The report job runs (`if: always()`) and publishes the report to GitHub Pages.
3. The published report shows the failed test with the attached screenshot.
4. The Categories tab correctly classifies the failure.
