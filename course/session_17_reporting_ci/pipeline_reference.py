"""
Session 17 — Reporting & CI: Allure 3 + GitHub Pages
Reference guide for the two-job GitHub Actions pipeline that:
  1. Runs tests and uploads allure-results as an artifact
  2. Generates an Allure 3 HTML report and publishes it to GitHub Pages

See: .github/workflows/playwright-tests.yml
"""

# ── One-time repo setup ────────────────────────────────────────────────────────
SETUP_STEPS = [
    "Settings → Actions → General → Workflow permissions → Read and write",
    "Settings → Pages → Source: Deploy from a branch → gh-pages / (root)",
    "Settings → Secrets → Actions → New secret: TEST_SECRETS_JSON = <contents of data/secrets.json>",
]

# ── Pipeline structure ─────────────────────────────────────────────────────────
JOBS = {
    "test": {
        "purpose": "Run the full test suite and upload raw allure-results/",
        "runs_on": "ubuntu-latest",
        "key_steps": [
            "actions/checkout@v4",
            "actions/setup-python@v5  (Python 3.12, pip cache)",
            "pip install -r requirements.txt",
            "Write secrets.json from TEST_SECRETS_JSON secret",
            "Cache ~/.cache/ms-playwright keyed on requirements.txt hash",
            "playwright install chromium --with-deps  (only on cache miss)",
            "pytest tests/ -n auto --dist loadscope  (parallel by module)",
            "actions/upload-artifact@v4 → allure-results/  (retention 7 days)",
        ],
    },
    "report": {
        "purpose": "Download results, generate Allure 3 HTML, push to gh-pages branch",
        "needs": "test",
        "runs_on": "ubuntu-latest",
        "if": "always()  # runs even when tests fail so the report is always published",
        "key_steps": [
            "actions/download-artifact@v4 ← allure-results/",
            "Checkout gh-pages branch → restore allure-history/ for trend charts",
            "actions/setup-node@v4  (Node 20)",
            "npm ci  (installs allure CLI from package.json)",
            "npx allure generate allure-results  → allure-report/",
            "Copy allure-history/ into allure-report/ for next run's trends",
            "Copy architecture.html into allure-report/",
            "Post Pages URL + commit link to $GITHUB_STEP_SUMMARY",
            "peaceiris/actions-gh-pages@v4 → publish allure-report/ to gh-pages branch",
            "GitHub API PATCH /pages → enforce gh-pages/root as Pages source",
        ],
    },
}

# ── Allure 3 vs Allure 2 key differences ──────────────────────────────────────
ALLURE3_NOTES = [
    "CLI installed via npm (allure-commandline), not apt or brew — consistent across all CI runners",
    "Command: `npx allure generate allure-results` (no --clean flag needed; output dir is allure-report/)",
    "Trend charts require copying allure-history/ from the previous report into the results dir BEFORE generate",
    "allure-pytest writes results to allure-results/ by default (configure in pytest.ini: --alluredir)",
]

# ── Artifact vs Pages: when to use each ───────────────────────────────────────
ARTIFACT_VS_PAGES = {
    "allure-results artifact": (
        "Raw JSON/XML output from pytest-allure. "
        "Retained 7 days. Used by the report job to build the HTML. "
        "Also useful for re-generating the report locally: "
        "`npx allure generate allure-results && npx allure open`"
    ),
    "GitHub Pages (gh-pages branch)": (
        "Rendered HTML report — accessible at https://<owner>.github.io/<repo>. "
        "Persists across runs. Contains trend history. "
        "architecture.html is also served here alongside the report."
    ),
}

# ── pytest.ini allure configuration ──────────────────────────────────────────
PYTEST_INI_ALLURE = """\
[pytest]
addopts = --alluredir=allure-results
"""

# ── allure-results directory contents (after a test run) ─────────────────────
ALLURE_RESULTS_FILES = {
    "*-result.json":     "One file per test: status, steps, attachments, labels",
    "*-container.json":  "Fixture setup/teardown for a group of tests",
    "categories.json":   "Custom failure categories (optional, place in allure-results/ before generate)",
    "environment.properties": "Key-value pairs shown on the report Overview tab",
}

# ── categories.json example — classify failures by type ──────────────────────
CATEGORIES_JSON_EXAMPLE = [
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
]

# ── environment.properties example ───────────────────────────────────────────
ENVIRONMENT_PROPERTIES_EXAMPLE = """\
Browser=Chromium
Base.URL=https://tutorialsninja.com/demo
Python.Version=3.12
Allure.Version=3.x
CI=GitHub Actions
"""


def print_pipeline_overview() -> None:
    print("=== Session 17: Allure 3 + GitHub Pages Pipeline ===\n")
    print("One-time setup:")
    for i, step in enumerate(SETUP_STEPS, 1):
        print(f"  {i}. {step}")
    print()
    for job, info in JOBS.items():
        print(f"Job: {job}  — {info['purpose']}")
        for step in info["key_steps"]:
            print(f"    • {step}")
        print()
    print("Allure 3 notes:")
    for note in ALLURE3_NOTES:
        print(f"  • {note}")


if __name__ == "__main__":
    print_pipeline_overview()
