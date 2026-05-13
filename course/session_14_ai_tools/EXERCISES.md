# Session 14 — Exercises

## Exercise 1: Improve the Generation Prompt

Run `cli.py test` for the feature "User can sort products alphabetically (A to Z and Z to A)".

1. Inspect the output — does it use `get_by_role`/`get_by_label` or CSS/XPath?
2. Does it have at least one positive test, one negative test, and one edge case?
3. Update the generation prompt in `cli.py` to fix any gaps, re-run, and compare.

---

## Exercise 2: Batch Generation

Create a file `features.txt` with five feature descriptions (one per line), covering different areas of the demo site.

Run `cli.py batch features.txt` and inspect the five generated files. For each file:
- Does it import from your project's page objects? (It won't unless you teach it to — explain why.)
- What would you need to add to the prompt to make it import from `pages/`?

---

## Exercise 3: Trigger Self-Healing

1. In `test_with_healing.py`, change one locator to a selector that does not exist (e.g. `[data-test="nonexistent"]`).
2. Run the test and confirm the `[self-heal]` line appears in output.
3. Confirm the healed selector actually works (test passes).
4. Now update the Page Object with the correct stable locator and remove the broken one.

---

## Exercise 4: Heal Report Analysis

Generate a heal report by running the suite several times after introducing multiple broken selectors.

Produce the Markdown table from `heal_report.py`. Answer:
- Which selector was healed most often?
- What does high heal frequency indicate about that part of the application?

---

## Exercise 5: Review an Existing Test File

Run `cli.py review` on `tests/web-ui/test_registration.py`. For each finding:
- Does the finding accurately identify a real problem?
- Is the suggested fix correct?
- If Claude missed a real issue, write a finding in the same format (file:line, severity, fix).
