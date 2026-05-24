# Session 1 — Exercises

> ✏️ **Exercises** · [session_01_qa_foundations](.) · [Lecture notes](lecture.md)


## 📤 How to Submit

Create one Markdown file named `session_01_answers.md`.
Use the same headings as the exercises below.
Where a task asks for test cases or bug reports, write them as tables so they can be reviewed quickly.

## ✔️ Review Criteria

Your work is complete when:

- Every test case has all seven required fields.
- Steps are atomic and numbered.
- Expected results are concrete and observable.
- Boundary values include both valid and invalid sides of each boundary.
- Bug reports include exact environment, actual result, expected result, severity, priority, and evidence.

---

## ✏️ Exercise 1: Write a Test Case from Scratch

**Scenario:** A registered user tries to log in with a correct username but wrong password.

Write a complete test case with all seven fields: ID, title, priority, type, precondition, steps, and expected result. Make every step atomic and the expected result concrete (include the exact error text that appears on screen).

**Self-check:** If the error text is unknown, execute the scenario once and copy it exactly. Do not invent the message.

---

## ✏️ Exercise 2: Apply EP and BVA

The registration form requires a username between 3 and 20 characters.

1. List all equivalence partitions for the username field.
2. For each boundary (min, min-1, max, max+1), state the input value and expected result.
3. Write one test case per boundary value.

**Expected boundary set:** 2 characters, 3 characters, 20 characters, 21 characters.

---

### 🔐 Cybersecurity Variant

A password-reset API accepts a one-time token that must be **exactly 64 hexadecimal characters** long.  
Tokens that are too short, too long, contain non-hex characters, or are reused must be rejected.

1. List the equivalence partitions for the token field (valid, too short, too long, invalid charset, already used).
2. Identify the boundaries and write one test case per boundary value.
3. Add one negative case for a structurally valid token that has already been consumed.

**Expected boundary set:** 63 chars, 64 chars (valid), 65 chars — plus one non-hex input and one reused token.

> [!TIP]
> A token that is the right length but contains `g`, `z`, or spaces is a separate partition from "too long" — length passes, charset fails. Keep partitions clean.

---

### 💳 FinTech Variant

A wire-transfer form accepts an amount in USD with the rule:  
**minimum $0.01 — maximum $999,999.99** (two decimal places, no negative values, no zero).

1. List all equivalence partitions (valid range, below minimum, above maximum, zero, negative, non-numeric, too many decimal places).
2. For each boundary write the exact input value and expected result.
3. Write one test case per boundary value.

**Expected boundary set:** `$0.00`, `$0.01`, `$999,999.99`, `$1,000,000.00` — plus `$0.001` (too many decimals) and `-$1.00` (negative).

> [!TIP]
> Formatting edge cases (`1000000` vs `1,000,000.00` vs `1.000.000,00`) are a separate partition from the numeric range — they test input parsing, not business logic. List them separately.

---

## ✏️ Exercise 3: Decision Table

The site applies a 10% discount when:
- The user is a premium member, **and**
- The cart total is over $50.

Build a full decision table (all combinations) and write one test case per column.

**Hint:** Two boolean conditions produce four columns. Do not skip the "premium member with exactly $50" clarification if your rule says "over $50".

---

## ✏️ Exercise 4: Bug Report

Go to `https://tutorialsninja.com/demo` and intentionally try to break something (e.g. search for an empty string, add 0 quantity, navigate directly to the checkout URL without a cart).

Write a complete bug report using the template from `bug_report.py`. Include steps that reproduce the issue 100% of the time.

**Evidence required:** screenshot or copied browser/console/network error. If the behaviour is not a bug, write a short "not a bug" note and explain the product rule you verified.

---

## ✏️ Exercise 5: Automation ROI Decision

For each scenario below, decide whether to automate. Write one sentence explaining the ROI logic.

1. Login with valid credentials — runs on every commit in a suite of 200 tests.
2. A new onboarding wizard that the product team is redesigning every two weeks.
3. Checking that prices display with two decimal places across 50 product pages.
4. A usability review of the checkout flow with a screen reader.
5. Regression tests for a feature that has been stable for 18 months.

---

## ✏️ Exercise 6: Exploratory Charter

Write one 30-minute exploratory testing charter for either search, cart, or checkout.
Use this format:

| Field | Value |
| --- | --- |
| Area | |
| Mission | |
| Risks | |
| Data to use | |
| Time box | |
| Notes to capture | |

After executing it, summarize:

- Bugs found.
- Questions for product or development.
- Areas covered.
- Areas still untested.
