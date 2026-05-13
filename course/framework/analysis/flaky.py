"""Session 16 — flaky test detector: scans workflow runs and opens a GitHub issue."""
import collections
import os
import requests

_GH = "https://api.github.com"
_REPO = os.environ.get("REPO", "")
_HEADERS = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}"}
FLAKY_THRESHOLD = 0.95
MIN_RUNS = 5


def get_recent_runs(workflow_file: str = "tests.yml", per_page: int = 30) -> list[dict]:
    url = f"{_GH}/repos/{_REPO}/actions/workflows/{workflow_file}/runs?per_page={per_page}"
    return requests.get(url, headers=_HEADERS).json().get("workflow_runs", [])


def collect_results(runs: list[dict]) -> dict[str, dict]:
    results: dict[str, dict] = collections.defaultdict(lambda: {"pass": 0, "fail": 0})
    for run in runs:
        artifacts = requests.get(run["artifacts_url"], headers=_HEADERS).json().get("artifacts", [])
        _ = artifacts  # download + parse each JUnit XML here (see analysis/failures.py)
    return results


def find_flaky(results: dict[str, dict]) -> list[tuple[str, float, int]]:
    flaky = []
    for name, counts in results.items():
        total = counts["pass"] + counts["fail"]
        if total < MIN_RUNS:
            continue
        rate = counts["pass"] / total
        if rate < FLAKY_THRESHOLD:
            flaky.append((name, rate, total))
    return flaky


def open_flaky_issue(flaky: list[tuple[str, float, int]]) -> int:
    lines = ["## Flaky Tests Detected", "", "| Test | Success Rate | Runs |", "|---|---|---|"]
    for name, rate, total in sorted(flaky, key=lambda x: x[1]):
        badge = "🔴" if rate < 0.7 else "🟠" if rate < 0.9 else "🟡"
        lines.append(f"| `{name}` | {badge} {rate:.0%} | {total} |")
    r = requests.post(
        f"{_GH}/repos/{_REPO}/issues",
        headers=_HEADERS,
        json={
            "title": f"Flaky tests — {len(flaky)} tests intermittently failing",
            "body": "\n".join(lines),
            "labels": ["flaky", "qa"],
        },
    )
    return r.status_code
