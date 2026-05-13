# Session 24 — Exercises

## Exercise 1: Generate a Test with /generate-test

1. Run `/generate-test user can sort products from Z to A` in Claude Code.
2. Inspect the output:
   - Is the file placed in `tests/web-ui/`?
   - Does it use a page object from `pages/`?
   - Are Allure decorators present?
   - Does `pytest --collect-only -q` collect it without errors?
3. If any rule was violated, update the command file in `.claude/commands/generate-test.md` to fix the gap, then re-run.

---

## Exercise 2: Review Your Own Tests with /review-tests

1. Run `/review-tests tests/web-ui/` against the full UI test directory.
2. For each HIGH finding:
   - Is it accurate? (Not a false positive?)
   - Fix it, then re-run the command to confirm the finding disappears.
3. For each MED finding, decide whether to fix it now or add it to a backlog item.
4. Write one sentence explaining which anti-pattern is hardest to catch with static analysis alone.

---

## Exercise 3: Create a Page Object with /create-page-object

1. Run `/create-page-object wish list page` (the wishlist is accessible after logging in).
2. Verify Claude navigated the real site before writing the locators (check the Playwright MCP tool calls).
3. Open the generated file and audit every locator against the stability hierarchy.
4. If any locator is rank 7 or lower, ask Claude to fix it: `/fix-selectors pages/wish_list_page.py`

---

## Exercise 4: Analyze Failures with /analyze-failures

1. Intentionally break two tests in different ways:
   - Break one locator (selector issue)
   - Change an assertion to expect the wrong text (assertion failure)
2. Run `pytest --junitxml=results.xml` to generate the failure XML.
3. Run `/analyze-failures results.xml`.
4. Evaluate the report:
   - Were both failures correctly bucketed?
   - Was the root cause accurate for each?
   - Was the fix suggestion actionable without further research?

---

## Exercise 5: Write a Custom Slash Command

Write a new command `.claude/commands/std-to-test.md` that:

1. Takes the path to a test design document (STD) in `stds/` as `$ARGUMENTS`.
2. Reads the STD file.
3. Generates a pytest test file with one test per test case in the STD.
4. Places the file in the correct `tests/` subdirectory based on the STD content.
5. Runs `pytest --collect-only -q` on the output file.

Test it by running `/std-to-test stds/STD_AddToCart.md` and verifying the generated tests match the STD cases.
