"""Session 13 — write Allure categories/environment and validate decorator coverage."""
import json
import os
import re
import sys
from pathlib import Path

RESULTS_DIR = Path("allure-results")

CATEGORIES = [
    {"name": "Flaky tests",          "messageRegex": ".*TimeoutError.*",               "matchedStatuses": ["broken", "failed"]},
    {"name": "Product defects",      "messageRegex": ".*AssertionError.*",             "matchedStatuses": ["failed"]},
    {"name": "Infrastructure issues","messageRegex": ".*ConnectionError.*|.*DNS.*",    "matchedStatuses": ["broken"]},
    {"name": "Missing selectors",    "messageRegex": ".*locator.*|.*selector.*",       "matchedStatuses": ["broken", "failed"]},
]


def write_categories(results_dir: Path = RESULTS_DIR) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    out = results_dir / "categories.json"
    out.write_text(json.dumps(CATEGORIES, indent=2))
    print(f"[allure] written {out}")


def write_environment(results_dir: Path = RESULTS_DIR) -> None:
    import subprocess
    results_dir.mkdir(parents=True, exist_ok=True)
    try:
        allure_ver = subprocess.check_output(
            ["npx", "allure", "--version"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        allure_ver = "unknown"
    props = {
        "Browser":    "Chromium",
        "Python":     sys.version.split()[0],
        "Allure":     allure_ver,
        "CI":         os.environ.get("CI", "local"),
        "Branch":     os.environ.get("GITHUB_REF_NAME", "local"),
        "Run":        os.environ.get("GITHUB_RUN_NUMBER", "0"),
    }
    out = results_dir / "environment.properties"
    out.write_text("\n".join(f"{k}={v}" for k, v in props.items()) + "\n")
    print(f"[allure] written {out}")


def validate_decorators(tests_dir: Path = Path("tests")) -> list[dict]:
    """Return a list of test functions missing @allure.title or @allure.severity."""
    required = {"allure.title", "allure.severity"}
    findings = []
    for py_file in sorted(tests_dir.rglob("test_*.py")):
        source = py_file.read_text()
        lines = source.splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"\s+def (test_\w+)", line)
            if not m:
                continue
            context = "\n".join(lines[max(0, i - 10): i])
            missing = [d for d in required if d not in context]
            if missing:
                findings.append({"file": str(py_file), "line": i + 1,
                                  "function": m.group(1), "missing": missing})
    return findings


def summarise_results(results_dir: Path = RESULTS_DIR) -> dict[str, int]:
    counts: dict[str, int] = {}
    for f in results_dir.glob("*-result.json"):
        try:
            status = json.loads(f.read_text()).get("status", "unknown")
            counts[status] = counts.get(status, 0) + 1
        except json.JSONDecodeError:
            continue
    return counts
