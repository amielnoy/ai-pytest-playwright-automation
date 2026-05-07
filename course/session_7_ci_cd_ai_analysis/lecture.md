# Session 7 — CI/CD & AI Failure Analysis

## Why CI/CD for Test Automation?

Running tests locally is not enough. CI enforces that tests pass on every commit, on a clean machine, without manual intervention.
A good CI pipeline for a test suite does four things: installs dependencies, runs tests, generates a report, and notifies the team of failures.

This session adds a fifth step: **AI failure analysis** — automatically explaining why tests failed and posting the explanation as a PR comment.

---

## Parsing JUnit XML

pytest writes JUnit-compatible XML when given `--junitxml=results.xml`.
`analyze_failures.py` walks `artifacts/**/*.xml` with `glob`, parses each file with `xml.etree.ElementTree`, and collects every `<testcase>` that has a `<failure>` child.

Each failure becomes a dict: `{test, file, message}`. The message is capped at 2 000 chars to stay within the Claude prompt limit.

---

## AI Analysis with Claude

The collected failures are sent to Claude in a single prompt:

> "You are a senior SDET. Analyze these test failures and produce a Markdown summary. For each failure: 1) likely root cause, 2) one-line fix suggestion, 3) confidence (high/med/low). Group by likely cause if related."

Claude returns a structured Markdown block ready to paste into a PR comment.
The `post_pr_comment()` function uses the GitHub REST API to post it under the PR number from `$PR_NUMBER`.

---

## Heuristic Failure Bucketing

Before sending to Claude, `group_by_cause()` heuristically buckets failures by keyword:

- `timeout` / `timed out` → timing / infra issue
- `assert` / `expected` → test assertion failure (product defect)
- `selector` / `locator` / `element` → broken selector (DOM change)
- `connection` / `network` / `dns` → infrastructure issue
- everything else → `other`

Bucketing reduces prompt size when there are many failures and helps Claude group related issues.

---

## Flaky Test Detection

`flaky_detector.py` fetches the last 30 workflow runs from the GitHub API, collects pass/fail counts per test, and flags any test with a success rate below 95%.

Flaky tests are reported in a GitHub Issue with a table showing success rate and run count.
The `flaky_rate_badge()` helper adds a colour indicator: 🟡 low / 🟠 medium / 🔴 high flakiness.

The 95% threshold and 5-run minimum (`MIN_RUNS`) are configurable constants at the top of the file.
