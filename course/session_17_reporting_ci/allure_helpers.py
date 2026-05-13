"""
Session 17 — Reporting & CI: Allure 3 + GitHub Pages
Helpers for:
  - Writing categories.json and environment.properties into allure-results/
  - Validating that test files use Allure decorators correctly
  - Summarising an allure-results directory before generating the report

Usage:
    python allure_helpers.py setup          # write categories + environment files
    python allure_helpers.py validate       # check test files for missing decorators
    python allure_helpers.py summarise      # count results by status
"""

import json
import os
import re
import sys
from pathlib import Path

RESULTS_DIR = Path("allure-results")

CATEGORIES = [
    {
        "name": "Flaky tests",
        "messageRegex": ".*TimeoutError.*",
        "matchedStatuses": ["broken", "failed"],
    },
    {
        "name": "Product defects",
        "messageRegex": ".*AssertionError.*",
        "matchedStatuses": ["failed"],
    },
    {
        "name": "Infrastructure issues",
        "messageRegex": ".*ConnectionError.*|.*DNS.*",
        "matchedStatuses": ["broken"],
    },
    {
        "name": "Missing selectors",
        "messageRegex": ".*locator.*|.*selector.*",
        "matchedStatuses": ["broken", "failed"],
    },
]


def write_categories(results_dir: Path = RESULTS_DIR) -> None:
    """Write categories.json so Allure groups failures by type on the Categories tab."""
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / "categories.json"
    out.write_text(json.dumps(CATEGORIES, indent=2))
    print(f"Written: {out}")


def write_environment(results_dir: Path = RESULTS_DIR) -> None:
    """Write environment.properties so the Overview tab shows run context."""
    results_dir.mkdir(parents=True, exist_ok=True)
    import subprocess

    python_version = sys.version.split()[0]
    try:
        allure_version = subprocess.check_output(
            ["npx", "allure", "--version"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        allure_version = "unknown"

    props = {
        "Browser": "Chromium",
        "Base.URL": "https://tutorialsninja.com/demo",
        "Python.Version": python_version,
        "Allure.Version": allure_version,
        "CI": os.environ.get("CI", "local"),
        "Branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "Run.Number": os.environ.get("GITHUB_RUN_NUMBER", "0"),
    }
    lines = "\n".join(f"{k}={v}" for k, v in props.items())
    out = results_dir / "environment.properties"
    out.write_text(lines + "\n")
    print(f"Written: {out}")


def validate_allure_decorators(tests_dir: Path = Path("tests")) -> list[dict]:
    """Scan test files and report functions missing required Allure decorators.

    Returns a list of findings: {file, line, function, missing}.
    """
    required = {"allure.title", "allure.severity"}
    findings = []

    for py_file in sorted(tests_dir.rglob("test_*.py")):
        source = py_file.read_text()
        lines = source.splitlines()
        for i, line in enumerate(lines):
            if not re.match(r"\s+def (test_\w+)", line):
                continue
            fn_name = re.search(r"def (test_\w+)", line).group(1)  # type: ignore[union-attr]
            # look back up to 10 lines for decorators
            context = "\n".join(lines[max(0, i - 10): i])
            missing = [d for d in required if d not in context]
            if missing:
                findings.append(
                    {"file": str(py_file), "line": i + 1, "function": fn_name, "missing": missing}
                )

    return findings


def summarise_results(results_dir: Path = RESULTS_DIR) -> dict[str, int]:
    """Count test results by status from allure-results JSON files."""
    counts: dict[str, int] = {}
    for result_file in results_dir.glob("*-result.json"):
        try:
            data = json.loads(result_file.read_text())
            status = data.get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
        except json.JSONDecodeError:
            continue
    return counts


def print_summary(results_dir: Path = RESULTS_DIR) -> None:
    counts = summarise_results(results_dir)
    if not counts:
        print(f"No result files found in {results_dir}/")
        return
    total = sum(counts.values())
    print(f"\nAllure results summary ({total} tests):")
    for status, n in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * n
        print(f"  {status:<10} {n:>4}  {bar}")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "setup"

    if command == "setup":
        write_categories()
        write_environment()

    elif command == "validate":
        findings = validate_allure_decorators()
        if not findings:
            print("All test functions have required Allure decorators.")
        else:
            print(f"{len(findings)} function(s) missing decorators:\n")
            for f in findings:
                print(f"  {f['file']}:{f['line']}  {f['function']}  missing: {f['missing']}")

    elif command == "summarise":
        print_summary()

    else:
        print(f"Unknown command: {command}. Use: setup | validate | summarise")
        sys.exit(1)
