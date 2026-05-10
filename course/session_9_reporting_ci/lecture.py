"""
Session 9 — Allure 3 + GitHub Pages
Key concepts: report anatomy, categories, environment, trend history, CI pipeline.
"""

# ── What Allure 3 shows ───────────────────────────────────────────────────────
REPORT_TABS = {
    "Overview":    "Pass/fail counts, trend chart, environment properties, categories.",
    "Suites":      "Test results grouped by class → story → test.",
    "Graphs":      "Status distribution, severity breakdown, duration over time.",
    "Timeline":    "Which tests ran in parallel and for how long.",
    "Categories":  "Failures grouped by cause (regex on message field).",
    "Packages":    "Results grouped by Python module path.",
}

# ── Allure decorator cheat-sheet ──────────────────────────────────────────────
DECORATORS = {
    "@allure.feature('Cart')":                "Top-level grouping (maps to Epic).",
    "@allure.story('Add to cart')":           "Sub-feature grouping.",
    "@allure.title('Badge updates to 1')":    "Human-readable test name in the report.",
    "@allure.severity(BLOCKER|CRITICAL|…)":   "Shown as coloured badge; filterable.",
    "with allure.step('Click Add to cart'):": "Collapsible step inside a test case.",
    "allure.attach(data, name, type)":        "Attach PNG / JSON / HTML to the report.",
}

# ── categories.json — how failures are grouped on the Categories tab ──────────
CATEGORIES_EXPLAINED = [
    "Each category has: name, messageRegex, matchedStatuses.",
    "Categories are matched top-down — first match wins.",
    "Write categories.json into allure-results/ BEFORE npx allure generate.",
    "conftest.py calls write_categories() in pytest_configure() so it's always present.",
]

# ── environment.properties — shown on the Overview tab ────────────────────────
ENVIRONMENT_KEYS = ["Browser", "Python", "Allure", "CI", "Branch", "Run"]

# ── Trend history: how to keep it across runs ─────────────────────────────────
TREND_SETUP = [
    "1. Generate report → allure-report/ contains allure-history/",
    "2. Before next generate, copy allure-history/ into allure-results/",
    "3. CI does this by checking out the gh-pages branch between jobs.",
    "4. Trend charts then show the last N builds automatically.",
]

# ── Allure 3 CLI commands ─────────────────────────────────────────────────────
CLI_COMMANDS = {
    "npm ci":                              "Install allure CLI from package.json.",
    "npx allure generate allure-results":  "Generate HTML report into allure-report/.",
    "npx allure open":                     "Open the report in a browser (local).",
    "npx allure --version":                "Check installed version.",
}

# ── Evolution summary ─────────────────────────────────────────────────────────
FRAMEWORK_EVOLUTION = {
    "Session 3": "conftest.py + raw Playwright tests (no POM)",
    "Session 4": "+ pages/ (BasePage, LoginPage, InventoryPage, CartPage, CheckoutPage)",
    "Session 5": "+ tools/ (CLI generator, self-healing, heal-report) + screenshot_on_failure",
    "Session 6": "+ agents/ (browser explorer) + browser_agent fixture",
    "Session 7": "+ analysis/ (failures, flaky) + CI markers + failure_record fixture",
    "Session 8": "+ allure_screenshot fixture (Allure attachment on failure)",
    "Session 9": "+ reporting/ (categories, environment) + pytest_configure hook",
}

if __name__ == "__main__":
    print("Report tabs:")
    for tab, desc in REPORT_TABS.items():
        print(f"  {tab:<14} {desc}")
    print("\nAllure decorators:")
    for dec, desc in DECORATORS.items():
        print(f"  {dec}")
        print(f"    → {desc}")
    print("\nFramework evolution:")
    for session, what in FRAMEWORK_EVOLUTION.items():
        print(f"  {session}: {what}")
