"""
Session 19 — Capstone Project: Production-Level Framework
Reference architecture summary and self-evaluation rubric.
"""

ARCHITECTURE_LAYERS = {
    "Tests": "Describe business behavior — no Playwright calls inline.",
    "Pages": "Encapsulate UI structure; one class per page or major component.",
    "API clients": "Typed wrappers around backend endpoints.",
    "AI utilities": "qa-gen CLI, self-healing wrapper, exploration agent.",
    "Fixtures & data": "pytest fixtures, faker factories, test data.",
}

DECISIONS = [
    "Sync Playwright API for readability (ADR-001).",
    "POM with Fluent API to keep tests linear (ADR-002).",
    "Self-healing logged but never silent — flakiness must surface (ADR-003).",
]

SELF_EVALUATION_RUBRIC = {
    "Code quality (30%)": {
        "excellent": "ruff + mypy --strict pass; small focused modules; no dead code",
        "acceptable": "Linting passes; some module bloat",
    },
    "Coverage (25%)": {
        "excellent": "50+ tests, all green 5 runs in a row, smoke + regression split",
        "acceptable": "30+ tests, occasional flakiness",
    },
    "AI integration (20%)": {
        "excellent": "CLI used to generate ≥10 real tests; self-heal logged & reviewed",
        "acceptable": "CLI present but rarely used",
    },
    "CI/CD (15%)": {
        "excellent": "Matrix shards + AI summary + flaky detector all wired",
        "acceptable": "Single-job CI without sharding",
    },
    "Docs (10%)": {
        "excellent": "README + ARCHITECTURE + 3 ADRs + diagrams",
        "acceptable": "README only",
    },
}

ADR_004 = {
    "id": "ADR-004",
    "title": "Use Allure for test reporting",
    "status": "Accepted",
    "context": (
        "pytest's built-in output is unreadable for non-engineers. "
        "Stakeholders need pass/fail trends, screenshots on failure, and step-level detail."
    ),
    "decision": (
        "All tests use @allure.feature / @allure.story / @allure.title. "
        "CI uploads allure-results as artifacts and publishes the HTML report to GitHub Pages."
    ),
    "consequences": (
        "+ Non-engineers can read test results in a browser.\n"
        "+ Screenshots attached automatically on failure.\n"
        "- allure-pytest adds ~0.3 s per test for attachment hooks."
    ),
}

ADR_005 = {
    "id": "ADR-005",
    "title": "Isolate each test with a fresh browser context",
    "status": "Accepted",
    "context": (
        "Shared browser state (cookies, localStorage) between tests causes order-dependent failures "
        "that are hard to reproduce locally."
    ),
    "decision": (
        "The `context` fixture has request scope; each test gets a new browser context "
        "and page. The browser itself is session-scoped to avoid the 3-second launch overhead per test."
    ),
    "consequences": (
        "+ Tests are fully isolated by default.\n"
        "+ Parallel execution with pytest-xdist is safe.\n"
        "- Slightly higher memory usage for long parallel runs."
    ),
}

KNOWN_ISSUES_AUDIT = [
    {
        "issue": "time.sleep(5) everywhere",
        "risk": "flakiness + slow runs",
        "fix": "Replace with Playwright's expect().to_be_visible() (auto-wait)",
    },
    {
        "issue": "Hardcoded URLs",
        "risk": "cannot run on staging/prod",
        "fix": "BASE_URL env var + config module",
    },
    {
        "issue": "XPath selectors in JSON",
        "risk": "fragile, not accessibility-driven",
        "fix": "Move to get_by_role / get_by_label per ARIA",
    },
    {
        "issue": "Global state in helpers",
        "risk": "tests depend on execution order",
        "fix": "pytest fixtures with proper scope; no global mutable state",
    },
    {
        "issue": "bash loop instead of pytest plugins",
        "risk": "no reports, no parallelism, no retries",
        "fix": "pytest-xdist for parallel, pytest-rerunfailures for flaky, Allure for reporting",
    },
]


CAPSTONE_CHECKLIST = [
    ("Framework structure",   "pages/, services/, flows/, tests/ all present"),
    ("BasePage pattern",      "All page classes extend BasePage; no raw selectors in tests"),
    ("Allure decorators",     "@allure.feature + @allure.story on every test class/method"),
    ("Screenshot on failure", "conftest hook attaches screenshot to Allure on failure"),
    ("Data isolation",        "Unique emails via {ts} placeholder; no shared state between tests"),
    ("CI pipeline",           "GitHub Actions: test → allure-generate → upload-artifact → gh-pages"),
    ("Flaky detector",        "flaky_detector.py wired to CI; issue opened when rate < 95%"),
    ("AI integration",        "qa-gen CLI used; self-heal logging enabled; at least 10 AI-gen tests"),
    ("Pre-commit hooks",      "ruff + ruff-format + mypy --strict passing on all files"),
    ("ADRs",                  "At least 5 ADRs in docs/adrs/ covering key design decisions"),
]


def print_architecture():
    print("=== Framework Architecture ===\n")
    print("Layers:")
    for layer, desc in ARCHITECTURE_LAYERS.items():
        print(f"  {layer}: {desc}")
    print("\nDecisions:")
    for d in DECISIONS:
        print(f"  - {d}")


def print_rubric():
    print("\n=== Self-Evaluation Rubric ===\n")
    for criterion, levels in SELF_EVALUATION_RUBRIC.items():
        print(f"{criterion}")
        print(f"  Excellent: {levels['excellent']}")
        print(f"  Acceptable: {levels['acceptable']}")


def print_checklist():
    print("\n=== Capstone Checklist ===\n")
    for item, description in CAPSTONE_CHECKLIST:
        print(f"  [ ] {item}: {description}")


def print_adrs():
    print("\n=== Architecture Decision Records ===\n")
    for adr in (ADR_004, ADR_005):
        print(f"{adr['id']}: {adr['title']}  [{adr['status']}]")
        print(f"  Decision: {adr['decision'][:120]}...")
        print()


if __name__ == "__main__":
    print_architecture()
    print_rubric()
    print_checklist()
    print_adrs()
