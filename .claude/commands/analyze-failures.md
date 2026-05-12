Analyze the most recent test failures and produce a root-cause report.

Additional context or a path to a JUnit XML file: $ARGUMENTS

## Steps

1. **Find the failure data** — in order of preference:
   - If a path to a `.xml` file is given in `$ARGUMENTS`, parse it.
   - Otherwise, look for `results.xml` or any `*.xml` in `tmp-allure/` or `allure-results/`.
   - Otherwise, run `pytest --lf --tb=short -q` to re-run only the last-failed tests and capture output.

2. **Bucket failures by type** before sending to the AI:
   - `timeout` — message contains "timeout" or "timed out" → timing / infra issue
   - `selector` — message contains "locator", "selector", or "element not found" → broken selector / DOM change
   - `assertion` — message contains "AssertionError" or "expected" → product defect
   - `network` — message contains "connection", "DNS", or "refused" → infra issue
   - `other` — everything else

3. **Produce a Markdown report** with this structure for each failure:

   ### `<test_name>` — `<bucket>`
   **File:** `<file>:<line>`
   **Error:** `<exact error message, truncated to 300 chars>`
   **Likely root cause:** one sentence.
   **Suggested fix:** one sentence, concrete and actionable.
   **Confidence:** high | medium | low

4. **Group related failures** — if multiple tests failed for the same likely reason (e.g. a selector change), group them under one heading.

5. **End with a priority list** — rank failures by impact (HIGH = blocks other tests or reflects a product defect, MED = isolated test issue, LOW = infra / transient).

Output the full Markdown report. Do not truncate.
