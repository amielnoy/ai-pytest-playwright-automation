"""
Session 16 — CI/CD + AI Failure Analysis
Parses JUnit XML test results from CI artifacts, sends failures to Claude,
and posts an AI-generated summary as a GitHub PR comment.

Required env vars:
    ANTHROPIC_API_KEY
    GITHUB_TOKEN
    PR_NUMBER
    REPO  (e.g. "owner/repo")
"""

import os
import glob
import requests
import anthropic
import xml.etree.ElementTree as ET

client = anthropic.Anthropic()


def collect_failures(artifacts_glob: str = "artifacts/**/*.xml") -> list[dict]:
    failures = []
    for xml_file in glob.glob(artifacts_glob, recursive=True):
        tree = ET.parse(xml_file)
        for tc in tree.iter("testcase"):
            failure = tc.find("failure")
            if failure is not None:
                failures.append(
                    {
                        "test": tc.attrib.get("name"),
                        "file": tc.attrib.get("classname"),
                        "message": (failure.text or "")[:2000],
                    }
                )
    return failures


def analyze_with_claude(failures: list[dict]) -> str:
    prompt = (
        "You are a senior SDET. Analyze these test failures and produce a Markdown summary "
        "for a PR comment. For each failure: 1) likely root cause, 2) one-line fix suggestion, "
        "3) confidence (high/med/low). Group by likely cause if related.\n\n"
        f"Failures:\n{failures}"
    )
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def post_pr_comment(summary: str) -> int:
    gh_token = os.environ["GITHUB_TOKEN"]
    pr = os.environ["PR_NUMBER"]
    repo = os.environ["REPO"]
    url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    body = f"## AI Failure Analysis\n\n{summary}"
    r = requests.post(
        url,
        json={"body": body},
        headers={"Authorization": f"Bearer {gh_token}"},
    )
    return r.status_code


def group_by_cause(failures: list[dict]) -> dict[str, list[dict]]:
    """Heuristically bucket failures by common root-cause keywords in the message."""
    buckets: dict[str, list[dict]] = {
        "timeout": [],
        "assertion": [],
        "selector": [],
        "network": [],
        "other": [],
    }
    for f in failures:
        msg = (f.get("message") or "").lower()
        if "timeout" in msg or "timed out" in msg:
            buckets["timeout"].append(f)
        elif "assert" in msg or "expected" in msg:
            buckets["assertion"].append(f)
        elif "selector" in msg or "locator" in msg or "element" in msg:
            buckets["selector"].append(f)
        elif "connection" in msg or "network" in msg or "dns" in msg:
            buckets["network"].append(f)
        else:
            buckets["other"].append(f)
    return {k: v for k, v in buckets.items() if v}


def trend_report(history: list[list[dict]]) -> str:
    """Given failure lists from N consecutive runs, return a Markdown trend table.

    history[0] is the oldest run, history[-1] is the latest.
    """
    from collections import Counter

    counts = [Counter(f["test"] for f in run) for run in history]
    all_tests = {t for c in counts for t in c}
    lines = ["| Test | " + " | ".join(f"Run {i+1}" for i in range(len(history))) + " |"]
    lines.append("|---|" + "---|" * len(history))
    for test in sorted(all_tests):
        row = " | ".join("FAIL" if c.get(test) else "pass" for c in counts)
        lines.append(f"| `{test}` | {row} |")
    return "\n".join(lines)


if __name__ == "__main__":
    failures = collect_failures()
    if not failures:
        print("No failures to analyze")
    else:
        print("Groups:", {k: len(v) for k, v in group_by_cause(failures).items()})
        summary = analyze_with_claude(failures)
        status = post_pr_comment(summary)
        print(f"PR comment posted: {status}")
