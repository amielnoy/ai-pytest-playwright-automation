Review the test files specified by: $ARGUMENTS

If no argument is given, review all files under `tests/` that were changed in the current git branch.

## What to check

For each file, scan for the following anti-patterns and report every finding:

1. **Inline selectors** — raw `locator()`, `get_by_role()`, `fill()`, or `click()` calls inside test functions instead of page objects.
2. **time.sleep()** — any `time.sleep()` or `asyncio.sleep()` call instead of Playwright auto-wait.
3. **Bare assert on DOM** — `assert element.inner_text() == ...` or `assert page.title() == ...` without `expect()`.
4. **Hardcoded values** — credentials, base URLs, or search terms written as string literals in test functions.
5. **Shared mutable state** — class-level or module-level variables that tests write to (causes flakiness in parallel runs).
6. **Missing teardown** — browser contexts or API sessions opened in a test without `yield` + cleanup, or without using a fixture.
7. **Missing Allure decorators** — test class without `@allure.feature`, test method without `@allure.title` or `@allure.severity`.
8. **Missing marker** — test class or function not tagged with a marker from `pytest.ini`.

## Output format

For each finding output exactly:

```
FILE:LINE  [SEVERITY]  Description of the problem.
           Fix: one-line concrete fix suggestion.
```

Severity levels: HIGH (will cause failures), MED (will cause flakiness or bad reports), LOW (style / maintainability).

At the end, output a summary table:

| File | HIGH | MED | LOW |
|---|---|---|---|
| ... | ... | ... | ... |

If no issues are found in a file, print `OK: <filename>`.
