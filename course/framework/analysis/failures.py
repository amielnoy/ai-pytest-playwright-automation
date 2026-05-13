"""Session 16 — parse JUnit XML failures and send them to Claude for analysis."""
import glob
import os
import xml.etree.ElementTree as ET
import anthropic

_client = anthropic.Anthropic()

_BUCKET_KEYWORDS: dict[str, list[str]] = {
    "timeout":   ["timeout", "timed out"],
    "assertion": ["assert", "expected"],
    "selector":  ["selector", "locator", "element"],
    "network":   ["connection", "network", "dns"],
}


def collect_failures(artifacts_glob: str = "artifacts/**/*.xml") -> list[dict]:
    """Parse JUnit XML artifacts and return a list of failure dicts."""
    failures = []
    for xml_file in glob.glob(artifacts_glob, recursive=True):
        tree = ET.parse(xml_file)
        for tc in tree.iter("testcase"):
            failure = tc.find("failure")
            if failure is not None:
                failures.append({
                    "test": tc.attrib.get("name"),
                    "file": tc.attrib.get("classname"),
                    "message": (failure.text or "")[:2_000],
                })
    return failures


def group_by_cause(failures: list[dict]) -> dict[str, list[dict]]:
    """Heuristically bucket failures by likely root cause."""
    buckets: dict[str, list[dict]] = {k: [] for k in _BUCKET_KEYWORDS}
    buckets["other"] = []
    for f in failures:
        msg = (f.get("message") or "").lower()
        matched = False
        for bucket, keywords in _BUCKET_KEYWORDS.items():
            if any(kw in msg for kw in keywords):
                buckets[bucket].append(f)
                matched = True
                break
        if not matched:
            buckets["other"].append(f)
    return {k: v for k, v in buckets.items() if v}


def analyze_with_claude(failures: list[dict]) -> str:
    """Send failures to Claude and return a Markdown PR comment."""
    prompt = (
        "You are a senior SDET. Analyze these test failures and produce a Markdown summary "
        "for a PR comment. For each failure: 1) likely root cause, 2) one-line fix suggestion, "
        "3) confidence (high/med/low). Group by likely cause if related.\n\n"
        f"Failures:\n{failures}"
    )
    resp = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2_000,
        messages=[{"role": "user", "content": prompt}],
    )
    return next((b.text for b in resp.content if hasattr(b, "text")), "")
