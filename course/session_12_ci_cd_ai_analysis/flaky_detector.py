"""
Session 12 — CI/CD + AI Failure Analysis
Flaky test detector: scans the last 30 workflow runs, computes per-test success rates,
and opens a GitHub Issue listing tests with success rate < 95%.

Required env vars:
    GITHUB_TOKEN
    REPO  (e.g. "owner/repo")
"""

import os
import requests
import collections

GH = "https://api.github.com"
REPO = os.environ.get("REPO", "")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
FLAKY_THRESHOLD = 0.95
MIN_RUNS = 5


def get_recent_runs(workflow_file: str = "regression.yml", per_page: int = 30) -> list[dict]:
    url = f"{GH}/repos/{REPO}/actions/workflows/{workflow_file}/runs?per_page={per_page}"
    return requests.get(url, headers=HEADERS).json().get("workflow_runs", [])


def collect_test_results(runs: list[dict]) -> dict[str, dict]:
    test_results: dict[str, dict] = collections.defaultdict(lambda: {"pass": 0, "fail": 0})
    for run in runs:
        artifacts = requests.get(run["artifacts_url"], headers=HEADERS).json().get("artifacts", [])
        # Full implementation would download + parse each JUnit XML artifact here.
        # Skipped for brevity — see analyze_failures.py for XML parsing pattern.
        _ = artifacts
    return test_results


def find_flaky(test_results: dict[str, dict]) -> list[tuple[str, float, int]]:
    flaky = []
    for name, counts in test_results.items():
        total = counts["pass"] + counts["fail"]
        if total < MIN_RUNS:
            continue
        success_rate = counts["pass"] / total
        if success_rate < FLAKY_THRESHOLD:
            flaky.append((name, success_rate, total))
    return flaky


def open_flaky_issue(flaky: list[tuple[str, float, int]]) -> int:
    body_lines = ["## Flaky Tests Detected (last 30 runs)", ""]
    body_lines.append("| Test | Success Rate | Runs |")
    body_lines.append("|---|---|---|")
    for name, rate, total in sorted(flaky, key=lambda x: x[1]):
        body_lines.append(f"| `{name}` | {rate:.0%} | {total} |")

    issue = {
        "title": f"Flaky tests — {len(flaky)} failing intermittently",
        "body": "\n".join(body_lines),
        "labels": ["flaky", "qa"],
    }
    r = requests.post(f"{GH}/repos/{REPO}/issues", headers=HEADERS, json=issue)
    return r.status_code


def flaky_rate_badge(rate: float) -> str:
    """Return a text badge indicating flakiness severity."""
    if rate >= 0.9:
        return "🟡 low"
    if rate >= 0.7:
        return "🟠 medium"
    return "🔴 high"


def print_flaky_table(flaky: list[tuple[str, float, int]]) -> None:
    print(f"{'Test':<60} {'Rate':>6}  {'Runs':>5}  Severity")
    print("-" * 85)
    for name, rate, total in sorted(flaky, key=lambda x: x[1]):
        print(f"{name:<60} {rate:>5.0%}  {total:>5}  {flaky_rate_badge(rate)}")


if __name__ == "__main__":
    runs = get_recent_runs()
    test_results = collect_test_results(runs)
    flaky = find_flaky(test_results)
    if flaky:
        print_flaky_table(flaky)
        status = open_flaky_issue(flaky)
        print(f"\nFlaky issue created: HTTP {status}")
    else:
        print("No flaky tests detected.")
