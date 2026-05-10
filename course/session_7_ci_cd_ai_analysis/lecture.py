"""
Session 7 — CI/CD + AI Failure Analysis
Key concepts: marker strategy, failure pipelines, flaky detection.
"""

# ── pytest marker strategy for CI ─────────────────────────────────────────────
MARKER_STRATEGY = {
    "smoke":       "Run on EVERY commit (< 2 min). Any failure blocks the PR.",
    "regression":  "Run on PR open/push (< 10 min). Failures block merge.",
    "flaky_prone": "Tagged but not blocking. Monitored by flaky_detector weekly.",
}

# ── CI pipeline stages ────────────────────────────────────────────────────────
CI_PIPELINE = [
    "1. test job:    pytest -m smoke --alluredir=allure-results  (always runs)",
    "2. test job:    pytest -m regression ... (on PR, after smoke passes)",
    "3. upload:      actions/upload-artifact allure-results/",
    "4. report job:  download → npx allure generate → deploy GitHub Pages",
    "5. analysis:    collect_failures() → analyze_with_claude() → post_pr_comment()",
    "6. flaky cron:  weekly: find_flaky() → open_flaky_issue() if rate < 95%",
]

# ── failure_record autouse fixture ────────────────────────────────────────────
# In CI (env CI=true), every failed test appends to ci-artifacts/failures.jsonl:
#   {"test": "test_login.py::test_login_happy_path", "message": "TimeoutError…"}
# analyze_failures.py reads this file and sends it to Claude for root-cause analysis.

# ── group_by_cause buckets ────────────────────────────────────────────────────
FAILURE_BUCKETS = {
    "timeout":   ["timeout", "timed out"],
    "assertion": ["assert", "expected"],
    "selector":  ["selector", "locator", "element"],
    "network":   ["connection", "network", "dns"],
    "other":     ["everything else"],
}

# ── Flaky threshold and remediation ───────────────────────────────────────────
FLAKY_RULES = {
    "threshold":   "< 95% pass rate over the last 30 runs → flagged as flaky.",
    "min_runs":    "At least 5 runs needed before a test is considered for flagging.",
    "remediation": [
        "Add explicit wait (expect().to_be_visible()) if race condition.",
        "Move flaky setup to API fixture (faster + deterministic).",
        "Quarantine: mark @pytest.mark.skip(reason='flaky #123') until fixed.",
        "Root cause: use explain_heal() or analyze_with_claude() on failure log.",
    ],
}

if __name__ == "__main__":
    print("CI pipeline:")
    for stage in CI_PIPELINE:
        print(f"  {stage}")
    print("\nFailure buckets:")
    for bucket, keywords in FAILURE_BUCKETS.items():
        print(f"  {bucket:<12} keywords: {keywords}")
    print("\nFlaky remediation:")
    for tip in FLAKY_RULES["remediation"]:
        print(f"  • {tip}")
