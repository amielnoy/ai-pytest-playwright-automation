# Session 16 — CI/CD & AI Failure Analysis

## Learning Objectives

By the end of this session you will be able to:

- Configure a two-job GitHub Actions pipeline that runs tests and publishes an Allure report.
- Parse JUnit XML output to extract failures and feed them to Claude for root-cause analysis.
- Apply heuristic bucketing to reduce prompt size before sending failures to the AI.
- Post an AI-generated failure summary as a GitHub PR comment via the REST API.
- Detect flaky tests by querying the GitHub Actions API and flag them in a GitHub Issue.
- Store secrets safely using GitHub repository secrets and reference them in workflows.

---

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

---

## Secrets Management

Test suites often need credentials: API keys, login passwords, tokens. Handling these incorrectly is the most common security mistake in CI pipelines.

**The rules:**

1. **Never commit secrets to git.** Not in `config.json`, not in `.env`, not commented out. Use `git log -S "my_password"` to confirm nothing leaked.
2. **Use GitHub repository secrets** (`Settings → Secrets and variables → Actions`) for CI. Reference them in workflows as `${{ secrets.MY_KEY }}`.
3. **Use environment variables locally.** Load them with `os.environ.get("MY_KEY")` — never `os.environ["MY_KEY"]` (the latter raises `KeyError` in CI if the variable is missing, which masks the real error).
4. **Provide a `.example` file.** `data/secrets.json.example` shows the shape of the file without real values. New team members copy it and fill in their own credentials.

**GitHub Actions example:**

```yaml
- name: Run tests
  env:
    APP_PASSWORD: ${{ secrets.APP_PASSWORD }}
    API_KEY: ${{ secrets.API_KEY }}
  run: pytest tests/
```

**Local development with a `.env` file:**

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
import os

load_dotenv()          # reads .env file if present; no-op if absent
password = os.environ.get("APP_PASSWORD", "")
```

Add `.env` to `.gitignore`. Never add `secrets.json` to git (check `.gitignore` in this project).

---

## Session Completion Checklist

Before moving to Session 17, verify you can answer yes to each item:

- [ ] I have a GitHub Actions workflow that installs dependencies, runs pytest, and uploads `allure-results` as an artifact.
- [ ] I ran `analyze_failures.py` against a JUnit XML file and received a Markdown failure summary from Claude.
- [ ] I can explain the five heuristic buckets and which keyword triggers each one.
- [ ] I stored at least one secret in GitHub repository secrets and referenced it in a workflow without hardcoding it.
- [ ] I ran `flaky_detector.py` and understood what success rate and `MIN_RUNS` control.
- [ ] I completed the exercises in `EXERCISES.md`.
