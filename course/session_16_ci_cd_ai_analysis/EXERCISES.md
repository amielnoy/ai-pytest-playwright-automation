# Session 16 — Exercises

## Exercise 1: Write the GitHub Actions Workflow

Write a `.github/workflows/test.yml` that:

1. Triggers on every push to `main` and every pull request.
2. Installs Python dependencies and Playwright Chromium.
3. Runs `pytest tests/ --junitxml=results.xml --alluredir=allure-results`.
4. Uploads `results.xml` and `allure-results/` as artifacts retained for 7 days.

Run the workflow by pushing a commit and confirm it passes in the Actions tab.

---

## Exercise 2: AI Failure Analysis

1. Intentionally break a test (change a selector to something that does not exist).
2. Push to CI so it fails and the JUnit XML is generated.
3. Run `analyze_failures.py` against the downloaded `results.xml`.
4. Evaluate Claude's output: is the root cause correct? Is the fix suggestion actionable?

---

## Exercise 3: Add a New Failure Bucket

The current bucketing logic does not handle `AssertionError` separately from generic `assert` failures.

1. Add a new bucket: `assertion` — triggered by `"AssertionError"` in the failure message.
2. Update the `group_by_cause()` function in `analyze_failures.py`.
3. Write a unit test that verifies a failure message containing `"AssertionError: expected True"` maps to the `assertion` bucket.

---

## Exercise 4: Secrets Audit

1. Run `git log --all -S "password" --oneline` in this repo. If anything appears, identify whether it contains a real secret.
2. Check that `data/secrets.json` is listed in `.gitignore`.
3. Add your `ANTHROPIC_API_KEY` to GitHub repository secrets and update the workflow from Exercise 1 to pass it as an environment variable.
4. Confirm `analyze_failures.py` reads the key from `os.environ.get("ANTHROPIC_API_KEY")` and not from a file.

---

## Exercise 5: Flaky Detector Threshold

In `flaky_detector.py`, the threshold is 95% and the minimum run count is 5.

1. Lower the threshold to 80% and the minimum to 3 and re-run the detector.
2. Does a new test get flagged? Is the flag a false positive?
3. Write one sentence explaining the trade-off between a low threshold (catches more flakiness) and a high threshold (reduces noise).
