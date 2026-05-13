# Session 18 - Exercises

## Exercise 1: Build Your Four-Week Plan

Create a file named `learning_plan.md` with a four-week automation learning plan.

For each week include:

- Focus area.
- Two practice tasks.
- One measurable output.
- One verification command or review step.

Example measurable outputs:

- "One Playwright test with no raw selectors in the test body."
- "Two API tests using service classes."
- "One Allure report with a screenshot attached to a failing test."

---

## Exercise 2: Convert Manual Work to Automation Work

Choose one manual test case from Session 1.

Create a task breakdown table with these columns:

- Manual step.
- Automation layer.
- File to change.
- Assertion.
- Risk or flake concern.

Do not write code yet. The goal is to prove that the automation plan is sound before implementation.

---

## Exercise 3: Improve One Existing Test

Pick one test from `tests/web-ui/`.

Improve it by doing at least two of the following:

- Move a raw selector into a page object.
- Replace a weak assertion with a concrete assertion.
- Add an Allure step.
- Use test data from `data/test_data.json`.
- Reduce UI setup by using a service or fixture.

Run the narrowest relevant test command and record the result in your learning note.

---

## Exercise 4: Debugging Drill

Intentionally break one locator in a page object.

Run the affected test and collect:

- The failing command.
- The error message.
- Screenshot or trace location, if available.
- The root cause.
- The fix.

Restore the locator and confirm the test passes again.

---

## Exercise 5: Automation Portfolio Entry

Write a short portfolio entry for the work you completed in this session.

Include:

- Problem or behavior covered.
- Files changed.
- Test command used.
- Result.
- What you learned.
- What you would improve next.

Keep it factual. A good portfolio entry proves skill through working evidence, not broad claims.
