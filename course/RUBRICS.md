# Course Rubrics

## Exercise Rubric

| Level | Criteria |
|---|---|
| Pass | Solves the requested behavior, runs with a focused command, and has a concrete assertion. |
| Strong | Also uses the correct framework layer, stable data, and readable names. |
| Excellent | Also includes useful failure output, cleanup, and a short learning note. |

## Automation Quality Gates

- No raw selectors in test files.
- Role, label, text, or test-id locators are preferred over CSS/XPath.
- Setup is explicit through fixtures or API helpers.
- Data is isolated and parallel-safe.
- Assertions are specific and behavior-focused.
- Allure names and steps help explain failures.
- The narrowest relevant command was run and recorded.

## Review Rubric

A good review finding includes file, line or area, risk, impact, and a concrete fix.
