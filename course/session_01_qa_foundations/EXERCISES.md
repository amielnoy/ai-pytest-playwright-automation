# Session 1 — Exercises

## Exercise 1: Write a Test Case from Scratch

**Scenario:** A registered user tries to log in with a correct username but wrong password.

Write a complete test case with all seven fields: ID, title, priority, type, precondition, steps, and expected result. Make every step atomic and the expected result concrete (include the exact error text that appears on screen).

---

## Exercise 2: Apply EP and BVA

The registration form requires a username between 3 and 20 characters.

1. List all equivalence partitions for the username field.
2. For each boundary (min, min-1, max, max+1), state the input value and expected result.
3. Write one test case per boundary value.

---

## Exercise 3: Decision Table

The site applies a 10% discount when:
- The user is a premium member, **and**
- The cart total is over $50.

Build a full decision table (all combinations) and write one test case per column.

---

## Exercise 4: Bug Report

Go to `https://tutorialsninja.com/demo` and intentionally try to break something (e.g. search for an empty string, add 0 quantity, navigate directly to the checkout URL without a cart).

Write a complete bug report using the template from `bug_report.py`. Include steps that reproduce the issue 100% of the time.

---

## Exercise 5: Automation ROI Decision

For each scenario below, decide whether to automate. Write one sentence explaining the ROI logic.

1. Login with valid credentials — runs on every commit in a suite of 200 tests.
2. A new onboarding wizard that the product team is redesigning every two weeks.
3. Checking that prices display with two decimal places across 50 product pages.
4. A usability review of the checkout flow with a screen reader.
5. Regression tests for a feature that has been stable for 18 months.
